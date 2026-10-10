"""
Consistency checks for the synthetic corpus. Reads files only, writes nothing.
Run from the repo root:  python scripts/check_corpus.py
Exit code 0 = all good, 1 = at least one problem found.
"""
import csv
import re
import sys
from pathlib import Path

import yaml

ROOT = Path("data")
MAX_CHARS = 1800  # a KPI/SOP file must stay small enough to be one chunk in variant V3
META = ["doc_id", "title", "doc_type", "domain", "owner", "certification", "version", "effective_date"]
problems = []


def bad(msg):
    problems.append(msg)


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def split_front_matter(text):
    # A markdown doc starts with --- YAML --- then the body
    _, header, body = text.split("---", 2)
    return yaml.safe_load(header), body


def section_bullets(body, heading):
    # Lines starting with "- " under "## heading", up to the next "## "
    m = re.search(rf"^## {heading}\n(.*?)(?=^## |\Z)", body, re.S | re.M)
    return [l[2:].strip() for l in m.group(1).splitlines() if l.startswith("- ")] if m else []


manifest = {r["doc_id"]: r for r in read_csv(ROOT / "corpus_manifest.csv")}
catalog = {r["name"]: r for r in read_csv(ROOT / "raw/catalog/data_catalog.csv")}
dashboards = {n for n, r in catalog.items() if r["asset_type"] == "dashboard"}
tables = {n for n, r in catalog.items() if r["asset_type"] == "table"}

# 1. Every manifest path exists, and every file under data/raw is in the manifest
paths = {r["source_path"] for r in manifest.values()}
for p in sorted(paths):
    if not Path(p).exists():
        bad(f"manifest path missing on disk: {p}")
for f in Path("data/raw").rglob("*.*"):
    if f.name != ".gitkeep" and f.as_posix() not in paths:
        bad(f"file not in manifest: {f.as_posix()}")

# 2. Markdown docs: YAML header equals the manifest row, and the file is small
for doc_id, row in manifest.items():
    p = Path(row["source_path"])
    if p.suffix != ".md" or not p.exists():
        continue
    text = p.read_text(encoding="utf-8")
    if len(text) > MAX_CHARS:
        bad(f"{doc_id}: {len(text)} chars, over {MAX_CHARS}")
    header, body = split_front_matter(text)
    for key in META:
        if str(header.get(key)) != row[key]:
            bad(f"{doc_id}: '{key}' is '{header.get(key)}' in the file but '{row[key]}' in the manifest")

    # 3. KPI files only: the dashboards and tables they name must exist in the catalog
    if row["doc_type"] != "kpi":
        continue
    for d in section_bullets(body, "Dashboards"):
        if d.startswith("None"):
            continue
        if d not in dashboards:
            bad(f"{doc_id}: dashboard '{d}' is not in the catalog")
        elif doc_id not in catalog[d]["linked_kpis"].split(";"):
            bad(f"{doc_id}: names '{d}' but the catalog does not link it back")
    for t in section_bullets(body, "Source tables"):
        name = re.match(r"`([^`]+)`", t)
        if name and name.group(1) not in tables:
            bad(f"{doc_id}: source table '{name.group(1)}' is not in the catalog")

# 4. Catalog rows: same owner, domain and status as their manifest row; linked KPIs exist
by_title = {r["title"]: r for r in manifest.values() if r["doc_type"] == "catalog"}
for name, c in catalog.items():
    m = by_title.get(name)
    if not m:
        bad(f"catalog asset '{name}' has no manifest row")
        continue
    for ckey, mkey in [("owner", "owner"), ("domain", "domain"), ("certification", "certification")]:
        if c[ckey] != m[mkey]:
            bad(f"{name}: {ckey} is '{c[ckey]}' in the catalog but '{m[mkey]}' in the manifest")
    for k in c["linked_kpis"].split(";"):
        if k not in manifest:
            bad(f"{name}: linked KPI {k} does not exist")

print(f"Checked {len(manifest)} manifest rows, {len(catalog)} catalog assets.")
if problems:
    print(f"{len(problems)} problem(s):")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("All checks passed.")
