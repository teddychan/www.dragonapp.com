# www.dragonapp.com

Source for **[www.dragonapp.com](https://www.dragonapp.com)** — the marketing
site for **Dragon App**, a small studio reviving beloved, discontinued macOS
apps as fast, native, open-source rebuilds.

This repo does **not** contain any app source. Each app is built in its own
repository; this repo only hosts:

1. **A marketing page per app** — one landing page each.
2. **The Sparkle appcast feeds** — the auto-update XML each app polls. These
   are written by each app's release CI, not by hand.

The site is served by **GitHub Pages from the [`docs/`](docs/) folder**.

## Apps

| App | Page | Source repo |
| --- | --- | --- |
| ClipMenu 2 | [/clipmenu-2/](https://www.dragonapp.com/clipmenu-2/) | [teddychan/clipmenu-2](https://github.com/teddychan/clipmenu-2) |
| Yahoo KeyKey 2 | [/yahoo-keykey-2/](https://www.dragonapp.com/yahoo-keykey-2/) | [teddychan/yahoo-keykey-2](https://github.com/teddychan/yahoo-keykey-2) |
| Ice 2 | [/ice-2/](https://www.dragonapp.com/ice-2/) | [teddychan/ice-2](https://github.com/teddychan/ice-2) |

[`docs/index.html`](docs/index.html) is the studio hub that links to all of
them. `/clipmenu/` and `/keykey/` are redirect stubs kept for old links.

## Layout

```
docs/                  ← published by GitHub Pages
  index.html           studio hub (app cards)
  <app>/index.html     one landing page per app
  <app>/appcast.xml    Sparkle update feed (written by each app's release CI)
  shared/dragon.css    shared design system (per-app accent via a <body> theme class)
  shared/*.js          consent banner + i18n runtime
  <locale>/            localized pages (es, fr, ja, ko, zh-Hans, zh-Hant)
  sitemap.xml, robots.txt, CNAME, favicons, app icons
i18n/                  localization build (build_i18n.py + templates/ + strings/*.json)
scripts/cache-bust.sh  fingerprints CSS/JS/images before publishing
```

## Editing

Edit files under `docs/` directly, commit, and push `main` (or open a PR and
merge) — GitHub Pages rebuilds automatically.

**Do not hand-edit** the `appcast.xml` files (managed by each app's release
CI), `docs/CNAME`, or the localized pages under `docs/<locale>/` (regenerated
by `i18n/build_i18n.py` from the templates and string tables).

Adding a new app = a new `docs/<app>/` folder, a card on the hub, plus updates
to `docs/sitemap.xml` and `docs/robots.txt` for the new URL.

## License

The site content, design, and brand assets are **© 2026 Teddy Chan, all
rights reserved** — see [LICENSE](LICENSE). The repo is public for
transparency, not for reuse. The apps marketed here are licensed separately in
their own repositories. See also [PRIVACY.md](PRIVACY.md).
