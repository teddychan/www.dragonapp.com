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
