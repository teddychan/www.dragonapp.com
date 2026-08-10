#!/usr/bin/env python3
"""Fetch GitHub Releases per app -> i18n/changelogs/<slug>.json.

Run manually or in release CI. Keeps the site build hermetic (no network at
build time). Falls back gracefully when a release has no body. Uses only the
Python stdlib; honors GITHUB_TOKEN if present (higher rate limit).

Usage:  python3 scripts/fetch-changelogs.py
"""
import json
import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(ROOT, "i18n", "apps")
OUT = os.path.join(ROOT, "i18n", "changelogs")
MAX_ENTRIES = 8


def repo_path(repo_url):
    # https://github.com/teddychan/ice-2 -> teddychan/ice-2
    return repo_url.rstrip("/").split("github.com/")[1]


WHATS_CHANGED_RE = re.compile(r"(?im)^\s*#{1,6}\s*what'?s\s+changed\s*$")

# The one public release tag shape. Anchored at both ends so a prefixed family (sample-v*,
# mas-v*, app-v*) or a prerelease suffix (v2.5.1-beta1) can never be rendered as a version.
PUBLIC_TAG_RE = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+$")


def _note_lines(text):
    lines = []
    for raw in text.split("\n"):
        l = raw.strip().strip("# ").strip()              # drop markdown headings
        if not l or l.lower() in ("what's changed", "whats changed", "changes"):
            continue                                      # drop the auto-generated header
        l = re.sub(r"\s*\bby @[\w-]+\s+in\s+https?://\S+", "", l)  # drop "by @user in <PR url>"
        l = re.sub(r"\s*https?://\S+", "", l)             # drop any remaining bare URLs
        l = l.lstrip("*-• ").strip()                      # drop bullet markers
        l = l.replace("**", "").replace("__", "")         # drop markdown bold markers
        if l:
            lines.append(l)
    return lines


def clean_notes(body):
    if not body:
        return ""
    text = body.replace("\r\n", "\n")
    text = re.sub(r"\*\*Full Changelog\*\*.*", "", text, flags=re.S).strip()
    # Everything under GitHub's "What's Changed" heading is an auto-generated
    # list of PR titles ("docs: unify README structure…"), which reads badly on
    # a marketing page. Prefer the hand-written prose above it. Releases that
    # never got a written summary have nothing above the heading, so fall back
    # to the list rather than rendering an empty row.
    prose = _note_lines(WHATS_CHANGED_RE.split(text)[0])
    lines = prose or _note_lines(text)
    return " · ".join(lines[:4])


def fetch(repo):
    api = "https://api.github.com/repos/%s/releases?per_page=%d" % (repo, MAX_ENTRIES)
    req = urllib.request.Request(api, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "dragonapp-changelog"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=20) as r:
        releases = json.load(r)
    out = []
    for rel in releases:
        # Drafts were already skipped; prereleases were not. Neither filter is fixing something
        # visible today — _index.json tracks only the four shipping apps, and clipmenu-2's
        # mas-v* tags carry no GitHub Release. Both are guards that become load-bearing as soon
        # as Dragon Sample App gets its own repo and page: dragon-kit demotes every sample
        # release to Pre-release (sample-v1.4.0, sample-v1.3.1 today) so its own tags keep the
        # "Latest" badge, and that habit follows the app.
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
        out.append({
            "version": tag[1:],
            "date": (rel.get("published_at") or "")[:10],
            "notes": clean_notes(rel.get("body")),
            "url": rel.get("html_url", ""),
        })
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    idx = json.load(open(os.path.join(APPS, "_index.json")))
    for slug in idx:
        data = json.load(open(os.path.join(APPS, slug + ".json")))
        repo = repo_path(data["repo"])
        try:
            entries = fetch(repo)
        except Exception as e:  # noqa: BLE001 — log and keep prior file
            print("  [warn] %s: %s (keeping existing changelog)" % (slug, e))
            continue
        with open(os.path.join(OUT, slug + ".json"), "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
        print("  %s: %d releases" % (slug, len(entries)))


if __name__ == "__main__":
    main()
