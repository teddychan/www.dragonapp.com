# Design — Add `ice-2` (3rd app) to www.dragonapp.com + clarify Homebrew install

**Date:** 2026-06-25
**Status:** Approved (design) — pending spec review
**Repo:** `teddychan/www.dragonapp.com` (GitHub Pages, served from `docs/`)

## Goal

1. Add a third app — **Ice** (repo `teddychan/ice-2`) — to the Dragon App studio site, at full
   parity with the existing two apps (ClipMenu 2, KeyKey): English page + 6 localized copies, hub
   card, sitemap, and JSON-LD.
2. Ice ships **GitHub binary** + **Homebrew** only (no Mac App Store edition), both presented as
   live now.
3. While we're here, surface a **dedicated Homebrew install method** on all three app pages
   (ice-2, ClipMenu 2, KeyKey) with the exact `brew install --cask` command.

## Key facts (verified)

- `teddychan/ice-2`: "Powerful menu bar manager for macOS", homepage `icemenubar.app`,
  license **GPL-3.0** (the other two apps are MIT — attribution/footer/JSON-LD differ accordingly).
- Fork of the discontinued **[jordanbaird/Ice](https://github.com/jordanbaird/Ice)** by Jordan Baird.
  Fork's headline value: **rebuilt to support macOS 26 and 27**.
- No GitHub release or Homebrew cask exists yet, but per owner decision the page treats both as
  **live** (`releases/latest` + `brew install --cask teddychan/tap/ice-2`); the release + cask will
  be published right after this site change.
- Site already ships 7 languages: `en-US` (root) + `zh-Hans`, `zh-Hant`, `ja`, `ko`, `es`, `fr`.
  Each app has a localized `…/<app>/index.html` sibling under each language folder.
- App pages link `/shared/dragon.css`; the hub `index.html` files have the design system **inlined**.
  The new `theme-ice` accent only needs to live in `dragon.css` (only the ice-2 page uses it).
- Homebrew currently appears only in `support.html`. Cask tokens:
  - ice-2 → `teddychan/tap/ice-2`
  - ClipMenu 2 → `teddychan/tap/clipmenu-2`
  - KeyKey → `teddychan/tap/yahoo-keykey-2`

## Decisions (from brainstorming)

| Decision | Choice |
|---|---|
| ice-2 availability | **Live now** — link `releases/latest` + working brew command |
| Localization | **Full parity (7 languages)** |
| Homebrew presentation | **Dedicated Homebrew card** in each download section (3 cards per page) |
| ice-2 icon | **Placeholder glyph** (snowflake) in Dragon style; real icon dropped in later |

## Architecture / approach

Follow the **KeyKey page template** for ice-2 (closest match: GitHub-only, glyph icon, signed
download story). Reuse the shared design system; add minimal new CSS only.

### New CSS (in `docs/shared/dragon.css`)

1. `body.theme-ice` — icy cyan/teal accent, light + dark `@media (prefers-color-scheme: dark)`
   variants, mirroring the existing `body.theme-keykey` block (override `--accent`, `--accent-action`,
   `--accent-action-ink`, `--accent-deep`, `--accent-tint`, `--accent-ink`, `--shadow`, `--shadow-sm`).
2. `.cmd` — a copy-paste command block used by the Homebrew cards: monospace line + a small "Copy"
   button. Styled with existing tokens (`--surface-2`, `--border`, `--accent`). Progressive
   enhancement: a tiny inline script wires the copy button; the command is fully usable (selectable)
   without JS.

> Both additions are append-only to `dragon.css`; no existing rules change. After editing, the
> `?v=` fingerprint for `dragon.css` must be re-busted everywhere it is referenced.

### Homebrew card (added to all three app pages' `#download` `.plans`)

A third `.plan` card titled **Homebrew**:
- Badge: "Terminal · one command"
- A `.cmd` block with the app's exact `brew install --cask …`
- 2–3 bullets: "Same free build", "Updates with `brew upgrade --cask`", "Manage with one command"
- Result: ice-2 → GitHub (featured) + Homebrew (2 cards); ClipMenu 2 → App Store (featured) +
  GitHub + Homebrew (3 cards); KeyKey → GitHub (featured) + App Store (coming soon) + Homebrew (3).

The `.plans` grid is `repeat(auto-fit, minmax(300px, 1fr))`, so 3 cards reflow cleanly.

## New page: `docs/ice-2/index.html` (English, source of truth)

Structure mirrors KeyKey. Finalized English copy:

- `<title>`: `Ice — Menu Bar Manager for Mac, rebuilt for macOS 26 & 27`
- `<meta name="description">`: `Ice is a free, open-source menu bar manager for Mac — hide and arrange menu bar items, show them on demand. Rebuilt to support macOS 26 and 27. Download free on GitHub or with Homebrew.`
- canonical `https://www.dragonapp.com/ice-2/`; 7 hreflang alternates + x-default; OG/Twitter tags.
- `<body class="theme-ice">`
- **Hero**
  - Snowflake glyph (`appicon appicon-lg`) instead of a PNG.
  - eyebrow: `The menu bar manager for macOS`
  - H1: `Tame your menu bar — back on modern macOS`
  - sub: `Ice hides the menu bar items you don't need, brings them back when you want them, and lets you lay the bar out your way. A faithful, open-source rebuild — now running on macOS 26 and 27.`
  - CTAs: GitHub (`btn btn-github` → `https://github.com/teddychan/ice-2/releases/latest`) and a
    secondary link to `#download`.
  - req line: `Requires macOS 26 or later · Universal · Open source (GPLv3)`
- **Product shot** — reuse `.window` mock styled as a menu bar: a row of menu-bar glyphs with a
  "hidden" divider (⋯) and a couple items revealed, captioned to explain hide/show. `role="img"`
  with descriptive `aria-label`.
- **Features** (6 × `.feature`), icons reuse the existing inline-SVG style:
  1. **Hide menu bar items** — Tuck away the icons you rarely use; your menu bar stays clean.
  2. **The Ice Bar** — Move hidden items into a separate bar that appears only when you call it.
  3. **Show on demand** — Reveal hidden items with a click, a hotkey, or by hovering — your choice.
  4. **Arrange & space** — Reorder items and control spacing so the bar looks exactly how you like.
  5. **Custom hotkeys & appearance** — Bind shortcuts and tweak the menu bar's tint, shadow, and border.
  6. **Free & open source** — Full source on GitHub under the GPLv3 — inspect it, build it, trust it.
- **How it works** (`#how`, 3 × `.step`):
  1. **Install & launch** — Get Ice from GitHub or Homebrew and open it; it lives in your menu bar.
  2. **Pick what to hide** — Drag the divider so the items to its left stay hidden until you need them.
  3. **Reveal anytime** — Click the Ice icon or press your hotkey to show everything, then auto-hide again.
- **Download** (`#download`): GitHub release (featured) + Homebrew card (see above).
  - GitHub card bullets: direct `.app` download, no account; built-in updates; full GPLv3 source;
    runs on macOS 26 & 27.
- **Credit** (`.credit`): attribute the original **Ice by Jordan Baird**, note the GPLv3 rebuild.
- **Footer**: links to All apps, ClipMenu 2, KeyKey, Support, GitHub (`teddychan/ice-2`),
  License (GPLv3). © line references GPLv3.
- **Consent banner** markup (identical to other pages).

### JSON-LD on the ice-2 page

- `SoftwareApplication`: name "Ice", `applicationCategory` UtilitiesApplication, `operatingSystem`
  "macOS 26", `downloadUrl` releases/latest, `softwareLicense` ice-2 LICENSE (GPLv3), single free
  `Offer` (price 0). **No `aggregateRating`** (per global rule).
- `BreadcrumbList`: Dragon App → Ice.
- `FAQPage`: 4 Qs — "What does Ice do?", "How do I install it?" (GitHub pkg/app **or**
  `brew install --cask teddychan/tap/ice-2`), "What do I need to run it?" (macOS 26+), "Is this the
  original Ice?" (independent fork of Jordan Baird's Ice, GPLv3).

## Hub changes: `docs/index.html` (+ 6 localized copies)

- Add a 3rd `.app-card` linking `ice-2/` **before** the `.placeholder` card:
  - Icon: inline snowflake SVG inside `.app-icon`.
  - H3 "Ice"; status `status-available` ("Available" / localized).
  - desc (en): `A clean menu bar, on your terms — hide, arrange, and reveal menu bar items. Rebuilt for macOS 26 & 27.`
  - foot: `macOS · Free · Open source` (localized).
- Add ice-2 as **position 3** in the `ItemList` JSON-LD (`SoftwareApplication`, url `/ice-2/`).
- Update the homepage `<meta name="description">` / OG text that currently says
  "starting with ClipMenu 2 and KeyKey" → include Ice (en + localized).

## Add Homebrew card to existing pages (en + 6 localized each)

- `docs/clipmenu/index.html` — add Homebrew card (`clipmenu-2`).
- `docs/keykey/index.html` — add Homebrew card (`yahoo-keykey-2`).
- Localized siblings get the same card with translated badge/bullets; the command itself stays
  in English (it's a literal shell command).

## Localization plan (translated copy, English brand names)

Create and translate, following the conventions already used by the localized ClipMenu/KeyKey pages:
- `docs/{zh-Hans,zh-Hant,ja,ko,es,fr}/ice-2/index.html`
- Translate visible copy, `lang` attribute, hreflang `active` state, status badges, nav labels,
  consent banner. Keep brand names ("Ice", "Dragon App", "Homebrew") and shell commands in English.
- JSON-LD on localized pages keeps English `name`, adjusts `url`/`inLanguage` to match existing
  localized pages' pattern.

## SEO & build hygiene (definition of done)

1. `docs/sitemap.xml`: add 7 `ice-2` `<url>` blocks (en + 6 locales) with 7 hreflang alternates
   each + x-default, `priority` 0.8, `lastmod` 2026-06-25 (matches keykey rows).
2. `docs/robots.txt`: no change (site is `Allow: /`; `/superpowers/` already disallowed — this spec
   lives there and stays out of the index).
3. Run the **`/seo`** skill over the new ice-2 page (titles/meta/OG, JSON-LD, internal links). No fake
   `aggregateRating`.
4. Run **dragonapp-site-optimize** (minify/compress, image dimensions) before committing.
5. **Cache-bust** changed assets (`scripts/cache-bust.sh`) so `dragon.css`'s `?v=` hash updates
   everywhere it is referenced.
6. Remind owner to resubmit the sitemap in Google Search Console + Bing Webmaster.

## File inventory (~30 files)

- **New (7):** `docs/ice-2/index.html` + `docs/{zh-Hans,zh-Hant,ja,ko,es,fr}/ice-2/index.html`
- **Edited hubs (7):** `docs/index.html` + 6 localized `index.html`
- **Edited ClipMenu (7):** `docs/clipmenu/index.html` + 6 localized
- **Edited KeyKey (7):** `docs/keykey/index.html` + 6 localized
- **Edited shared/SEO (2):** `docs/shared/dragon.css`, `docs/sitemap.xml`
- Plus cache-bust touch-ups to `?v=` references.

## Out of scope

- Publishing the actual `ice-2` GitHub release and `homebrew-tap/Casks/ice-2.rb` cask (owner does
  this; the site links assume they will exist).
- Any change to `docs/appcast.xml`, `docs/CNAME`, `docs/appicon.png`.
- A real ice-2 app icon (placeholder glyph for now).
