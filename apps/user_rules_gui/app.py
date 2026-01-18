from flask import Flask, render_template, request, redirect, url_for, flash, session
from sqlalchemy import create_engine, text
import os, datetime, json
from pathlib import Path
from functools import wraps

app = Flask(__name__)
app.secret_key = "user_rules_secret"

engine = create_engine("sqlite:///user_rules.db", future=True)

with engine.begin() as con:
    con.execute(text("""CREATE TABLE IF NOT EXISTS rules(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        antecedent TEXT NOT NULL,
        consequent TEXT NOT NULL,
        weight REAL DEFAULT 1.0,
        source TEXT,
        created_at TEXT NOT NULL
    )"""))

# Optional admin password. If unset/empty, everyone is effectively an admin (dev / lab mode).
RULES_ADMIN_PASSWORD = os.environ.get("AE_RULES_ADMIN_PASSWORD")


@app.context_processor
def inject_admin_flags():
    """Expose admin-related flags to templates.

    - is_admin: whether the current session is treated as admin.
    - rules_admin_protected: True if AE_RULES_ADMIN_PASSWORD is set.
    """
    protected = bool(RULES_ADMIN_PASSWORD)
    is_admin = (not protected) or bool(session.get("is_admin"))
    return {
        "is_admin": is_admin,
        "rules_admin_protected": protected,
    }


def admin_only(fn):
    """Decorator for routes that modify rules.

    If AE_RULES_ADMIN_PASSWORD is unset, this is a no-op.
    If it is set, only sessions that have logged in via /login
    (session["is_admin"] == True) may access the route.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if RULES_ADMIN_PASSWORD:
            if not session.get("is_admin"):
                flash("Admin login required to modify rules.")
                return redirect(url_for("login", next=request.path))
        return fn(*args, **kwargs)
    return wrapper


@app.route("/login", methods=["GET", "POST"])
def login():
    if not RULES_ADMIN_PASSWORD:
        flash("No AE_RULES_ADMIN_PASSWORD configured; all users are admins.")
        return redirect(url_for("index"))
    if request.method == "POST":
        pwd = request.form.get("password", "").strip()
        if pwd == RULES_ADMIN_PASSWORD:
            session["is_admin"] = True
            flash("Logged in as admin.")
            next_url = request.args.get("next") or url_for("index")
            return redirect(next_url)
        else:
            flash("Incorrect admin password.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("is_admin", None)
    flash("Logged out.")
    return redirect(url_for("index"))


@app.route("/")
def index():
    with engine.begin() as con:
        rows = con.execute(text("SELECT * FROM rules ORDER BY id DESC")).mappings().all()
    return render_template("index.html", rows=rows)


@app.route("/new", methods=["GET", "POST"])
@admin_only
def new_rule():
    if request.method == "POST":
        name = request.form["name"].strip()
        ant = request.form["antecedent"].strip()
        conq = request.form["consequent"].strip()
        w = float(request.form.get("weight", "1.0") or "1.0")
        src = request.form.get("source", "").strip()
        with engine.begin() as con:
            con.execute(
                text(
                    "INSERT INTO rules(name,antecedent,consequent,weight,source,created_at) "
                    "VALUES(:n,:a,:c,:w,:s,:t)"
                ),
                {
                    "n": name,
                    "a": ant,
                    "c": conq,
                    "w": w,
                    "s": src,
                    "t": datetime.datetime.utcnow().isoformat() + "Z",
                },
            )
        flash("Rule created.")
        return redirect(url_for("index"))
    return render_template("edit.html", row=None)


@app.route("/edit/<int:rid>", methods=["GET", "POST"])
@admin_only
def edit_rule(rid):
    if request.method == "POST":
        name = request.form["name"].strip()
        ant = request.form["antecedent"].strip()
        conq = request.form["consequent"].strip()
        w = float(request.form.get("weight", "1.0") or "1.0")
        src = request.form.get("source", "").strip()
        with engine.begin() as con:
            con.execute(
                text(
                    "UPDATE rules SET name=:n, antecedent=:a, consequent=:c, weight=:w, "
                    "source=:s WHERE id=:id"
                ),
                {"n": name, "a": ant, "c": conq, "w": w, "s": src, "id": rid},
            )
        flash("Rule updated.")
        return redirect(url_for("index"))
    with engine.begin() as con:
        row = con.execute(
            text("SELECT * FROM rules WHERE id=:id"), {"id": rid}
        ).mappings().first()
    return render_template("edit.html", row=row)


@app.route("/delete/<int:rid>", methods=["POST"])
@admin_only
def delete_rule(rid):
    with engine.begin() as con:
        con.execute(text("DELETE FROM rules WHERE id=:id"), {"id": rid})
    flash("Rule deleted.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    ports_path = Path(__file__).resolve().parents[1] / "contracts" / "ports.json"
    port = 5051
    if ports_path.exists():
        try:
            data = json.loads(ports_path.read_text(encoding="utf-8"))
            port = int(data.get("ports", {}).get("rulegraph_ui", {}).get("host", port))
        except Exception:
            port = 5051
    app.run(port=port, debug=True)
