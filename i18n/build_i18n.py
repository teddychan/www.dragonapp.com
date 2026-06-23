#!/usr/bin/env python3
"""Dragon App i18n static-site generator.

Reads i18n/templates/*.html + i18n/strings/<lang>.json and writes localized
pages into docs/. English lives at the site root; each other language lives
under /<lang>/. Also (re)writes docs/sitemap.xml with hreflang alternates.

Run from the repo root:  python3 i18n/build_i18n.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STRINGS_DIR = os.path.join(ROOT, "i18n", "strings")
TEMPLATES_DIR = os.path.join(ROOT, "i18n", "templates")
DOCS = os.path.join(ROOT, "docs")
SITE = "https://www.dragonapp.com"

# Order matters: this is the order shown in the switcher and sitemap.
LANGS = ["en-US", "zh-Hans", "zh-Hant", "ja", "ko", "es", "fr"]

NATIVE = {
    "en-US": "English",
    "zh-Hans": "简体中文",
    "zh-Hant": "繁體中文",
    "ja": "日本語",
    "ko": "한국어",
    "es": "Español",
    "fr": "Français",
}
OG_LOCALE = {
    "en-US": "en_US",
    "zh-Hans": "zh_CN",
    "zh-Hant": "zh_HK",
    "ja": "ja_JP",
    "ko": "ko_KR",
    "es": "es_ES",
    "fr": "fr_FR",
}

# page key -> (template filename, page path within a language tree, output relpath)
PAGES = {
    "index":   ("index.html",   "",             "index.html"),
    "keykey":  ("keykey.html",  "keykey/",      os.path.join("keykey", "index.html")),
    "clipmenu":("clipmenu.html","clipmenu/",    os.path.join("clipmenu", "index.html")),
    "support": ("support.html", "support.html", "support.html"),
}
# sitemap priorities
PRIORITY = {"index": "1.0", "keykey": "0.8", "clipmenu": "0.9", "support": "0.5"}
LASTMOD = "2026-06-23"

GLOBE = ('<svg class="globe" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
         'stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M3 12h18"/>'
         '<path d="M12 3a15 15 0 0 1 0 18 15 15 0 0 1 0-18"/></svg>')

TOKEN_RE = re.compile(r"{{\s*([A-Za-z0-9_]+)\s*}}")


def lang_prefix(lang):
    return "" if lang == "en-US" else lang + "/"


def url_for(lang, page):
    return SITE + "/" + lang_prefix(lang) + PAGES[page][1]


def out_path(lang, page):
    return os.path.join(DOCS, lang_prefix(lang), PAGES[page][2])


def load_strings():
    data = {}
    for lang in LANGS:
        p = os.path.join(STRINGS_DIR, lang + ".json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                data[lang] = json.load(f)
    return data


def build_alternates(page):
    lines = []
    for l in LANGS:
        lines.append('  <link rel="alternate" hreflang="%s" href="%s">' % (l, url_for(l, page)))
    lines.append('  <link rel="alternate" hreflang="x-default" href="%s">' % url_for("en-US", page))
    return "\n".join(lines)


def build_switcher(current, page, common):
    label = common.get("switcher_label", "Language")
    out = []
    out.append('        <details class="lang-switch">')
    out.append('          <summary aria-label="%s">%s<span>%s</span></summary>'
               % (label, GLOBE, NATIVE[current]))
    out.append('          <div class="lang-menu">')
    for l in LANGS:
        active = ' class="active"' if l == current else ""
        aria = ' aria-current="true"' if l == current else ""
        out.append('            <a href="%s" hreflang="%s" data-setlang="%s"%s%s>%s</a>'
                   % (url_for(l, page), l, l, active, aria, NATIVE[l]))
    out.append('          </div>')
    out.append('        </details>')
    return "\n".join(out)


def render(template, lang, page, strings, missing):
    en = strings["en-US"]
    cur = strings.get(lang, en)
    page_str = cur.get(page, {})
    common = cur.get("common", {})
    en_page = en.get(page, {})
    en_common = en.get("common", {})

    specials = {
        "LANG": lang,
        "CANONICAL": url_for(lang, page),
        "OG_LOCALE": OG_LOCALE[lang],
        "ALTERNATES": build_alternates(page),
        "SWITCHER": build_switcher(lang, page, common if common else en_common),
        "URL_INDEX": url_for(lang, "index"),
        "URL_KEYKEY": url_for(lang, "keykey"),
        "URL_CLIPMENU": url_for(lang, "clipmenu"),
        "URL_SUPPORT": url_for(lang, "support"),
    }

    def repl(m):
        name = m.group(1)
        if name in specials:
            return specials[name]
        if name in page_str:
            return page_str[name]
        if name in common:
            return common[name]
        # fall back to English so the page never breaks; record the gap
        if name in en_page:
            missing.append((lang, page, name))
            return en_page[name]
        if name in en_common:
            missing.append((lang, page, name))
            return en_common[name]
        raise KeyError("Unknown token {{ %s }} in page '%s'" % (name, page))

    return TOKEN_RE.sub(repl, template)


def write_sitemap():
    XHTML = "http://www.w3.org/1999/xhtml"
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
                 'xmlns:xhtml="%s">' % XHTML)
    for page in ["index", "clipmenu", "keykey", "support"]:
        for lang in LANGS:
            lines.append("  <url>")
            lines.append("    <loc>%s</loc>" % url_for(lang, page))
            for alt in LANGS:
                lines.append('    <xhtml:link rel="alternate" hreflang="%s" href="%s"/>'
                             % (alt, url_for(alt, page)))
            lines.append('    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>'
                         % url_for("en-US", page))
            lines.append("    <lastmod>%s</lastmod>" % LASTMOD)
            lines.append("    <changefreq>monthly</changefreq>")
            lines.append("    <priority>%s</priority>" % PRIORITY[page])
            lines.append("  </url>")
    lines.append("</urlset>")
    with open(os.path.join(DOCS, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    strings = load_strings()
    if "en-US" not in strings:
        sys.exit("Missing i18n/strings/en-US.json")
    templates = {}
    for page, (tpl, _, _) in PAGES.items():
        with open(os.path.join(TEMPLATES_DIR, tpl), encoding="utf-8") as f:
            templates[page] = f.read()

    missing = []
    count = 0
    available = [l for l in LANGS if l in strings]
    for lang in available:
        for page in PAGES:
            html = render(templates[page], lang, page, strings, missing)
            dest = out_path(lang, page)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding="utf-8") as f:
                f.write(html)
            count += 1
    write_sitemap()

    print("Built %d pages for languages: %s" % (count, ", ".join(available)))
    if missing:
        # summarize per-language gaps (keys that fell back to English)
        per = {}
        for lang, page, key in missing:
            per.setdefault(lang, set()).add("%s.%s" % (page, key))
        for lang in sorted(per):
            print("  [fallback] %s missing %d keys -> used English" % (lang, len(per[lang])))
    only_en = [l for l in LANGS if l not in strings]
    if only_en:
        print("  [note] no translation file yet for: %s" % ", ".join(only_en))


if __name__ == "__main__":
    main()
