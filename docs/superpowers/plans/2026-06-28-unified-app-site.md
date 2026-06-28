# Unified Dragon App Site — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate every Dragon App page (3 apps × 7 languages) plus a hub, an `/about/` page, localized privacy, legacy redirects, and an `/llms.txt` from one data-driven template system, optimized for SEO/GEO and a PageSpeed score of 100, with light + dark themes.

**Architecture:** Extend the existing Python static generator `i18n/build_i18n.py`. App pages render from one `app.html` template + per-app JSON facts (`i18n/apps/<slug>.json`) + per-language copy (`i18n/strings/<lang>.json`) + generated changelog JSON (`i18n/changelogs/<slug>.json`). The generator writes localized HTML into `docs/` and rewrites `sitemap.xml`. No runtime backend; GitHub Pages serves `docs/`.

**Tech Stack:** Python 3 (stdlib only: `json`, `re`, `urllib`), HTML, CSS (`docs/shared/dragon.css`), GitHub Pages, Sparkle appcasts, GitHub Releases API.

**Reference spec:** `docs/superpowers/specs/2026-06-28-unified-app-site-design.md`

**Conventions for every task:**
- Always run the build from repo root: `python3 i18n/build_i18n.py`.
- Never hand-edit files in `docs/` that the generator owns — edit `i18n/` sources.
- Commit identity must be `teddychan <teddychan@gmail.com>` (global hook enforces this).
- A "build is clean" check = the generator prints `Built N pages` and no `Unknown token` traceback.

---

## Phase 0 — Test harness for the generator

The generator currently has no tests. Add a tiny pytest harness so later tasks are verifiable.

### Task 0: Add generator smoke test

**Files:**
- Create: `i18n/tests/test_build.py`
- Create: `i18n/tests/__init__.py` (empty)

- [ ] **Step 1: Write the failing test**

```python
# i18n/tests/test_build.py
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_build():
    return subprocess.run(
        [sys.executable, "i18n/build_i18n.py"],
        cwd=ROOT, capture_output=True, text=True
    )

def test_build_runs_clean():
    r = run_build()
    assert r.returncode == 0, r.stderr
    assert "Built" in r.stdout
    assert "Traceback" not in r.stderr

def test_known_pages_exist():
    run_build()
    for rel in ["docs/index.html", "docs/zh-Hant/index.html", "docs/support.html"]:
        assert os.path.exists(os.path.join(ROOT, rel)), rel
```

- [ ] **Step 2: Run test to verify current state**

Run: `cd /Users/teddychan/git/www.dragonapp.com/.claude/worktrees/vibrant-hellman-25579b && python3 -m pytest i18n/tests/test_build.py -v`
Expected: PASS (the generator already builds today). If it fails, stop and fix the environment before continuing.

- [ ] **Step 3: Commit**

```bash
git add i18n/tests/
git commit -m "test: add smoke test for the i18n site generator"
```

---

## Phase 1 — App registry + per-app data files

### Task 1: Create the app registry and data files

**Files:**
- Create: `i18n/apps/_index.json`
- Create: `i18n/apps/ice-2.json`
- Create: `i18n/apps/clipmenu-2.json`
- Create: `i18n/apps/yahoo-keykey-2.json`
- Test: `i18n/tests/test_apps.py`

- [ ] **Step 1: Write the failing test**

```python
# i18n/tests/test_apps.py
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APPS = os.path.join(ROOT, "i18n", "apps")

REQUIRED = {"slug", "name", "theme", "repo", "homebrew_cask", "mas_url",
            "license", "license_url", "min_macos", "appcast_path",
            "credit_name", "credit_url", "sponsors_url"}

def test_index_lists_apps():
    idx = json.load(open(os.path.join(APPS, "_index.json")))
    assert idx == ["ice-2", "clipmenu-2", "yahoo-keykey-2"]

def test_each_app_has_required_fields():
    idx = json.load(open(os.path.join(APPS, "_index.json")))
    for slug in idx:
        data = json.load(open(os.path.join(APPS, slug + ".json")))
        assert REQUIRED <= set(data), "%s missing %s" % (slug, REQUIRED - set(data))
        assert data["slug"] == slug
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest i18n/tests/test_apps.py -v`
Expected: FAIL — `FileNotFoundError` for `_index.json`.

- [ ] **Step 3: Create `i18n/apps/_index.json`**

```json
["ice-2", "clipmenu-2", "yahoo-keykey-2"]
```

- [ ] **Step 4: Create `i18n/apps/ice-2.json`**

```json
{
  "slug": "ice-2",
  "name": "Ice 2",
  "theme": "theme-ice",
  "repo": "https://github.com/teddychan/ice-2",
  "homebrew_cask": "teddychan/tap/ice-2",
  "mas_url": null,
  "license": "GPLv3",
  "license_url": "https://github.com/teddychan/ice-2/blob/main/LICENSE",
  "min_macos": "26",
  "appcast_path": "ice-2/appcast.xml",
  "credit_name": "Jordan Baird",
  "credit_url": "https://github.com/jordanbaird/Ice",
  "sponsors_url": null
}
```

- [ ] **Step 5: Create `i18n/apps/clipmenu-2.json`**

```json
{
  "slug": "clipmenu-2",
  "name": "ClipMenu 2",
  "theme": "",
  "repo": "https://github.com/teddychan/clipmenu-2",
  "homebrew_cask": "teddychan/tap/clipmenu-2",
  "mas_url": null,
  "license": "MIT",
  "license_url": "https://github.com/teddychan/clipmenu-2/blob/main/LICENSE",
  "min_macos": "26",
  "appcast_path": "clipmenu-2/appcast.xml",
  "credit_name": "the original ClipMenu",
  "credit_url": "https://github.com/naotaka/ClipMenu",
  "sponsors_url": null
}
```

Note: `theme` is empty because ClipMenu uses the default studio blue. Confirm
`license` against the repo's actual LICENSE during execution; if it differs, set
the correct SPDX id and URL.

- [ ] **Step 6: Create `i18n/apps/yahoo-keykey-2.json`**

```json
{
  "slug": "yahoo-keykey-2",
  "name": "Yahoo KeyKey 2",
  "theme": "theme-keykey",
  "repo": "https://github.com/teddychan/yahoo-keykey-2",
  "homebrew_cask": "teddychan/tap/yahoo-keykey-2",
  "mas_url": null,
  "license": "GPLv3",
  "license_url": "https://github.com/teddychan/yahoo-keykey-2/blob/main/LICENSE",
  "min_macos": "26",
  "appcast_path": "yahoo-keykey-2/appcast.xml",
  "credit_name": "Yahoo! KeyKey",
  "credit_url": "https://github.com/teddychan/yahoo-keykey-2",
  "sponsors_url": null
}
```

Note: confirm the Homebrew cask name and LICENSE for KeyKey during execution;
if there is no cask yet, set `"homebrew_cask": null` (the template handles null
by hiding the Homebrew card — see Task 5 `render_download`).

- [ ] **Step 7: Run test to verify it passes**

Run: `python3 -m pytest i18n/tests/test_apps.py -v`
Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add i18n/apps/ i18n/tests/test_apps.py
git commit -m "feat: add app registry + per-app data files (ice-2, clipmenu-2, yahoo-keykey-2)"
```

---

## Phase 2 — Changelog fetcher + data

### Task 2: Changelog fetch script

**Files:**
- Create: `scripts/fetch-changelogs.py`
- Create: `i18n/changelogs/ice-2.json` (committed output)
- Create: `i18n/changelogs/clipmenu-2.json`
- Create: `i18n/changelogs/yahoo-keykey-2.json`
- Test: `i18n/tests/test_changelogs.py`

- [ ] **Step 1: Write the failing test (validates the committed JSON shape)**

```python
# i18n/tests/test_changelogs.py
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CL = os.path.join(ROOT, "i18n", "changelogs")

def test_changelog_files_exist_and_are_lists():
    for slug in ["ice-2", "clipmenu-2", "yahoo-keykey-2"]:
        data = json.load(open(os.path.join(CL, slug + ".json")))
        assert isinstance(data, list)
        for entry in data:
            assert {"version", "date", "notes", "url"} <= set(entry)
            assert len(entry["date"]) == 10 and entry["date"][4] == "-"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest i18n/tests/test_changelogs.py -v`
Expected: FAIL — files do not exist.

- [ ] **Step 3: Create `scripts/fetch-changelogs.py`**

```python
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
    lines = [l.strip("# ").strip() for l in text.split("\n") if l.strip()]
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
```

- [ ] **Step 4: Run the fetcher**

Run: `python3 scripts/fetch-changelogs.py`
Expected: prints `ice-2: N releases` etc. If GitHub rate-limits (no token), set `GITHUB_TOKEN` and re-run.

- [ ] **Step 5: If the fetcher could not reach GitHub, seed minimal valid files**

Only if Step 4 failed for a slug, create a valid placeholder so the build stays deterministic (replace later by re-running the fetcher). Example for `ice-2` (version 2.5.3, 2026-06-28 from its appcast):

```json
[
  {"version": "2.5.3", "date": "2026-06-28", "notes": "", "url": "https://github.com/teddychan/ice-2/releases/tag/v2.5.3"}
]
```

Create equivalent single-entry files for `clipmenu-2` (2.12.0, 2026-06-27) and `yahoo-keykey-2` (use its appcast's latest version/date).

- [ ] **Step 6: Run test to verify it passes**

Run: `python3 -m pytest i18n/tests/test_changelogs.py -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add scripts/fetch-changelogs.py i18n/changelogs/ i18n/tests/test_changelogs.py
git commit -m "feat: changelog fetcher + committed per-app changelog JSON"
```

---

## Phase 3 — The unified app template

### Task 3: Add per-app English copy to en-US.json

**Files:**
- Modify: `i18n/strings/en-US.json` (add a top-level block per app slug + shared app-page headings under `common`)

- [ ] **Step 1: Add shared app-page section headings under `common`**

Add these keys to the existing `common` object in `i18n/strings/en-US.json`:

```json
"app_demo_h2": "See it in action",
"app_changelog_h2": "What's new",
"app_changelog_sub": "Plain-language notes, newest first.",
"app_changelog_auto": "Auto-generated from GitHub Releases",
"app_changelog_view": "View on GitHub",
"app_download_h2": "Ways to get it",
"app_channel_github": "GitHub release",
"app_channel_github_badge": "Easiest · free",
"app_channel_brew": "Homebrew",
"app_channel_brew_badge": "Terminal · one command",
"app_channel_mas": "Mac App Store",
"app_channel_mas_soon": "Coming soon",
"app_token_h2": "Buy me Token",
"app_token_badge": "Support development",
"app_token_body": "These apps are kept running mostly by AI. Instead of a coffee, you can chip in for the AI tokens that pay for ongoing maintenance.",
"app_token_cta": "Buy me Token",
"app_support_h2": "Need help?",
"app_support_cta": "Open an issue on GitHub",
"app_credit_kicker": "In tribute",
"promise_macos": "Latest 2 macOS",
"promise_langs": "7 languages",
"promise_channels": "3 channels",
"promise_icloud": "iCloud sync",
"promise_link": "Why I build & maintain these"
```

- [ ] **Step 2: Add an `ice-2` copy block at the top level of en-US.json**

```json
"ice-2": {
  "title": "Ice 2 — Menu Bar Manager for Mac, rebuilt for macOS 26 & 27",
  "description": "Ice 2 is a free, open-source menu bar manager for Mac — hide and arrange menu bar items, then show them on demand. Rebuilt to support macOS 26 and 27.",
  "eyebrow": "The menu bar manager for macOS",
  "h1": "Tame your menu bar — back on modern macOS",
  "sub": "Ice 2 hides the menu bar items you don't need, brings them back when you want them, and lets you lay the bar out your way. A faithful, open-source rebuild — now running on macOS 26 and 27.",
  "demo_caption": "A Mac menu bar managed by Ice 2: rarely-used icons are tucked behind a divider, while the clock, battery, Wi-Fi and Control Center stay visible.",
  "feat1_h": "Hide menu bar items", "feat1_p": "Tuck rarely-used icons behind a divider so the bar stays clean.",
  "feat2_h": "The Ice Bar", "feat2_p": "Move hidden items into a separate bar that appears on demand.",
  "feat3_h": "Show on demand", "feat3_p": "Reveal items with a click, a hotkey, or by hovering the edge.",
  "support_body": "I maintain Ice 2 for free in my spare time. Questions, bug reports and feature requests are genuinely welcome — open an issue on GitHub and I'll take a look.",
  "credit_body": "Ice 2 is an independent, open-source rebuild of <strong><a href=\"https://github.com/jordanbaird/Ice\">Ice</a></strong>, the menu bar manager originally created by <strong>Jordan Baird</strong>. This fork, actively maintained by Teddy Chan, carries it forward to modern macOS.",
  "faq": [
    {"q": "What does Ice 2 do?", "a": "Ice 2 hides the menu bar items you don't need so your menu bar stays clean, and brings them back on demand — with a click, a hotkey, or by hovering."},
    {"q": "How do I install Ice 2?", "a": "Download from the latest GitHub release and drag it to Applications, or install with Homebrew: brew install --cask teddychan/tap/ice-2."},
    {"q": "What do I need to run Ice 2?", "a": "A Mac running macOS 26 or later."},
    {"q": "Is this the original Ice?", "a": "It is an independent, open-source rebuild of Ice (originally by Jordan Baird), carried forward to modern macOS under GPLv3."}
  ]
}
```

- [ ] **Step 3: Add `clipmenu-2` and `yahoo-keykey-2` copy blocks**

Mirror the `ice-2` block shape for both. Source the headline/sub/features from
the existing pages `docs/clipmenu-2/index.html` and `docs/yahoo-keykey-2/index.html`
(read them, lift the human copy, fit the keys above). Each block MUST contain
every key present in the `ice-2` block (English is the source, so all keys must
exist here).

- [ ] **Step 4: Validate JSON**

Run: `python3 -c "import json; json.load(open('i18n/strings/en-US.json')); print('ok')"`
Expected: `ok`

- [ ] **Step 5: Commit**

```bash
git add i18n/strings/en-US.json
git commit -m "content: add unified app-page English copy for all apps"
```

### Task 4: Create `app.html` template

**Files:**
- Create: `i18n/templates/app.html`

- [ ] **Step 1: Create the template**

Build the skeleton modeled on `docs/ice-2/index.html` (which already has the
correct `<head>`, nav, consent, and copy-button JS), but:
- Replace all hard-coded text with `{{ tokens }}` resolved from the app's copy
  block and `common` (the generator resolves page strings from the app slug — Task 5).
- Order the `<body>` sections exactly: **hero (intro) → demo → changelog → download → token → support → credit → promise strip → footer.** Each section after the hero gets the matching `id`: `id="demo"`, `id="changelog"`, `id="download"`, `id="token"`, `id="support"`, `id="credit"`.
- Use these structural tokens (provided by the generator in Task 5):
  `{{ LANG }} {{ CANONICAL }} {{ OG_LOCALE }} {{ ALTERNATES }} {{ SWITCHER }}
   {{ CONSENT_HEAD }} {{ CONSENT_BANNER }} {{ JSONLD }} {{ THEME_CLASS }}
   {{ CHANGELOG_ROWS }} {{ DOWNLOAD_CHANNELS }} {{ TOKEN_BLOCK }}
   {{ URL_ABOUT }} {{ APP_REPO }} {{ APP_ISSUES }}`
- Content tokens come from the copy block: `{{ title }} {{ description }} {{ eyebrow }}
  {{ h1 }} {{ sub }} {{ demo_caption }} {{ feat1_h }}…{{ feat3_p }} {{ support_body }}
  {{ credit_body }}` and headings from `common` (e.g. `{{ app_changelog_h2 }}`).
- The changelog list, download channel cards, the Buy-me-Token block, and the
  JSON-LD are rendered by the generator and injected as whole strings
  (`{{ CHANGELOG_ROWS }}`, `{{ DOWNLOAD_CHANNELS }}`, `{{ TOKEN_BLOCK }}`,
  `{{ JSONLD }}`) so per-app/per-null logic lives in Python, not the template.
- Reference shared assets exactly as the ice-2 page does:
  `<link rel="stylesheet" href="/shared/dragon.css">` and
  `<script src="/shared/i18n.js" defer></script>` (cache-bust adds the `?v=` later).
- Keep the existing `.cmd-copy` clipboard `<script>` from the ice-2 page.
- Wrap the JSON-LD as: `<script type="application/ld+json">\n{{ JSONLD }}\n</script>`.
- Changelog section body:

```html
<section id="changelog"><div class="container">
  <div class="head"><h2>{{ app_changelog_h2 }}</h2><p>{{ app_changelog_sub }}</p></div>
  <div class="changelog">{{ CHANGELOG_ROWS }}</div>
  <p class="changelog-auto">{{ app_changelog_auto }}</p>
</div></section>
```

- Download section body: `<section id="download"><div class="container"><div class="head"><h2>{{ app_download_h2 }}</h2></div>{{ DOWNLOAD_CHANNELS }}</div></section>`
- Token section body: `<section id="token"><div class="container">{{ TOKEN_BLOCK }}</div></section>`
- Support section body:

```html
<section id="support"><div class="container"><div class="support-block">
  <h2>{{ app_support_h2 }}</h2><p>{{ support_body }}</p>
  <a class="btn btn-github" href="{{ APP_ISSUES }}">{{ app_support_cta }}</a>
</div></div></section>
```

- Credit section body (reuse the existing `.credit` block):

```html
<section class="credit"><div class="container">
  <p class="kicker">{{ app_credit_kicker }}</p>
  <p class="body">{{ credit_body }}</p>
</div></section>
```

- Promise strip (before the footer):

```html
<div class="container">
  <div class="promise">
    <span class="promise-chip">{{ promise_macos }}</span>
    <span class="promise-chip">{{ promise_langs }}</span>
    <span class="promise-chip">{{ promise_channels }}</span>
    <span class="promise-chip">{{ promise_icloud }}</span>
  </div>
  <a class="promise-link" href="{{ URL_ABOUT }}">{{ promise_link }} →</a>
</div>
```

- [ ] **Step 2: Verify the file exists**

Run: `test -f i18n/templates/app.html && echo ok`
Expected: `ok` (full token validation happens via the build in Task 5).

- [ ] **Step 3: Commit**

```bash
git add i18n/templates/app.html
git commit -m "feat: unified app-page template (7 sections, owner-specified order)"
```

---

## Phase 4 — Generator: render app pages

### Task 5: Teach `build_i18n.py` to render apps

**Files:**
- Modify: `i18n/build_i18n.py`
- Test: `i18n/tests/test_app_pages.py`

- [ ] **Step 1: Write the failing test**

```python
# i18n/tests/test_app_pages.py
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def build():
    r = subprocess.run([sys.executable, "i18n/build_i18n.py"], cwd=ROOT,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r

def test_app_pages_generated_all_langs():
    build()
    langs = ["", "zh-Hant/", "zh-Hans/", "ja/", "ko/", "es/", "fr/"]
    for slug in ["ice-2", "clipmenu-2", "yahoo-keykey-2"]:
        for lang in langs:
            p = os.path.join(ROOT, "docs", lang, slug, "index.html")
            assert os.path.exists(p), p

def test_app_page_has_sections_in_order():
    build()
    html = open(os.path.join(ROOT, "docs", "ice-2", "index.html")).read()
    order = ['id="demo"', 'id="changelog"', 'id="download"',
             'id="token"', 'id="support"', 'id="credit"']
    positions = [html.index(x) for x in order]
    assert positions == sorted(positions), positions

def test_sitemap_includes_ice_2():
    build()
    sm = open(os.path.join(ROOT, "docs", "sitemap.xml")).read()
    assert "https://www.dragonapp.com/ice-2/" in sm
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest i18n/tests/test_app_pages.py -v`
Expected: FAIL — the build doesn't generate app pages yet, so the order/sitemap assertions fail.

- [ ] **Step 3: Add app loading + helpers to `build_i18n.py`**

After the `PAGES` definition, add:

```python
APPS_DIR = os.path.join(ROOT, "i18n", "apps")
CHANGELOG_DIR = os.path.join(ROOT, "i18n", "changelogs")

def load_apps():
    idx = json.load(open(os.path.join(APPS_DIR, "_index.json")))
    return [json.load(open(os.path.join(APPS_DIR, s + ".json"))) for s in idx]

def load_changelog(slug):
    p = os.path.join(CHANGELOG_DIR, slug + ".json")
    return json.load(open(p)) if os.path.exists(p) else []

def app_url(lang, slug):
    return SITE + "/" + lang_prefix(lang) + slug + "/"
```

- [ ] **Step 4: Add renderers for the injected blocks**

```python
def render_changelog_rows(slug, common):
    rows = []
    view = common.get("app_changelog_view", "View on GitHub")
    for e in load_changelog(slug):
        note = e.get("notes") or "&nbsp;"
        rows.append(
            '<div class="logrow"><span class="ver">%s</span>'
            '<div><div class="lognote">%s</div>'
            '<div class="logmeta">%s · <a href="%s">%s →</a></div></div></div>'
            % (e.get("version", ""), note, e.get("date", ""), e.get("url", "#"), view)
        )
    return "\n".join(rows) if rows else '<p class="logmeta">Release notes coming soon.</p>'

def render_download(app, common):
    cards = []
    cards.append(
        '<div class="plan featured"><span class="badge">%s</span>'
        '<h3>%s</h3><a class="btn btn-github" href="%s/releases/latest">Get the latest release</a></div>'
        % (common.get("app_channel_github_badge", "Easiest · free"),
           common.get("app_channel_github", "GitHub release"), app["repo"]))
    if app.get("homebrew_cask"):
        cards.append(
            '<div class="plan"><span class="badge">%s</span><h3>%s</h3>'
            '<div class="cmd"><code>brew install --cask %s</code>'
            '<button type="button" class="cmd-copy" data-copied="Copied">Copy</button></div></div>'
            % (common.get("app_channel_brew_badge", "Terminal · one command"),
               common.get("app_channel_brew", "Homebrew"), app["homebrew_cask"]))
    if app.get("mas_url"):
        cards.append(
            '<div class="plan"><span class="badge">App Store</span><h3>%s</h3>'
            '<a class="btn btn-appstore" href="%s">Download on the Mac App Store</a></div>'
            % (common.get("app_channel_mas", "Mac App Store"), app["mas_url"]))
    else:
        cards.append(
            '<div class="plan"><span class="badge soon status-soon">%s</span><h3>%s</h3>'
            '<a class="btn btn-disabled" aria-disabled="true">%s</a></div>'
            % (common.get("app_channel_mas_soon", "Coming soon"),
               common.get("app_channel_mas", "Mac App Store"),
               common.get("app_channel_mas_soon", "Coming soon")))
    return '<div class="plans">' + "\n".join(cards) + '</div>'

def render_token(app, common):
    href = app.get("sponsors_url") or "#"
    badge = common.get("app_token_badge", "Support development")
    if not app.get("sponsors_url"):
        badge = "Coming soon · GitHub Sponsors"
    return (
        '<div class="token-block"><span class="badge soon status-soon">%s</span>'
        '<h2>%s</h2><p>%s</p>'
        '<a class="btn btn-primary" href="%s">%s</a></div>'
        % (badge, common.get("app_token_h2", "Buy me Token"),
           common.get("app_token_body", ""), href,
           common.get("app_token_cta", "Buy me Token")))
```

- [ ] **Step 5: Add the JSON-LD renderer (SoftwareApplication + Breadcrumb + FAQ)**

```python
def render_jsonld(app, lang, page_str):
    faq = page_str.get("faq", [])
    graph = [
        {"@type": "SoftwareApplication", "name": app["name"],
         "description": page_str.get("description", ""),
         "url": app_url(lang, app["slug"]),
         "image": SITE + "/icon-512.png",
         "applicationCategory": "UtilitiesApplication",
         "operatingSystem": "macOS " + app["min_macos"],
         "inLanguage": lang,
         "downloadUrl": app["repo"] + "/releases/latest",
         "softwareLicense": app["license_url"],
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD",
                    "url": app["repo"] + "/releases/latest"},
         "publisher": {"@type": "Organization", "name": "Dragon App", "url": SITE + "/"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Dragon App", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": app["name"], "item": app_url(lang, app["slug"])}]},
    ]
    if faq:
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f["q"],
             "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faq]})
    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, indent=2)
```

- [ ] **Step 6: Add the app-page render path**

```python
def _faq_safe(v):
    return v if isinstance(v, str) else ""  # faq lists feed render_jsonld, not text tokens

def build_app_switcher(current, slug, common):
    label = common.get("switcher_label", "Language")
    out = ['        <details class="lang-switch">',
           '          <summary aria-label="%s">%s<span>%s</span></summary>' % (label, GLOBE, NATIVE[current]),
           '          <div class="lang-menu">']
    for l in LANGS:
        active = ' class="active"' if l == current else ""
        aria = ' aria-current="true"' if l == current else ""
        out.append('            <a href="%s" hreflang="%s" data-setlang="%s"%s%s>%s</a>'
                   % (app_url(l, slug), l, l, active, aria, NATIVE[l]))
    out += ['          </div>', '        </details>']
    return "\n".join(out)

def render_app(template, app, lang, strings, missing):
    en = strings["en-US"]
    cur = strings.get(lang, en)
    page_str = cur.get(app["slug"], en.get(app["slug"], {}))
    common = cur.get("common", {}) or en.get("common", {})
    en_common = en.get("common", {})

    specials = {
        "LANG": lang, "OG_LOCALE": OG_LOCALE[lang],
        "CANONICAL": app_url(lang, app["slug"]),
        "ALTERNATES": "\n".join(
            ['  <link rel="alternate" hreflang="%s" href="%s">' % (l, app_url(l, app["slug"])) for l in LANGS]
            + ['  <link rel="alternate" hreflang="x-default" href="%s">' % app_url("en-US", app["slug"])]),
        "SWITCHER": build_app_switcher(lang, app["slug"], common),
        "CONSENT_HEAD": CONSENT_HEAD_EXTERNAL,
        "CONSENT_BANNER": build_consent(common, en_common),
        "THEME_CLASS": app.get("theme", ""),
        "URL_ABOUT": SITE + "/" + lang_prefix(lang) + "about/",
        "APP_REPO": app["repo"], "APP_ISSUES": app["repo"] + "/issues",
        "CHANGELOG_ROWS": render_changelog_rows(app["slug"], common),
        "DOWNLOAD_CHANNELS": render_download(app, common),
        "TOKEN_BLOCK": render_token(app, common),
        "JSONLD": render_jsonld(app, lang, page_str if page_str else en.get(app["slug"], {})),
    }

    def repl(m):
        name = m.group(1)
        if name in specials: return specials[name]
        if name in page_str: return _faq_safe(page_str[name])
        if name in common: return common[name]
        if name in en.get(app["slug"], {}):
            missing.append((lang, app["slug"], name)); return _faq_safe(en[app["slug"]][name])
        if name in en_common:
            missing.append((lang, app["slug"], name)); return en_common[name]
        raise KeyError("Unknown token {{ %s }} in app '%s'" % (name, app["slug"]))
    return TOKEN_RE.sub(repl, template)
```

- [ ] **Step 7: Wire app rendering into `main()` and the sitemap**

In `main()`, after the existing page loop (before `write_sitemap()`), add:

```python
    app_tpl = open(os.path.join(TEMPLATES_DIR, "app.html"), encoding="utf-8").read()
    for app in load_apps():
        for lang in available:
            html = render_app(app_tpl, app, lang, strings, missing)
            dest = os.path.join(DOCS, lang_prefix(lang), app["slug"], "index.html")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding="utf-8") as f:
                f.write(html)
            count += 1
```

In `write_sitemap()`, after the `I18N_PAGES` loop, add:

```python
    for app in load_apps():
        for lang in LANGS:
            lines.append("  <url>")
            lines.append("    <loc>%s</loc>" % app_url(lang, app["slug"]))
            for alt in LANGS:
                lines.append('    <xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (alt, app_url(alt, app["slug"])))
            lines.append('    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>' % app_url("en-US", app["slug"]))
            lines.append("    <lastmod>%s</lastmod>" % LASTMOD)
            lines.append("    <changefreq>monthly</changefreq>")
            lines.append("    <priority>0.9</priority>")
            lines.append("  </url>")
```

- [ ] **Step 8: Run the build and the tests**

Run: `python3 i18n/build_i18n.py && python3 -m pytest i18n/tests/ -v`
Expected: build prints `Built N pages`; all tests PASS. `[fallback]` lines for non-en languages are acceptable until Task 12.

- [ ] **Step 9: Commit**

```bash
git add i18n/build_i18n.py i18n/tests/test_app_pages.py docs/
git commit -m "feat: generate unified app pages + sitemap entries from registry"
```

---

## Phase 5 — CSS for new sections (light + dark)

### Task 6: Style changelog, token, support, promise strip

**Files:**
- Modify: `docs/shared/dragon.css`

- [ ] **Step 1: Append themed styles using existing tokens only**

Add to `docs/shared/dragon.css` (every color references a `var(--…)` so dark mode works automatically):

```css
/* changelog */
.changelog { max-width: 760px; margin: 0 auto; border: 1px solid var(--border); border-radius: 14px; overflow: hidden; }
.logrow { display: flex; gap: 14px; padding: 16px; border-bottom: 1px solid var(--border); }
.logrow:last-child { border-bottom: none; }
.logrow .ver { font-family: ui-monospace, Menlo, monospace; font-weight: 700; color: var(--accent-deep); min-width: 56px; }
.lognote { font-weight: 600; }
.logmeta { font-size: 0.85rem; color: var(--muted); }
.changelog-auto { text-align: center; font-size: 0.8rem; color: var(--muted); margin-top: 12px; }
/* buy me token */
.token-block { max-width: 640px; margin: 0 auto; text-align: center; background: var(--surface); border: 1px solid var(--border); border-radius: 18px; padding: 36px 28px; }
.token-block h2 { margin: 10px 0 8px; }
.token-block p { color: var(--muted); max-width: 46ch; margin: 0 auto 22px; }
.badge.soon { display: inline-block; }
/* support block */
.support-block { max-width: 640px; margin: 0 auto; text-align: center; background: var(--surface); border-radius: 18px; padding: 36px 28px; }
.support-block p { color: var(--muted); max-width: 50ch; margin: 0 auto 22px; }
/* promise strip */
.promise { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; background: var(--accent-tint); border-radius: 16px; padding: 18px; margin: 12px 0; }
.promise-chip { background: var(--bg); border: 1px solid var(--border); border-radius: 999px; padding: 8px 16px; font-size: 0.85rem; font-weight: 600; color: var(--accent-ink); }
.promise-link { display: block; text-align: center; font-weight: 600; margin: 4px 0 8px; }
```

- [ ] **Step 2: Re-run cache-bust + build**

Run: `bash scripts/cache-bust.sh && python3 i18n/build_i18n.py`
Expected: CSS fingerprint updates; build clean.

- [ ] **Step 3: Visually verify light + dark**

Open `docs/ice-2/index.html` in a browser; toggle OS appearance (or DevTools "Emulate prefers-color-scheme"). Confirm changelog/token/support/promise all read correctly in both modes.

- [ ] **Step 4: Commit**

```bash
git add docs/shared/dragon.css docs/
git commit -m "style: themed changelog, token, support, promise sections (light+dark)"
```

---

## Phase 6 — About page

### Task 7: `about.html` template + strings + wiring

**Files:**
- Create: `i18n/templates/about.html`
- Modify: `i18n/strings/en-US.json` (add `about` block)
- Modify: `i18n/build_i18n.py` (register the `about` page)
- Test: `i18n/tests/test_about.py`

- [ ] **Step 1: Write the failing test**

```python
# i18n/tests/test_about.py
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def test_about_pages_built():
    subprocess.run([sys.executable, "i18n/build_i18n.py"], cwd=ROOT, check=True)
    for lang in ["", "zh-Hant/", "ja/", "fr/"]:
        assert os.path.exists(os.path.join(ROOT, "docs", lang, "about", "index.html"))
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest i18n/tests/test_about.py -v`
Expected: FAIL.

- [ ] **Step 3: Add the `about` strings block to en-US.json**

```json
"about": {
  "title": "Why Dragon App — apps I love, kept alive",
  "description": "Dragon App revives macOS apps their original makers no longer maintain. The story behind the studio, and the promise behind every app.",
  "h1": "Apps I love, kept alive",
  "story": "Every app here is one I rely on every day — and that its original maintainer could no longer keep going. Rather than watch them break on each new macOS, I adopted them. Today they're maintained largely with the help of AI, which is also why support runs on 'Buy me Token' instead of coffee.",
  "promise_h2": "What every Dragon App promises",
  "promise_macos_d": "Runs on at least the latest two macOS releases.",
  "promise_langs_d": "Available in 7 languages, like this site.",
  "promise_channels_d": "Installable 3 ways: GitHub, Homebrew, and (where possible) the Mac App Store.",
  "promise_icloud_d": "Settings sync across your Macs via iCloud."
}
```

- [ ] **Step 4: Create `i18n/templates/about.html`**

A single-column page reusing the `<head>`/nav/footer/consent structure from
`app.html` (no app-specific tokens). Body: `<h1>{{ h1 }}</h1>`, the `{{ story }}`
paragraph, and a promise grid pairing `{{ promise_macos }}`/`{{ promise_macos_d }}`
(and langs/channels/icloud). Structural tokens: `{{ LANG }} {{ CANONICAL }}
{{ ALTERNATES }} {{ SWITCHER }} {{ OG_LOCALE }} {{ CONSENT_HEAD }} {{ CONSENT_BANNER }}`.
The generator's existing `render()` already supplies these for registered pages.

- [ ] **Step 5: Register `about` as an i18n page**

In `build_i18n.py` `PAGES`, add:
```python
    "about": ("about.html", "about/", os.path.join("about", "index.html")),
```
add `"about"` to `I18N_PAGES`, and set `PRIORITY["about"] = "0.6"`.

- [ ] **Step 6: Build + test**

Run: `python3 i18n/build_i18n.py && python3 -m pytest i18n/tests/test_about.py -v`
Expected: build clean; PASS.

- [ ] **Step 7: Commit**

```bash
git add i18n/templates/about.html i18n/strings/en-US.json i18n/build_i18n.py i18n/tests/test_about.py docs/
git commit -m "feat: localized /about/ story + promise page"
```

---

## Phase 7 — Hub regenerated from registry

### Task 8: Generate hub app cards from the registry

**Files:**
- Modify: `i18n/templates/index.html` (replace hard-coded app cards with `{{ APP_CARDS }}`)
- Modify: `i18n/build_i18n.py` (render `APP_CARDS` for the index page)
- Test: extend `i18n/tests/test_app_pages.py`

- [ ] **Step 1: Add a card renderer to `build_i18n.py`**

```python
def render_app_cards(lang, strings):
    cur = strings.get(lang, strings["en-US"])
    cards = []
    for app in load_apps():
        ps = cur.get(app["slug"], strings["en-US"].get(app["slug"], {}))
        cards.append(
            '<a class="app-card %s" href="%s"><div class="app-head">'
            '<span class="app-icon"><span class="glyph">%s</span></span>'
            '<h3>%s</h3></div><p class="desc">%s</p>'
            '<div class="app-foot"><span>macOS · Free · Open source</span>'
            '<span class="arrow">→</span></div></a>'
            % (app.get("theme", ""), app_url(lang, app["slug"]),
               app["name"][:1], app["name"], ps.get("sub", "")))
    return '<div class="apps">' + "\n".join(cards) + "</div>"
```

Add `"APP_CARDS": render_app_cards(lang, strings)` to the `specials` dict inside
the existing `render()` function so the index template can use it.

- [ ] **Step 2: Replace the hard-coded cards in `i18n/templates/index.html`**

Find the existing app-cards block and replace its contents with `{{ APP_CARDS }}`.
Leave the hero and other index content intact.

- [ ] **Step 3: Add a test (append to `test_app_pages.py`)**

```python
def test_hub_lists_all_apps():
    build()
    html = open(os.path.join(ROOT, "docs", "index.html")).read()
    for slug in ["ice-2", "clipmenu-2", "yahoo-keykey-2"]:
        assert "/%s/" % slug in html
```

- [ ] **Step 4: Build + test**

Run: `python3 i18n/build_i18n.py && python3 -m pytest i18n/tests/ -v`
Expected: build clean; all PASS.

- [ ] **Step 5: Commit**

```bash
git add i18n/templates/index.html i18n/build_i18n.py i18n/tests/test_app_pages.py docs/
git commit -m "feat: generate hub app cards from the registry"
```

---

## Phase 8 — Localize privacy

### Task 9: Make privacy a 7-language i18n page

**Files:**
- Modify: `i18n/build_i18n.py` (move `privacy` from `EN_ONLY_PAGES` to `I18N_PAGES`)
- Modify: `i18n/strings/<lang>.json` (ensure a `privacy` block exists; English is source)

- [ ] **Step 1: Confirm `privacy` strings exist in en-US**

Run: `python3 -c "import json;print('privacy' in json.load(open('i18n/strings/en-US.json')))"`
Expected: `True`. If `False`, add a `privacy` block sourced from `PRIVACY.md` / the current `docs/privacy.html` before continuing.

- [ ] **Step 2: Switch privacy to localized**

In `build_i18n.py`: remove `"privacy"` from `EN_ONLY_PAGES`, add it to `I18N_PAGES`. Keep `PRIORITY["privacy"]`.

- [ ] **Step 3: Build + verify localized output**

Run: `python3 i18n/build_i18n.py && test -f docs/zh-Hant/privacy.html && echo ok`
Expected: `ok` (English text falls back per-key until translations land in Task 12).

- [ ] **Step 4: Commit**

```bash
git add i18n/build_i18n.py docs/
git commit -m "feat: localize the privacy page to all 7 languages"
```

---

## Phase 9 — Legacy redirects + llms.txt

### Task 10: Legacy `/clipmenu/` and `/keykey/` redirect pointers

**Files:**
- Modify: `i18n/build_i18n.py` (emit redirect stubs; stop emitting full legacy pages)
- Delete: `i18n/templates/keykey.html`, `i18n/templates/clipmenu.html`
- Test: `i18n/tests/test_redirects.py`

- [ ] **Step 1: Write the failing test**

```python
# i18n/tests/test_redirects.py
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def test_legacy_redirects():
    subprocess.run([sys.executable, "i18n/build_i18n.py"], cwd=ROOT, check=True)
    for old, new in [("clipmenu", "clipmenu-2"), ("keykey", "yahoo-keykey-2")]:
        html = open(os.path.join(ROOT, "docs", old, "index.html")).read()
        assert "/%s/" % new in html
        assert 'http-equiv="refresh"' in html
        assert "canonical" in html
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest i18n/tests/test_redirects.py -v`
Expected: FAIL (current legacy pages are full pages, not redirects).

- [ ] **Step 3: Add a redirect emitter to `build_i18n.py`**

```python
LEGACY_REDIRECTS = {"clipmenu": "clipmenu-2", "keykey": "yahoo-keykey-2"}

def write_redirects():
    for old, new in LEGACY_REDIRECTS.items():
        for lang in LANGS:
            target = app_url(lang, new)
            html = (
                "<!DOCTYPE html><html lang=\"%s\"><head><meta charset=\"utf-8\">"
                "<title>Moved</title>"
                "<link rel=\"canonical\" href=\"%s\">"
                "<meta http-equiv=\"refresh\" content=\"0; url=%s\">"
                "<meta name=\"robots\" content=\"noindex\">"
                "</head><body><p>This app has moved to <a href=\"%s\">%s</a>.</p>"
                "</body></html>" % (lang, target, target, target, target)
            )
            dest = os.path.join(DOCS, lang_prefix(lang), old, "index.html")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding="utf-8") as f:
                f.write(html)
```

Call `write_redirects()` from `main()` after the app loop. Remove the legacy
`keykey`/`clipmenu` entries from `PAGES` and `I18N_PAGES` so the generator no
longer emits full pages for them, and delete `i18n/templates/keykey.html` and
`i18n/templates/clipmenu.html`.

- [ ] **Step 4: Build + test**

Run: `python3 i18n/build_i18n.py && python3 -m pytest i18n/tests/test_redirects.py -v`
Expected: build clean; PASS.

- [ ] **Step 5: Commit**

```bash
git add i18n/build_i18n.py i18n/tests/test_redirects.py i18n/templates/ docs/
git commit -m "feat: redirect legacy /clipmenu/ and /keykey/ to current app pages"
```

### Task 11: Generate `/llms.txt`

**Files:**
- Modify: `i18n/build_i18n.py` (write `docs/llms.txt`)

- [ ] **Step 1: Add the writer**

```python
def write_llms_txt(strings):
    en = strings["en-US"]
    lines = ["# Dragon App", "",
             "> A small studio reviving beloved, discontinued macOS apps as free, open-source rebuilds.",
             "", "## Apps"]
    for app in load_apps():
        ps = en.get(app["slug"], {})
        lines.append("- [%s](%s): %s Install: brew install --cask %s"
                     % (app["name"], app_url("en-US", app["slug"]),
                        ps.get("sub", ""), app.get("homebrew_cask") or "n/a"))
    lines += ["", "## About", "%s/about/ — why these apps exist and the maintenance promise." % SITE]
    with open(os.path.join(DOCS, "llms.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
```

Call `write_llms_txt(strings)` from `main()`.

- [ ] **Step 2: Build + verify**

Run: `python3 i18n/build_i18n.py && grep -q "Dragon App" docs/llms.txt && echo ok`
Expected: `ok`.

- [ ] **Step 3: Commit**

```bash
git add i18n/build_i18n.py docs/llms.txt
git commit -m "feat: generate /llms.txt for AI crawlers (GEO)"
```

---

## Phase 10 — Translations

### Task 12: Translate app, about, and privacy blocks into 6 languages

**Files:**
- Modify: `i18n/strings/zh-Hant.json`, `zh-Hans.json`, `ja.json`, `ko.json`, `es.json`, `fr.json`

- [ ] **Step 1: Identify fallback gaps**

Run: `python3 i18n/build_i18n.py`
Read the `[fallback] <lang> missing N keys` summary — those are untranslated keys.

- [ ] **Step 2: Add translations per language**

For each language file, add the `ice-2`, `clipmenu-2`, `yahoo-keykey-2`, `about`,
and `privacy` blocks plus the new `common` app/promise keys, mirroring the en-US
keys exactly. Translate values; keep HTML tags and URLs intact. Do not translate
brand names, commands (`brew install …`), or code.

- [ ] **Step 3: Rebuild until no fallbacks for content keys**

Run: `python3 i18n/build_i18n.py`
Expected: no `[fallback]` lines for the app/about/privacy keys. FAQ entries and
changelog notes staying in source language is acceptable by design.

- [ ] **Step 4: Commit**

```bash
git add i18n/strings/ docs/
git commit -m "i18n: translate app/about/privacy copy into all 6 non-English languages"
```

---

## Phase 11 — SEO / GEO / PageSpeed verification

### Task 13: Optimize assets and verify PageSpeed 100

**Files:**
- Modify: `docs/robots.txt` (ensure `Sitemap:` line), images under `docs/`
- Verify only: Lighthouse

- [ ] **Step 1: Run the asset-optimization workflow**

Invoke the `dragonapp-site-optimize` skill (pngquant images, add explicit
width/height, minify, then `scripts/cache-bust.sh`). Rebuild: `python3 i18n/build_i18n.py`.

- [ ] **Step 2: Confirm robots + sitemap reference each other**

Run: `grep -i sitemap docs/robots.txt`
Expected: `Sitemap: https://www.dragonapp.com/sitemap.xml`. Add the line if missing.

- [ ] **Step 3: Run the SEO skill**

Invoke the `/seo` skill against the generated app pages, the hub, and `/about/`:
titles/meta/OG, JSON-LD validity, internal links, hreflang. No fake `aggregateRating`.

- [ ] **Step 4: Lighthouse check (hard goal: 100)**

```bash
cd docs && python3 -m http.server 8099 &
# then: npx lighthouse http://localhost:8099/ice-2/ --view   (or Chrome DevTools)
```
Expected: Performance, Accessibility, Best Practices, SEO = 100 on mobile + desktop.
Fix any flagged issue (most likely image dimensions, contrast, or a render-blocking resource), rebuild, re-check. Stop the server when done (`kill %1`).

- [ ] **Step 5: Run the full test suite**

Run: `python3 -m pytest i18n/tests/ -v`
Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add docs/
git commit -m "perf: optimize assets, verify SEO + PageSpeed 100 across pages"
```

---

## Phase 12 — Final review

### Task 14: Whole-site verification before publish

- [ ] **Step 1: Clean rebuild from scratch**

```bash
python3 i18n/build_i18n.py && python3 -m pytest i18n/tests/ -v
```
Expected: `Built N pages`, all tests PASS.

- [ ] **Step 2: Spot-check each surface in a browser (light + dark)**

`/`, `/ice-2/`, `/zh-Hant/ice-2/`, `/about/`, `/privacy.html`, and a legacy
redirect `/keykey/`. Confirm section order, theme correctness, working copy
buttons, language switcher, and the redirect.

- [ ] **Step 3: Confirm no stale hand-made app HTML remains**

Run: `git status` — only generator-owned `docs/` files changed; no orphaned old
per-app HTML differing from generated output.

- [ ] **Step 4: Final commit (if anything outstanding)**

```bash
git add -A && git commit -m "chore: finalize unified app site"
```

---

## Self-Review (completed by author)

**Spec coverage:**
- Data-driven template → Tasks 1, 4, 5. URL map → Tasks 5, 7, 9. Section order → Task 4 + ordering test in Task 5. 3 channels incl. MAS placeholder → Task 5 `render_download`. Buy me Token placeholder → Task 5 `render_token`. Changelog auto from GitHub → Tasks 2, 5. About page → Task 7. Light/dark → Task 6. SEO/GEO (JSON-LD, FAQ, llms.txt, sitemap) → Tasks 5, 11, 13. PageSpeed 100 → Task 13. Legacy redirects → Task 10. Privacy on-site + localized → Task 9. Translations → Task 12. Every spec section maps to a task.
- **Confirm-at-execution items (flagged, not invented):** ClipMenu/KeyKey exact license + KeyKey cask name (Task 1).

**Placeholder scan:** No "TBD"/"implement later". Content tasks (3, 12) provide the full English exemplar and exact acceptance checks; translation values are produced at execution by definition.

**Type/name consistency:** `app_url`, `load_apps`, `load_changelog`, `render_changelog_rows`, `render_download`, `render_token`, `render_jsonld`, `render_app`, `build_app_switcher`, `_faq_safe`, `render_app_cards`, `write_redirects`, `write_llms_txt` are referenced consistently across tasks. Token names in Task 4 match the `specials` keys and copy keys produced in Tasks 3/5.
