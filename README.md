# Parashar Patterns — Blind 75 Revision Site

A static site for Blind 75 interview revision: one page per problem (pattern,
walkthrough, embedded video) plus a printable one-pager PDF for the morning
of the interview.

Live at: `https://pawanparashar.github.io/dsa-interview-prep/`
(enable in **Settings → Pages → Deploy from branch → main / root**)

## Structure

```
data/problems.json        ← single source of truth, one entry per problem
templates/                ← Jinja2 templates
  index.html.j2             home page (table of all 75)
  problem.html.j2           "Learn & Revise" detail page
  onepager.html.j2          print-ready one-pager (rendered to PDF)
scripts/build.py          ← generator: reads data/problems.json, writes the
                              site below
assets/css/site.css       ← shared site styling

index.html                 ← generated — do not hand-edit
problems/<slug>/index.html         ← generated
problems/<slug>/<slug>-onepager.pdf ← generated
```

## Adding a new problem

1. Append a new object to the `problems` array in `data/problems.json`
   (copy the Contains Duplicate entry as a template — same fields).
2. Run the build:
   ```bash
   pip install --break-system-packages jinja2 weasyprint   # one-time
   python3 scripts/build.py
   ```
3. Commit and push:
   ```bash
   git add -A
   git commit -m "Add problem N: <name>"
   git push
   ```

The homepage progress bar and "coming up" rows update automatically based on
how many entries are in `data/problems.json` (assumes 75 total).

## Enabling GitHub Pages (one-time)

1. Push this repo to GitHub.
2. Repo → **Settings → Pages**.
3. Source: **Deploy from a branch** → Branch: **main**, folder **/ (root)**.
4. Save. The site publishes at `https://pawanparashar.github.io/dsa-interview-prep/`
   within a minute or two.
