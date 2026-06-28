#!/usr/bin/env python3
"""Dragon App i18n static-site generator.

Reads i18n/templates/*.html + i18n/strings/<lang>.json and writes localized
pages into docs/. English lives at the site root; each other language lives
under /<lang>/. Also (re)writes docs/sitemap.xml with hreflang alternates.

Run from the repo root:  python3 i18n/build_i18n.py
"""
import json
import base64
import mimetypes
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STRINGS_DIR = os.path.join(ROOT, "i18n", "strings")
TEMPLATES_DIR = os.path.join(ROOT, "i18n", "templates")
DOCS = os.path.join(ROOT, "docs")
SITE = "https://www.dragonapp.com"
GA_ID = "G-FNQ1T94ESZ"

CONSENT_HEAD = (
    "  <!-- Google Consent Mode v2 (default denied); Google tag loads after consent. -->\n"
    "  <script>\n"
    "    window.dataLayer = window.dataLayer || [];\n"
    "    window.dragonGoogleAnalyticsId = '" + GA_ID + "';\n"
    "    function gtag(){dataLayer.push(arguments);}\n"
    "    gtag('consent', 'default', {\n"
    "      ad_storage: 'denied',\n"
    "      ad_user_data: 'denied',\n"
    "      ad_personalization: 'denied',\n"
    "      analytics_storage: 'denied',\n"
    "      functionality_storage: 'granted',\n"
    "      security_storage: 'granted',\n"
    "      wait_for_update: 500\n"
    "    });\n"
    "  </script>\n"
)

CONSENT_HEAD_EXTERNAL = (
    "  <!-- Google Consent Mode v2 (default denied); Google tag loads after consent. -->\n"
    "  <script>\n"
    "    window.dataLayer = window.dataLayer || [];\n"
    "    window.dragonGoogleAnalyticsId = '" + GA_ID + "';\n"
    "    function gtag(){dataLayer.push(arguments);}\n"
    "    gtag('consent', 'default', {\n"
    "      ad_storage: 'denied',\n"
    "      ad_user_data: 'denied',\n"
    "      ad_personalization: 'denied',\n"
    "      analytics_storage: 'denied',\n"
    "      functionality_storage: 'granted',\n"
    "      security_storage: 'granted',\n"
    "      wait_for_update: 500\n"
    "    });\n"
    "  </script>\n"
    "  <script src=\"/shared/consent.js\" defer></script>"
)

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
    "support": ("support.html", "support.html", "support.html"),
    "privacy": ("privacy.html", "privacy.html", "privacy.html"),
    "about":   ("about.html",   "about/",       os.path.join("about", "index.html")),
}

# pages built in every language (with hreflang/switcher) vs English-only standalone pages
I18N_PAGES = ["index", "support", "about", "privacy"]
EN_ONLY_PAGES = []
# sitemap priorities
PRIORITY = {"index": "1.0", "support": "0.5", "privacy": "0.3", "about": "0.6"}

# legacy app slugs (old URLs) -> current app slug they now redirect to
LEGACY_REDIRECTS = {"clipmenu": "clipmenu-2", "keykey": "yahoo-keykey-2"}
LASTMOD = "2026-06-23"

GLOBE = ('<svg class="globe" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
         'stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M3 12h18"/>'
         '<path d="M12 3a15 15 0 0 1 0 18 15 15 0 0 1 0-18"/></svg>')

TOKEN_RE = re.compile(r"{{\s*([A-Za-z0-9_]+)\s*}}")
ASSET_CACHE = {}


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


def read_asset(relpath):
    if relpath not in ASSET_CACHE:
        with open(os.path.join(DOCS, relpath), "r", encoding="utf-8") as f:
            ASSET_CACHE[relpath] = f.read()
    return ASSET_CACHE[relpath]


def data_uri(relpath):
    key = "data:" + relpath
    if key not in ASSET_CACHE:
        path = os.path.join(DOCS, relpath)
        mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("ascii")
        ASSET_CACHE[key] = "data:%s;base64,%s" % (mime, encoded)
    return ASSET_CACHE[key]


def inline_style(relpath):
    return "  <style>\n%s\n  </style>" % read_asset(relpath)


def inline_script(relpath, module=False):
    tag = 'script type="module"' if module else "script"
    return "  <%s>\n%s\n  </script>" % (tag, read_asset(relpath))


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
    out.append('          <summary aria-label="%s: %s">%s<span>%s</span></summary>'
               % (label, NATIVE[current], GLOBE, NATIVE[current]))
    out.append('          <div class="lang-menu">')
    for l in LANGS:
        active = ' class="active"' if l == current else ""
        aria = ' aria-current="true"' if l == current else ""
        out.append('            <a href="%s" hreflang="%s" data-setlang="%s"%s%s>%s</a>'
                   % (url_for(l, page), l, l, active, aria, NATIVE[l]))
    out.append('          </div>')
    out.append('        </details>')
    return "\n".join(out)


def build_app_menu(lang, strings):
    """A nav dropdown listing every app (+ the hub) so visitors can jump
    straight to an app. Reuses the .lang-switch / .lang-menu styling that
    already ships in dragon.css and the support page's inline CSS."""
    en_common = strings["en-US"].get("common", {})
    common = strings.get(lang, strings["en-US"]).get("common", {}) or en_common
    apps_label = common.get("nav_apps") or en_common.get("nav_apps", "Apps")
    all_label = common.get("nav_all_apps") or en_common.get("nav_all_apps", "All apps")
    chevron = ('<svg class="globe" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
               'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
               '<path d="m6 9 6 6 6-6"/></svg>')
    out = ['        <details class="lang-switch apps-switch">']
    out.append('          <summary aria-label="%s" aria-haspopup="true">%s<span>%s</span></summary>'
               % (apps_label, chevron, apps_label))
    out.append('          <div class="lang-menu">')
    out.append('            <a href="%s">%s</a>' % (SITE + "/" + lang_prefix(lang), all_label))
    for app in load_apps():
        out.append('            <a href="%s">%s</a>' % (app_url(lang, app["slug"]), app["name"]))
    out.append('          </div>')
    out.append('        </details>')
    return "\n".join(out)


def build_consent(common, en_common):
    def g(k):
        return common.get(k) or en_common.get(k, "")
    return (
        '  <div id="consent-banner" class="consent-banner" role="dialog" '
        'aria-label="Cookie consent preferences" aria-describedby="consent-text" hidden>\n'
        '    <div class="consent-inner">\n'
        '      <p class="consent-text" id="consent-text">%s</p>\n'
        '      <div class="consent-actions">\n'
        '        <button type="button" class="consent-btn consent-reject">%s</button>\n'
        '        <button type="button" class="consent-btn consent-accept">%s</button>\n'
        '      </div>\n'
        '    </div>\n'
        '  </div>'
    ) % (g("consent_message"), g("consent_reject"), g("consent_accept"))


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
        "APP_MENU": build_app_menu(lang, strings),
        "URL_INDEX": url_for(lang, "index"),
        "URL_SUPPORT": url_for(lang, "support"),
        "URL_ICE2": app_url(lang, "ice-2"),
        "URL_CLIPMENU2": app_url(lang, "clipmenu-2"),
        "URL_KEYKEY2": app_url(lang, "yahoo-keykey-2"),
        "ITEMLIST_JSONLD": render_itemlist(lang, strings),
        "CONSENT_HEAD": CONSENT_HEAD_EXTERNAL,
        "INDEX_CONSENT_HEAD": CONSENT_HEAD + "\n" + inline_script(os.path.join("shared", "consent.js")),
        "INLINE_DRAGON_CSS": inline_style(os.path.join("shared", "dragon.css")),
        "INLINE_I18N_JS": inline_script(os.path.join("shared", "i18n.js"), module=True),
        "APP_CARDS": render_app_cards(lang, strings),
        "CONSENT_BANNER": build_consent(common if common else en_common, en_common),
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


def render_itemlist(lang, strings):
    cur = strings.get(lang, strings["en-US"])
    items = []
    for i, app in enumerate(load_apps(), start=1):
        ps = cur.get(app["slug"], strings["en-US"].get(app["slug"], {}))
        items.append({"@type": "ListItem", "position": i, "name": app["name"],
                      "url": app_url(lang, app["slug"])})
    return json.dumps({"@context": "https://schema.org", "@type": "ItemList",
                       "itemListElement": items}, ensure_ascii=False, indent=2)


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


def _faq_safe(v):
    return v if isinstance(v, str) else ""  # faq lists feed render_jsonld, not text tokens


def build_app_switcher(current, slug, common):
    label = common.get("switcher_label", "Language")
    out = ['        <details class="lang-switch">',
           '          <summary aria-label="%s: %s">%s<span>%s</span></summary>' % (label, NATIVE[current], GLOBE, NATIVE[current]),
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
    common = {**en.get("common", {}), **(cur.get("common") or {})}
    en_common = en.get("common", {})

    specials = {
        "LANG": lang, "OG_LOCALE": OG_LOCALE[lang],
        "CANONICAL": app_url(lang, app["slug"]),
        "ALTERNATES": "\n".join(
            ['  <link rel="alternate" hreflang="%s" href="%s">' % (l, app_url(l, app["slug"])) for l in LANGS]
            + ['  <link rel="alternate" hreflang="x-default" href="%s">' % app_url("en-US", app["slug"])]),
        "SWITCHER": build_app_switcher(lang, app["slug"], common),
        "APP_MENU": build_app_menu(lang, strings),
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
        if name in specials:
            return specials[name]
        if name in page_str:
            return _faq_safe(page_str[name])
        if name in common:
            return common[name]
        if name in en.get(app["slug"], {}):
            missing.append((lang, app["slug"], name))
            return _faq_safe(en[app["slug"]][name])
        if name in en_common:
            missing.append((lang, app["slug"], name))
            return en_common[name]
        raise KeyError("Unknown token {{ %s }} in app '%s'" % (name, app["slug"]))

    return TOKEN_RE.sub(repl, template)


def _plain(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()


def write_llms_txt(strings):
    en = strings["en-US"]
    lines = ["# Dragon App", "",
             "> A small studio reviving beloved, discontinued macOS apps as free, open-source rebuilds.",
             "", "## Apps"]
    for app in load_apps():
        ps = en.get(app["slug"], {})
        lines.append("- [%s](%s): %s Install: brew install --cask %s"
                     % (app["name"], app_url("en-US", app["slug"]),
                        _plain(ps.get("sub", "")), app.get("homebrew_cask") or "n/a"))
    lines += ["", "## About", "%s/about/ — why these apps exist and the maintenance promise." % SITE]
    with open(os.path.join(DOCS, "llms.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def write_sitemap():
    XHTML = "http://www.w3.org/1999/xhtml"
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
                 'xmlns:xhtml="%s">' % XHTML)
    for page in I18N_PAGES:
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
    for page in EN_ONLY_PAGES:
        lines.append("  <url>")
        lines.append("    <loc>%s</loc>" % url_for("en-US", page))
        lines.append("    <lastmod>%s</lastmod>" % LASTMOD)
        lines.append("    <changefreq>yearly</changefreq>")
        lines.append("    <priority>%s</priority>" % PRIORITY[page])
        lines.append("  </url>")
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
        for page in I18N_PAGES:
            html = render(templates[page], lang, page, strings, missing)
            dest = out_path(lang, page)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding="utf-8") as f:
                f.write(html)
            count += 1
    # English-only standalone pages (e.g. privacy)
    for page in EN_ONLY_PAGES:
        html = render(templates[page], "en-US", page, strings, missing)
        dest = out_path("en-US", page)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(html)
        count += 1

    app_tpl = open(os.path.join(TEMPLATES_DIR, "app.html"), encoding="utf-8").read()
    for app in load_apps():
        for lang in available:
            html = render_app(app_tpl, app, lang, strings, missing)
            dest = os.path.join(DOCS, lang_prefix(lang), app["slug"], "index.html")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding="utf-8") as f:
                f.write(html)
            count += 1

    write_redirects()
    write_sitemap()
    write_llms_txt(strings)

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
