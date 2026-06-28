# Unified Dragon App site — design spec

**Date:** 2026-06-28
**Status:** Approved (design), pending implementation plan
**Scope:** Restructure www.dragonapp.com so every app has the same page
structure, generated from a single source, in 7 languages, optimized for SEO,
GEO (ChatGPT/Gemini), human readability, and a PageSpeed score of 100.

---

## 1. Goals

1. **Unified structure** — every app page has the same sections in the same
   order, so the studio feels like one product family.
2. **Single source of truth** — adding or editing an app is data-only; no
   hand-maintained per-language HTML. Zero drift.
3. **7 languages always** — en-US, zh-Hant, zh-Hans, ja, ko, es, fr.
4. **3 distribution channels per app** — GitHub binary, Homebrew, Mac App Store
   (the last is an optional, per-app placeholder until provided).
5. **SEO + GEO + PageSpeed 100** on every page.
6. **Light & dark theme** by system preference; default light when undetectable.

Non-goals: a CMS, server-side rendering, JS frameworks, or any runtime backend.
The site stays a static set of files served by GitHub Pages from `docs/`.

## 2. Build architecture (data-driven template)

Extend the existing generator `i18n/build_i18n.py`. Input layers:

| Layer | File | Holds | Language? |
|---|---|---|---|
| Template | `i18n/templates/app.html` | the single app-page skeleton (all sections, `{{ tokens }}`) | — |
| App facts | `i18n/apps/<slug>.json` | slug, theme class, repo URL, Homebrew cask, Mac App Store URL (or `null`), license + URL, min macOS, appcast path, upstream credit, Sponsors URL (or `null`), icon | language-independent |
| Copy | `i18n/strings/<lang>.json` | per-app text block (eyebrow, headline, sub, features, demo caption, support text, credit text, FAQ) + section headings + `about` page strings | per-language |
| Changelog | `i18n/changelogs/<slug>.json` | `[{version, date, notes, min_macos, url}]` (generated, committed) | source language |

The generator loops `apps × languages`, renders `app.html`, and writes
`docs/<slug>/index.html` (en) and `docs/<lang>/<slug>/index.html`. It also adds
every app + `/about/` to `docs/sitemap.xml` with hreflang alternates. Today
`ice-2` is missing from the sitemap; this fixes that class of bug permanently.

The old per-app templates `keykey.html` and `clipmenu.html` are removed in
favor of `app.html`.

### App registry

Apps are listed in a registry (in `build_i18n.py` or `i18n/apps/_index.json`):
`ice-2`, `clipmenu-2`, `yahoo-keykey-2`. The hub (`/`) is generated from the
same registry so app cards never go out of sync with app pages.

## 3. URL map (all bookmarkable, all in sitemap)

```
/                         hub (en)            /<lang>/                hub
/<slug>/                  app page (en)       /<lang>/<slug>/         app page
/about/                   story + promise     /<lang>/about/          localized
/privacy.html             privacy (en)        /<lang>/privacy.html    localized
/support.html             support hub         /<lang>/support.html    localized
```

Section anchors on each app page: `#demo`, `#changelog`, `#download`, `#token`,
`#support`, `#credit`. Each is a stable, shareable deep link.

## 4. The unified app page — section order

Per the owner's chosen order:

1. **① Intro / hero** — app glyph, eyebrow, H1 headline, 1–2 line description,
   primary CTA (GitHub) + secondary ("See install options"), requirements line.
   A compact feature trio sits under the hero/demo as supporting content.
2. **③ Demo** — stylized CSS/SVG product shot (placeholder, swappable for real
   screenshots/GIFs later), with `role="img"` + descriptive `aria-label`.
3. **④ Changelog** — auto-generated, newest first (see §6).
4. **② Download / install** — 3 channel cards: GitHub (featured), Homebrew
   (copy-able command), Mac App Store. The MAS card renders **"Coming soon"**
   when `mas_url` is `null`, and a real App Store button when set.
5. **⑦ Buy me Token** — explainer ("these apps are kept alive mostly by AI;
   instead of a coffee, fund the AI tokens that pay for maintenance") + button.
   Placeholder link now; swap to GitHub Sponsors when `sponsors_url` is set.
6. **⑥ Support** — "I maintain these for free; questions and feature requests
   welcome" → button to the repo's Issues.
7. **⑤ Credit** — tribute to the original author / upstream project.

Then a slim **"Our promise" strip** (Latest 2 macOS · 7 languages · 3 channels ·
iCloud sync) linking to `/about/`, followed by the footer (All apps, Support,
Privacy on-site, GitHub, License).

## 5. The `/about/` page

The owner's story — *apps they love and rely on, whose original maintainers
moved on, now kept alive largely with AI* — followed by the full **promise**
(the 4 commitments) as the studio-wide trust anchor. Localized to all 7
languages. Linked from the hub and every app page. Same template system, its
own `about.html` template + `about` strings block per language.

## 6. Changelog (auto-generated, hermetic)

The Sparkle appcasts (`docs/<slug>/appcast.xml`) contain only version + date +
minimum macOS — **no release notes**. Human-readable notes come from GitHub
Releases. To keep GitHub Pages builds offline and deterministic:

1. **`scripts/fetch-changelogs.py`** — run manually or in release CI. Calls the
   GitHub Releases API per app, writes `i18n/changelogs/<slug>.json`
   (`version, date, notes, min_macos, url`) into the repo.
2. **`build_i18n.py`** reads that JSON and renders the changelog section. No
   network at site-build time.
3. Each entry links to its full GitHub release. If a release has no body, the
   entry falls back to *"Version X — released <date> · requires macOS Y."*

**Known tradeoff:** notes are only as friendly as the GitHub release text, and
they stay in their original (source) language — section headings are translated,
entry bodies are not. Optional later enhancement: have the fetch script
AI-summarize each release into plain-language bullets.

## 7. Light & dark theme

`dragon.css` already defines light + dark via `@media (prefers-color-scheme)`
and per-app accent overrides. Work needed: ensure every **new** section
(changelog, Buy me Token, support block, promise strip, about page) uses theme
tokens (`var(--…)`) and reads correctly in both modes. Default is light, because
`prefers-color-scheme` resolves to light when no system preference is detectable.
No manual toggle ships on the live site (the mockup toggle was for review only);
the site follows the OS setting.

## 8. SEO + GEO + PageSpeed

**Keep & extend the existing strong base**, now generated for every app:
- Canonical, `hreflang` for all 7 langs + `x-default`, OG + Twitter cards.
- JSON-LD `@graph`: `SoftwareApplication`, `BreadcrumbList`, `FAQPage`.
- `sitemap.xml` (auto, includes every app + `/about/`) and `robots.txt`.

**GEO additions (ChatGPT/Gemini):**
- A per-app natural-language **FAQ** section (LLMs extract Q&A well).
- **`/llms.txt`** — a plain-text site summary for AI crawlers (apps, one-line
  descriptions, URLs, install commands).
- Descriptive `alt`/`aria-label` on the demo mockups; stable section anchors.

**PageSpeed 100 (hard goal, mobile + desktop):**
- Inline critical CSS (the build already inlines `dragon.css`) and i18n JS.
- Defer/async all non-critical JS; no render-blocking resources.
- Images optimized (pngquant) with explicit `width`/`height` (no layout shift).
- Preconnect only what's needed; analytics loads post-consent (already the case).
- Verify with Lighthouse before publish; run the `/seo` skill and the
  `dragonapp-site-optimize` skill (asset minify + cache-bust) per repo rules.

## 9. Legacy pages

`/clipmenu/` and `/keykey/` predate the current `/clipmenu-2/` and
`/yahoo-keykey-2/`. Keep them as **redirect pointers** to the new pages:
- `<link rel="canonical">` to the new URL +
- `<meta http-equiv="refresh" content="0; url=…">` (GitHub Pages has no
  server-side redirects), with a visible "This app moved → " fallback link.
- Applied to all language variants of the legacy slugs.

## 10. App data (initial registry)

| slug | name | theme | repo | cask | MAS | upstream credit |
|---|---|---|---|---|---|---|
| `ice-2` | Ice 2 | theme-ice | teddychan/ice-2 | teddychan/tap/ice-2 | null | Ice © Jordan Baird (GPLv3) |
| `clipmenu-2` | ClipMenu 2 | (blue/default) | teddychan/clipmenu-2 | teddychan/tap/clipmenu-2 | (when shipped) | original ClipMenu lineage |
| `yahoo-keykey-2` | Yahoo KeyKey 2 | theme-keykey | teddychan/yahoo-keykey-2 | (cask if any) | original Yahoo! KeyKey |

(Exact credit/license strings confirmed against each repo during build.)

## 11. Success criteria

- One `app.html` template + per-app JSON drives all 3 apps × 7 languages.
- Every app page renders the 7 sections in the specified order, in all 7
  languages, in light and dark.
- `/about/`, localized privacy, and a `/llms.txt` exist; sitemap lists every
  app + about page.
- Legacy `/clipmenu/` and `/keykey/` redirect to the current pages.
- `python3 i18n/build_i18n.py` regenerates the whole site with no manual edits
  to `docs/`.
- Lighthouse/PageSpeed = 100 on a representative app page (mobile + desktop).
- No fake `aggregateRating` or invented data in structured data.
