from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine, text
import os, datetime
app = Flask(__name__); app.secret_key = "user_rules_secret"
engine = create_engine("sqlite:///user_rules.db", future=True)
with engine.begin() as con:
    con.execute(text('''CREATE TABLE IF NOT EXISTS rules(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, antecedent TEXT NOT NULL, consequent TEXT NOT NULL,
        weight REAL DEFAULT 1.0, source TEXT, created_at TEXT NOT NULL)'''))
@app.route("/")
def index():
    with engine.begin() as con:
        rows = con.execute(text("SELECT * FROM rules ORDER BY id DESC")).all()
    return render_template("index.html", rows=rows)
@app.route("/new", methods=["GET","POST"])
def new_rule():
    if request.method=="POST":
        name=request.form["name"].strip(); ant=request.form["antecedent"].strip(); conq=request.form["consequent"].strip()
        w=float(request.form.get("weight","1.0")); src=request.form.get("source","").strip()
        with engine.begin() as con:
            con.execute(text("INSERT INTO rules(name,antecedent,consequent,weight,source,created_at) VALUES(:n,:a,:c,:w,:s,:t)"),
                {"n":name,"a":ant,"c":conq,"w":w,"s":src,"t":datetime.datetime.utcnow().isoformat()+"Z"})
        flash("Rule created."); return redirect(url_for("index"))
    return render_template("edit.html", row=None)
@app.route("/edit/<int:rid>", methods=["GET","POST"])
def edit_rule(rid):
    if request.method=="POST":
        name=request.form["name"].strip(); ant=request.form["antecedent"].strip(); conq=request.form["consequent"].strip()
        w=float(request.form.get("weight","1.0")); src=request.form.get("source","").strip()
        with engine.begin() as con:
            con.execute(text("UPDATE rules SET name=:n, antecedent=:a, consequent=:c, weight=:w, source=:s WHERE id=:id"),
                {"n":name,"a":ant,"c":conq,"w":w,"s":src,"id":rid})
        flash("Rule updated."); return redirect(url_for("index"))
    with engine.begin() as con:
        row = con.execute(text("SELECT * FROM rules WHERE id=:id"), {"id":rid}).mappings().first()
    return render_template("edit.html", row=row)
@app.route("/delete/<int:rid>", methods=["POST"])
def delete_rule(rid):
    with engine.begin() as con:
        con.execute(text("DELETE FROM rules WHERE id=:id"), {"id":rid})
    flash("Rule deleted."); return redirect(url_for("index"))
if __name__ == "__main__":
    app.run(port=5051, debug=True)