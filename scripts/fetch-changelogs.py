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


def clean_notes(body):
    if not body:
        return ""
    text = body.replace("\r\n", "\n")
    text = re.sub(r"\*\*Full Changelog\*\*.*", "", text, flags=re.S).strip()
    lines = []
    for raw in text.split("\n"):
        l = raw.strip().strip("# ").strip()              # drop markdown headings
        if not l or l.lower() in ("what's changed", "whats changed", "changes"):
            continue                                      # drop the auto-generated header
        l = re.sub(r"\s*\bby @[\w-]+\s+in\s+https?://\S+", "", l)  # drop "by @user in <PR url>"
        l = re.sub(r"\s*https?://\S+", "", l)             # drop any remaining bare URLs
        l = l.lstrip("*-• ").strip()                      # drop bullet markers
        if l:
            lines.append(l)
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
        if rel.get("draft"):
            continue
        out.append({
            "version": (rel.get("tag_name") or "").lstrip("v"),
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
