# Dragon App website i18n

The marketing site is generated in seven languages from a single set of
templates + per-language string files. **Edit the source here, never the
generated HTML in `docs/`** (the generator overwrites it).

```
i18n/
  templates/*.html      HTML skeletons with {{ key }} placeholders
  strings/en.json       English — the source of truth (edit this first)
  strings/<lang>.json   one per language: zh-Hans zh-Hant ja ko es fr
  build_i18n.py         generator: templates + strings -> docs/
```

## Rebuild

```sh
python3 i18n/build_i18n.py
```

English is written to the site root (`docs/`); every other language to
`docs/<lang>/`. The generator also rewrites `docs/sitemap.xml` with hreflang
alternates. Language auto-detection + the switcher live in `docs/shared/i18n.js`.

## Add a string

1. Add the key + English text to `strings/en.json`.
2. Reference it as `{{ key }}` in the relevant template.
3. Add the translation to each `strings/<lang>.json` (missing keys fall back to
   English, and the build prints which keys fell back).
4. Run the generator.

## Add a language

Add its code to `LANGS`, `NATIVE`, and `OG_LOCALE` in `build_i18n.py`, drop a
`strings/<code>.json`, and rebuild.
