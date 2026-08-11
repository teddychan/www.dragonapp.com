#!/usr/bin/env python3
"""Fetch each app's release notes -> i18n/changelogs/<slug>.json.

The notes are the app's own What's New pane, in every language the app ships it
in. Each release carries them as a `whats-new.json` asset written by
teddychan/dragon-release-ci; this script only transports them. Nothing here
reads the GitHub Release *body* any more: those bodies are auto-generated from
PR titles, so the site rendered marketing copy like "docs: realign
RELEASING.md with the actual release workflow" — and rendered it in English on
all seven locales.

Releases published before the asset existed keep whatever entry the site
already has. There is no backfill by design, so a release with neither an asset
nor an existing entry simply gets no entry: a missing row beats a wrong one.

Run manually or in release CI. Keeps the site build hermetic (no network at
build time). Uses only the Python stdlib; honors GITHUB_TOKEN if present
(higher rate limit).

Usage:  python3 scripts/fetch-changelogs.py
"""
import json
import os
import re
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(ROOT, "i18n", "apps")
OUT = os.path.join(ROOT, "i18n", "changelogs")
MAX_ENTRIES = 8

# The release asset that carries the What's New pane, and the only schema of it
# this script understands. An unknown schema is treated as no asset at all —
# guessing at a future shape would put mangled text on four marketing pages,
# whereas keeping the previous entry is merely stale.
ASSET_NAME = "whats-new.json"
ASSET_SCHEMA = 1

# The language the site falls back to when an app does not ship a locale. ice-2
# localizes with Apple String Catalogs and ships English only, so its asset
# carries one language and all seven of its pages render it.
BASE_LANG = "en"

# The one public release tag shape. Anchored at both ends so a prefixed family (sample-v*,
# mas-v*, app-v*) or a prerelease suffix (v2.5.1-beta1) can never be rendered as a version.
PUBLIC_TAG_RE = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+$")


def repo_path(repo_url):
    # https://github.com/teddychan/ice-2 -> teddychan/ice-2
    return repo_url.rstrip("/").split("github.com/")[1]


def flatten_notes(block):
    """One language's What's New pane -> the single line a changelog row shows.

    Summary first, then every section's entries **in the order the app gave
    them** — that order is the app's render order, not alphabetical and not the
    enum order, so it is preserved rather than sorted. The section `kind`
    (Added / Fixed / …) is deliberately dropped: the row is one prose line, and
    the app's own pane is where those headers belong.
    """
    parts = []
    summary = (block.get("summary") or "").strip()
    if summary:
        parts.append(summary)
    for section in block.get("sections") or []:
        for entry in section.get("entries") or []:
            entry = (entry or "").strip()
            if entry:
                parts.append(entry)
    return " · ".join(parts)


def notes_by_language(doc):
    """`languages` -> {lang: line}, keyed by the asset's own language codes."""
    langs = doc.get("languages") or {}
    notes = {}
    for code in sorted(langs):
        line = flatten_notes(langs[code] or {})
        if line:
            notes[code] = line
    # The asset's contract: a language absent from `languages` renders
    # `default_language`. The site resolves a missing locale by falling back to
    # BASE_LANG, so materialize that key when the app itself does not ship it —
    # otherwise an app whose default is not English would render empty rows.
    default = doc.get("default_language") or BASE_LANG
    if BASE_LANG not in notes and default in notes:
        notes[BASE_LANG] = notes[default]
    return notes


def parse_whats_new(raw, version):
    """A downloaded `whats-new.json` -> {lang: line}, or None if unusable.

    None means "act as if the release had no asset", which keeps the entry the
    site already has. Every rejection here is a case where rendering the file
    would be worse than rendering nothing new.
    """
    try:
        doc = json.loads(raw)
    except (ValueError, TypeError):
        return None
    if not isinstance(doc, dict) or doc.get("schema") != ASSET_SCHEMA:
        return None
    # The tag is what the release gate asserts against CFBundleShortVersionString,
    # so it wins. A disagreement means CI attached a stale or foreign file, and
    # publishing one version's notes under another is the failure nobody would
    # spot on the site.
    stated = str(doc.get("version") or "")
    if stated.removeprefix("v") != version:
        return None
    return notes_by_language(doc) or None


def download_asset(asset):
    """Asset bytes, or None on any failure — which reads as "no asset"."""
    url = asset.get("browser_download_url")
    if not url:
        return None
    # No Authorization header: browser_download_url redirects to a
    # pre-authorized storage URL that rejects a second auth mechanism, and every
    # Dragon app repo is public.
    req = urllib.request.Request(url, headers={"User-Agent": "dragonapp-changelog"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read()
    except (urllib.error.URLError, OSError, ValueError) as e:
        print("  [warn] %s: %s (keeping the existing entry)" % (url, e))
        return None


def fetch_releases(repo):
    api = "https://api.github.com/repos/%s/releases?per_page=%d" % (repo, MAX_ENTRIES)
    req = urllib.request.Request(api, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "dragonapp-changelog"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def merge_entries(releases, existing, download):
    """Releases (newest first) + the file on disk -> the file to write.

    A release with a usable asset produces a fresh entry; one without keeps the
    entry the site already has, unchanged, and contributes nothing if it has
    none. That asymmetry is the safety property this file is built around: with
    no asset published anywhere yet, this returns exactly what it was given.
    """
    prior = {e.get("version"): e for e in existing}
    out = []
    seen = set()
    for rel in releases:
        # Drafts were already skipped; prereleases were not. Neither filter is fixing something
        # visible today — _index.json tracks only the four shipping apps, and clipmenu-2's
        # mas-v* tags carry no GitHub Release. Both are guards that become load-bearing as soon
        # as an app demotes its own releases to Pre-release so a newer tag keeps the "Latest"
        # badge, the way dragon-kit did for every sample release.
        if rel.get("draft") or rel.get("prerelease"):
            continue
        tag = rel.get("tag_name") or ""
        # Only exact public tags reach the changelog. The old `.lstrip("v")` was not a prefix
        # strip — it removes leading "v" characters, so "mas-v2.20.1" came through untouched and
        # would have rendered as the literal version string "mas-v2.20.1". Per
        # dragon-kit/docs/MAC-APP-RELEASE-LIFECYCLE.md a channel-specific build is not a separate
        # release: every channel consumes the same exact vX.Y.Z.
        if not PUBLIC_TAG_RE.match(tag):
            continue
        version = tag[1:]
        seen.add(version)
        asset = next((a for a in rel.get("assets") or []
                      if a.get("name") == ASSET_NAME), None)
        notes = parse_whats_new(download(asset), version) if asset else None
        if notes:
            out.append({
                "version": version,
                # The release date, not the asset's `date`: this row says when the
                # version shipped, and an app's What's New date is written by hand
                # days before the tag.
                "date": (rel.get("published_at") or "")[:10],
                "notes": notes,
                "url": rel.get("html_url", ""),
            })
        elif version in prior:
            out.append(prior[version])
    # Entries older than the API window. Dropping them would delete rows the site
    # has already published the moment a release ages out of the newest page.
    out += [e for e in existing if e.get("version") not in seen]
    return out[:MAX_ENTRIES]


def load_existing(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except ValueError:
        return []
    return data if isinstance(data, list) else []


def main():
    os.makedirs(OUT, exist_ok=True)
    idx = json.load(open(os.path.join(APPS, "_index.json")))
    for slug in idx:
        data = json.load(open(os.path.join(APPS, slug + ".json")))
        repo = repo_path(data["repo"])
        path = os.path.join(OUT, slug + ".json")
        existing = load_existing(path)
        try:
            releases = fetch_releases(repo)
        except Exception as e:  # noqa: BLE001 — log and keep prior file
            print("  [warn] %s: %s (keeping existing changelog)" % (slug, e))
            continue
        entries = merge_entries(releases, existing, download_asset)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
        had = {e.get("version") for e in existing}
        fresh = [e["version"] for e in entries if e.get("version") not in had]
        print("  %s: %d entries%s" % (slug, len(entries),
                                      (" (new: %s)" % ", ".join(fresh)) if fresh else ""))


if __name__ == "__main__":
    main()
