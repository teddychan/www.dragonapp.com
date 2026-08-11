import json, os, subprocess, sys
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

def test_hub_lists_all_apps():
    build()
    html = open(os.path.join(ROOT, "docs", "index.html")).read()
    for slug in ["ice-2", "clipmenu-2", "yahoo-keykey-2"]:
        assert "/%s/" % slug in html

# The licences links and sitemap entries started life hand-edited into docs/, where the
# next build deleted them. These two assert they are generated, so a build reproduces
# them instead — which is the only reason running this file is safe for them.
LICENSED = ["ice-2", "clipmenu-2", "yahoo-keykey-2"]

def test_licenses_link_in_every_locale_and_page_exists():
    build()
    for slug in LICENSED:
        assert os.path.exists(os.path.join(ROOT, "docs", slug, "licenses", "index.html")), slug
        for lang in ["", "zh-Hant/", "zh-Hans/", "ja/", "ko/", "es/", "fr/"]:
            html = open(os.path.join(ROOT, "docs", lang, slug, "index.html")).read()
            assert '<a href="/%s/licenses/">' % slug in html, (slug, lang)
    # spectacle-2 has no notices page, so it must not link one
    html = open(os.path.join(ROOT, "docs", "spectacle-2", "index.html")).read()
    assert "/licenses/" not in html

def test_footer_license_link_matches_app_json():
    """Every locale's footer "License" href is the app's own license_url.

    The href was hardcoded as {{ APP_REPO }}/blob/main/LICENSE, which 404s for spectacle-2 —
    its file is LICENSE.md — on all seven of its pages. license_url already held the right
    value for every app, because render_jsonld() has always used it for softwareLicense; the
    footer just wasn't reading it. Assert against the JSON rather than a literal so the next
    app whose licence is named anything else fails here instead of shipping a dead link.
    """
    build()
    idx = json.load(open(os.path.join(ROOT, "i18n", "apps", "_index.json")))
    for slug in idx:
        app = json.load(open(os.path.join(ROOT, "i18n", "apps", slug + ".json")))
        for lang in ["", "zh-Hant/", "zh-Hans/", "ja/", "ko/", "es/", "fr/"]:
            html = open(os.path.join(ROOT, "docs", lang, slug, "index.html")).read()
            assert '<a href="%s">License</a>' % app["license_url"] in html, (slug, lang)

def test_sitemap_includes_licenses_pages():
    build()
    sm = open(os.path.join(ROOT, "docs", "sitemap.xml")).read()
    for slug in LICENSED:
        assert "https://www.dragonapp.com/%s/licenses/" % slug in sm, slug
    assert "spectacle-2/licenses/" not in sm
