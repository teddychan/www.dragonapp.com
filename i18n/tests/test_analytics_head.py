import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS = os.path.join(ROOT, "docs")

GOOGLE_TAG = "dragonGoogleAnalyticsId"
PRECONNECT = '<link rel="preconnect" href="https://www.googletagmanager.com">'


def all_html():
    for dirpath, _, names in os.walk(DOCS):
        for n in names:
            if n.endswith(".html"):
                yield os.path.join(dirpath, n)


def test_every_analytics_page_preconnects_to_googletagmanager():
    """consent.js loads gtag from googletagmanager.com, so every page that
    bootstraps the Google tag needs the preconnect. Covers the hand-written
    pages under docs/ too, not just the generated ones."""
    subprocess.run([sys.executable, "i18n/build_i18n.py"], cwd=ROOT, check=True)
    checked = 0
    for p in all_html():
        html = open(p, encoding="utf-8").read()
        if GOOGLE_TAG not in html:
            continue  # e.g. the legacy redirect stubs, which load no analytics
        checked += 1
        assert PRECONNECT in html, os.path.relpath(p, ROOT)
    assert checked > 50, checked  # the marker moved; the loop above proved nothing
