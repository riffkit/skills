#!/usr/bin/env python3
"""Render need-named skill variants from the canonical Riffkit skill.

One source of truth, fetched not stored: https://riffkit.ai/SKILL.md. Each entry
in `variants.json` becomes `<name>/SKILL.md` — the canonical body verbatim, under
a frontmatter whose name/description come from the variant and whose
version/updated_at/source_url/homepage are inherited from the canonical file.

The canonical body points to reference files in a `references/` folder next to
it. https://riffkit.ai/SKILL.json lists them, so each variant also gets
`<name>/references/<ref>.md`, one per entry there and nothing else (a reference
dropped from SKILL.json disappears from every variant on the next run).

This repo deliberately has NO SKILL.md at its root: the skills CLI stops at a
root SKILL.md and never scans subdirectories, so a root copy would hide every
variant from default discovery. The canonical skill lives in riffkit/skill.

Never edit a generated `<name>/` file: edit `variants.json` (naming) or the
canonical skill itself (body and references, served by the Riffkit app).

Stdlib only — this runs on a bare `actions/checkout` + ubuntu python3.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urljoin

REPO = Path(__file__).resolve().parent.parent
VARIANTS = REPO / "variants.json"

SOURCE_URL = "https://riffkit.ai/SKILL.md"
HEARTBEAT_URL = "https://riffkit.ai/HEARTBEAT.md"
MANIFEST_URL = "https://riffkit.ai/SKILL.json"
FETCH_TIMEOUT = 60

# Where the canonical body's "Reference files" index expects them.
REFERENCES_DIR = "references"
REFERENCE_NAME = re.compile(r"[a-z0-9][a-z0-9_-]*")

GENERATED_BANNER = (
    f"<!-- GENERATED from {SOURCE_URL} by scripts/render_variants.py "
    "— edit variants.json or the canonical SKILL.md, never this file -->"
)

# Frontmatter keys carried over from the canonical skill, in emitted order.
INHERITED_KEYS = ("version", "updated_at", "source_url", "homepage")

# A variant is a distinct client, so its files identify it — attribution only.
# Two independent, idempotent rewrites, applied to SKILL.md and every reference
# file; each is a no-op in a file without its anchor (the canonical files are
# never edited for this).
#
# 1. Any literal client tag, should the canonical ever carry one.
CLIENT_MARKER = '"client": "riffkit"'
# 2. The one-click sign-in "a. Start" step (in references/api.md today): teach
#    it to post the client name.
DEVICE_ANCHOR = "POST /api/skill/device/authorize"
DEVICE_FROM = "(no body, no auth needed)"

# Directories that are ours to delete when a variant leaves variants.json.
GENERATED_MARKER = "generated_from:"


def fetch(url: str, workdir: Path) -> str:
    """Download `url` to a temp file and read it back.

    curl rather than urllib: the site's edge rejects the default
    `Python-urllib/x.y` User-Agent with a 403.
    """
    dest = workdir / Path(url).name
    result = subprocess.run(
        ["curl", "-fsSL", url, "-o", str(dest)],
        capture_output=True,
        text=True,
        timeout=FETCH_TIMEOUT,
    )
    if result.returncode != 0:
        raise SystemExit(f"{url}: curl failed ({result.returncode}) {result.stderr.strip()}")
    return dest.read_text(encoding="utf-8")


def fetch_references(workdir: Path) -> dict[str, str]:
    """Fetch every reference file SKILL.json lists, as {name: text}."""
    try:
        manifest = json.loads(fetch(MANIFEST_URL, workdir))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{MANIFEST_URL}: not JSON ({exc})")
    refs = manifest.get("references") if isinstance(manifest, dict) else None
    if not isinstance(refs, dict):
        raise SystemExit(f"{MANIFEST_URL}: expected a 'references' object")

    out: dict[str, str] = {}
    for name, path in refs.items():
        if not isinstance(name, str) or not REFERENCE_NAME.fullmatch(name):
            raise SystemExit(f"{MANIFEST_URL}: unusable reference name {name!r}")
        if not isinstance(path, str) or not path:
            raise SystemExit(f"{MANIFEST_URL}: reference {name!r} has no path")
        out[name] = fetch(urljoin(MANIFEST_URL, path), workdir)
    return out


def split_frontmatter(text: str) -> tuple[list[str], str]:
    """Return (frontmatter lines, body) for a `---`-delimited YAML header."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise SystemExit(f"{SOURCE_URL}: expected YAML frontmatter opening '---'")
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], "".join(lines[i + 1 :])
    raise SystemExit(f"{SOURCE_URL}: unterminated YAML frontmatter")


def parse_simple_keys(fm_lines: list[str]) -> dict[str, str]:
    """Pick out top-level `key: value` scalars. No pyyaml, by design.

    Only column-0 keys count, so indented continuation lines (the canonical
    description is a multi-line plain scalar) never masquerade as keys.
    """
    out: dict[str, str] = {}
    for line in fm_lines:
        if not line.strip() or line[:1].isspace() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep or not key or key != key.strip():
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        out[key.strip()] = value
    return out


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def tag_client(text: str, name: str) -> tuple[str, int]:
    """Make one of the variant's files identify it as the calling client.

    Returns the rewritten text and how many sign-in start steps it tagged.
    """
    text = text.replace(CLIENT_MARKER, f'"client": "{name}"')

    device_to = f'(JSON body {{"client": "{name}"}}, no auth needed)'
    lines = text.splitlines(keepends=True)
    hits = 0
    for i, line in enumerate(lines):
        if DEVICE_ANCHOR in line and DEVICE_FROM in line:
            lines[i] = line.replace(DEVICE_FROM, device_to)
            hits += 1
    return "".join(lines), hits


def render(variant: dict, canonical_meta: dict[str, str], body: str) -> str:
    name = variant["name"]
    fm = [f"name: {name}", f"description: {yaml_quote(variant['description'])}"]
    for key in INHERITED_KEYS:
        if key in canonical_meta:
            fm.append(f"{key}: {yaml_quote(canonical_meta[key])}")
    fm.append(f"generated_from: {yaml_quote(SOURCE_URL)}")

    return "---\n" + "\n".join(fm) + "\n---\n\n" + GENERATED_BANNER + "\n" + body


def write_references(out_dir: Path, refs: dict[str, str]) -> None:
    """Make `<variant>/references/` hold exactly the files in `refs`."""
    ref_dir = out_dir / REFERENCES_DIR
    if ref_dir.exists():
        shutil.rmtree(ref_dir)
    if not refs:
        return
    ref_dir.mkdir()
    for ref_name, text in refs.items():
        (ref_dir / f"{ref_name}.md").write_text(text, encoding="utf-8")


def prune_stale(keep: set[str]) -> list[str]:
    """Drop variant dirs we generated that are no longer in variants.json."""
    removed = []
    for child in sorted(REPO.iterdir()):
        if not child.is_dir() or child.name.startswith(".") or child.name in keep:
            continue
        skill = child / "SKILL.md"
        if not skill.is_file():
            continue
        head = skill.read_text(encoding="utf-8")[:2048]
        if GENERATED_MARKER in head:
            shutil.rmtree(child)
            removed.append(child.name)
    return removed


def main() -> int:
    variants = json.loads(VARIANTS.read_text(encoding="utf-8"))

    # Fetch everything before writing anything, so a failed fetch leaves the
    # tree as it was.
    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        canonical = fetch(SOURCE_URL, workdir)
        heartbeat = fetch(HEARTBEAT_URL, workdir)
        references = fetch_references(workdir)

    fm_lines, body = split_frontmatter(canonical)
    meta = parse_simple_keys(fm_lines)
    body = body.lstrip("\n")

    names = set()
    for variant in variants:
        name = variant["name"]
        if name in names:
            raise SystemExit(f"variants.json: duplicate name {name!r}")
        if "/" in name or name.startswith("."):
            raise SystemExit(f"variants.json: unusable name {name!r}")
        names.add(name)

        variant_body, hits = tag_client(body, name)
        variant_refs = {}
        for ref_name, text in references.items():
            variant_refs[ref_name], ref_hits = tag_client(text, name)
            hits += ref_hits
        if not hits:
            print(
                f"WARN {name}: device-authorize anchor not found in SKILL.md or any "
                f"reference file ({DEVICE_ANCHOR!r} + {DEVICE_FROM!r}) — left as-is"
            )

        out_dir = REPO / name
        out_dir.mkdir(exist_ok=True)
        (out_dir / "SKILL.md").write_text(render(variant, meta, variant_body), encoding="utf-8")
        (out_dir / "HEARTBEAT.md").write_text(heartbeat, encoding="utf-8")
        write_references(out_dir, variant_refs)
        print(f"rendered {name}/SKILL.md + {len(variant_refs)} reference files")

    if (REPO / "SKILL.md").exists():
        # A root SKILL.md would make the skills CLI stop here and never see the
        # variants — the whole reason this repo is separate from riffkit/skill.
        raise SystemExit("refusing to leave a SKILL.md at the repo root")

    for name in prune_stale(names):
        print(f"removed stale variant {name}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
