#!/usr/bin/env python3
"""Validate every section file in the content pack against its JSON Schema,
then run cross-file consistency checks (slug uniqueness and slug references).

Exits 0 if everything is valid, 1 otherwise. Prints a per-file OK line and,
on failure, every schema error found (not just the first).
"""

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent

# (data file, schema file, top-level key holding the slug-keyed list(s))
SECTIONS = [
    ("identity.yaml", "schema/identity.schema.json", None),
    ("work.yaml", "schema/work.schema.json", ["work"]),
    ("projects.yaml", "schema/projects.schema.json", ["projects", "awards", "programs"]),
    ("links.yaml", "schema/links.schema.json", ["links"]),
    ("hobbies.yaml", "schema/hobbies.schema.json", ["shows", "hobbies"]),
]


def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def load_schema(path):
    with open(path, "r") as f:
        return json.load(f)


def validate_schema(name, data, schema):
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    if errors:
        print(f"FAIL {name}: {len(errors)} schema error(s)")
        for err in errors:
            loc = "/".join(str(p) for p in err.path) or "<root>"
            print(f"  - {loc}: {err.message}")
        return False
    print(f"OK   {name}: schema valid")
    return True


def check_slug_uniqueness(name, items, label):
    slugs = [item.get("slug") for item in items if isinstance(item, dict)]
    seen = set()
    dupes = set()
    for slug in slugs:
        if slug in seen:
            dupes.add(slug)
        seen.add(slug)
    if dupes:
        print(f"FAIL {name}: duplicate slug(s) in {label}: {sorted(dupes)}")
        return False
    return True


def main():
    ok = True
    data_by_file = {}

    for filename, schema_path, _ in SECTIONS:
        data_path = ROOT / filename
        try:
            data = load_yaml(data_path)
        except Exception as e:
            print(f"FAIL {filename}: could not parse YAML: {e}")
            ok = False
            continue
        try:
            schema = load_schema(ROOT / schema_path)
        except Exception as e:
            print(f"FAIL {filename}: could not load schema {schema_path}: {e}")
            ok = False
            continue

        data_by_file[filename] = data
        if not validate_schema(filename, data, schema):
            ok = False

    # Extra check (a): slug uniqueness within every slug-keyed list.
    work = data_by_file.get("work.yaml", {}) or {}
    projects_file = data_by_file.get("projects.yaml", {}) or {}
    links = data_by_file.get("links.yaml", {}) or {}
    hobbies_file = data_by_file.get("hobbies.yaml", {}) or {}

    slug_lists = [
        ("work.yaml", work.get("work", []), "work"),
        ("projects.yaml", projects_file.get("projects", []), "projects"),
        ("projects.yaml", projects_file.get("awards", []), "awards"),
        ("projects.yaml", projects_file.get("programs", []), "programs"),
        ("links.yaml", links.get("links", []), "links"),
        ("hobbies.yaml", hobbies_file.get("shows", []), "shows"),
        ("hobbies.yaml", hobbies_file.get("hobbies", []), "hobbies"),
    ]
    for filename, items, label in slug_lists:
        if not check_slug_uniqueness(filename, items, label):
            ok = False

    # Extra check (b): every awards[].project matches an existing project slug.
    project_slugs = {p.get("slug") for p in projects_file.get("projects", []) if isinstance(p, dict)}
    for award in projects_file.get("awards", []):
        ref = award.get("project")
        if ref not in project_slugs:
            print(f"FAIL projects.yaml: awards[slug={award.get('slug')}].project = {ref!r} does not match any project slug")
            ok = False

    # Extra check (c): work.algora's `project` ref and hobbies meme-culture's
    # `related_project` ref resolve against project slugs.
    for entry in work.get("work", []):
        if "project" in entry:
            ref = entry.get("project")
            if ref not in project_slugs:
                print(f"FAIL work.yaml: work[slug={entry.get('slug')}].project = {ref!r} does not match any project slug")
                ok = False

    for hobby in hobbies_file.get("hobbies", []):
        if "related_project" in hobby:
            ref = hobby.get("related_project")
            if ref not in project_slugs:
                print(f"FAIL hobbies.yaml: hobbies[slug={hobby.get('slug')}].related_project = {ref!r} does not match any project slug")
                ok = False

    if ok:
        print("OK   all checks passed")
        return 0
    else:
        print("FAIL one or more checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
