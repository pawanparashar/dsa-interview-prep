#!/usr/bin/env python3
"""
Build script for the Parashar Patterns (Blind 75 revision) static site.

Reads data/problems.json, renders:
  - index.html                                   (home page, all 75 rows)
  - problems/<slug>/index.html                   (learn & revise page)
  - problems/<slug>/<slug>-onepager.pdf           (printable one-pager)

Usage:
    pip install jinja2 weasyprint
    python3 scripts/build.py

Re-run this after editing data/problems.json to regenerate the whole site.
"""
import html
import json
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "problems.json"
TEMPLATES_DIR = ROOT / "templates"

PY_KEYWORDS = [
    "class", "def", "return", "if", "elif", "else", "for", "while", "in", "not",
    "and", "or", "is", "None", "True", "False", "self", "import", "from", "as",
    "with", "try", "except", "finally", "raise", "yield", "lambda", "pass",
    "break", "continue",
]
_KW_PATTERN = re.compile(r"\b(" + "|".join(re.escape(k) for k in PY_KEYWORDS) + r")\b")


def highlight_code(code: str) -> str:
    """Minimal keyword highlighter: escape HTML, then wrap Python keywords."""
    escaped = html.escape(code)
    return _KW_PATTERN.sub(r'<span class="kw">\1</span>', escaped)


def slugify(text: str) -> str:
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def main():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    site = data["site"]
    problems = data["problems"]
    roadmap = data.get("roadmap", [])
    solved_count = len(problems)

    for p in problems:
        p["code_html"] = highlight_code(p["code"])
        for alt in p.get("alternative_solutions", []):
            alt["code_html"] = highlight_code(alt["code"])
        if p.get("trace"):
            # html.escape so the JSON can sit safely inside a double-quoted
            # HTML attribute (escapes quotes/ampersands/angle brackets).
            p["trace_json"] = html.escape(json.dumps(p["trace"]), quote=True)

    # Merge the full 75-problem roadmap with whichever ones are solved
    # (present in `problems`), matched by slugified title. Unsolved entries
    # get their Problem/Difficulty from the roadmap and no links.
    solved_by_slug = {p["slug"]: p for p in problems}
    rows = []
    for i, entry in enumerate(roadmap, start=1):
        slug = slugify(entry["title"])
        p = solved_by_slug.get(slug)
        rows.append({
            "number": i,
            "title": p["title"] if p else entry["title"],
            "category": p["category"] if p else entry["category"],
            "difficulty": p["difficulty"] if p else entry["difficulty"],
            "slug": p["slug"] if p else slug,
            "solved": p is not None,
        })
    total_count = len(rows) or len(problems)

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=False)

    # --- home page ---
    index_tpl = env.get_template("index.html.j2")
    (ROOT / "index.html").write_text(
        index_tpl.render(
            site=site,
            rows=rows,
            solved_count=solved_count,
            total_count=total_count,
        ),
        encoding="utf-8",
    )
    print(f"wrote index.html ({solved_count}/{total_count} problems)")

    # --- per-problem pages + PDFs ---
    problem_tpl = env.get_template("problem.html.j2")
    onepager_tpl = env.get_template("onepager.html.j2")

    try:
        from weasyprint import HTML
        have_weasyprint = True
    except ImportError:
        have_weasyprint = False
        print("weasyprint not installed — skipping PDF generation (pip install weasyprint)")

    for p in problems:
        pdir = ROOT / "problems" / p["slug"]
        pdir.mkdir(parents=True, exist_ok=True)

        (pdir / "index.html").write_text(
            problem_tpl.render(site=site, p=p), encoding="utf-8"
        )

        onepager_html = onepager_tpl.render(site=site, p=p)
        onepager_html_path = pdir / f"{p['slug']}-onepager.html"
        onepager_html_path.write_text(onepager_html, encoding="utf-8")

        if have_weasyprint:
            pdf_path = pdir / f"{p['slug']}-onepager.pdf"
            HTML(string=onepager_html, base_url=str(pdir)).write_pdf(str(pdf_path))
            print(f"wrote problems/{p['slug']}/ (index.html + onepager.pdf)")
        else:
            print(f"wrote problems/{p['slug']}/index.html (PDF skipped)")

    # .nojekyll so GitHub Pages serves files as-is
    (ROOT / ".nojekyll").touch()


if __name__ == "__main__":
    main()
