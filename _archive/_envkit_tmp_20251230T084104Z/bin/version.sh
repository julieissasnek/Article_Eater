#!/usr/bin/env bash
# EnvKit v0.2 — Version Management
# Usage: ./bin/version.sh [check|bump|minor|set X.Y.Z]

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION_FILE="$ROOT/VERSION.txt"

current() {
    if [[ -f "$VERSION_FILE" ]]; then
        tr -d ' \r\n\t' < "$VERSION_FILE"
    else
        echo "0.0.0"
    fi
}

bump_patch() {
    local v="$(current)"
    local major=$(echo "$v" | cut -d. -f1)
    local minor=$(echo "$v" | cut -d. -f2)
    local patch=$(echo "$v" | cut -d. -f3)
    echo "$major.$minor.$((patch + 1))"
}

bump_minor() {
    local v="$(current)"
    local major=$(echo "$v" | cut -d. -f1)
    local minor=$(echo "$v" | cut -d. -f2)
    echo "$major.$((minor + 1)).0"
}

propagate_version() {
    local new_ver="$1"
    
    # Propagate to common locations (customize per project)
    # Example: update __version__ in Python files
    while IFS= read -r -d '' f; do
        if grep -q '__version__' "$f" 2>/dev/null; then
            sed -i.bak "s/__version__ = \"[^\"]*\"/__version__ = \"$new_ver\"/" "$f" 2>/dev/null || true
            rm -f "$f.bak"
        fi
    done < <(find "$ROOT" -maxdepth 3 -name "*.py" -type f -print0 2>/dev/null)
    
    # Update package.json if exists
    if [[ -f "$ROOT/package.json" ]]; then
        sed -i.bak "s/\"version\": \"[^\"]*\"/\"version\": \"$new_ver\"/" "$ROOT/package.json" 2>/dev/null || true
        rm -f "$ROOT/package.json.bak"
    fi
}

case "${1:-check}" in
    check|--check|-c)
        echo "$(current)"
        ;;
    bump|--bump|-b)
        old="$(current)"
        new="$(bump_patch)"
        echo "$new" > "$VERSION_FILE"
        propagate_version "$new"
        echo "Version: $old → $new"
        ;;
    minor|--minor|-m)
        old="$(current)"
        new="$(bump_minor)"
        echo "$new" > "$VERSION_FILE"
        propagate_version "$new"
        echo "Version: $old → $new (minor)"
        ;;
    set|--set|-s)
        if [[ -z "${2:-}" ]]; then
            echo "Usage: $0 set X.Y.Z"
            exit 1
        fi
        old="$(current)"
        echo "$2" > "$VERSION_FILE"
        propagate_version "$2"
        echo "Version: $old → $2"
        ;;
    *)
        echo "EnvKit v0.2 — Version Management"
        echo ""
        echo "Usage: $0 [check|bump|minor|set X.Y.Z]"
        echo ""
        echo "Commands:"
        echo "  check   Show current version (default)"
        echo "  bump    Increment patch version (1.2.3 → 1.2.4)"
        echo "  minor   Increment minor version (1.2.3 → 1.3.0)"
        echo "  set     Set specific version"
        echo ""
        echo "Current: $(current)"
        exit 1
        ;;
esac
