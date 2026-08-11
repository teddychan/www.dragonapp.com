# i18n/tests/test_apps.py
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APPS = os.path.join(ROOT, "i18n", "apps")

REQUIRED = {"slug", "name", "theme", "repo", "homebrew_cask", "mas_url",
            "license", "license_url", "min_macos", "appcast_repo",
            "credit_name", "credit_url", "sponsors_url"}

def test_index_lists_apps():
    """The four shipping products, in hub order.

    dragon-sample-app is deliberately absent, and this assertion is the only thing that says so.
    It is a real Dragon app by every other measure — its own repository, exact vX.Y.Z tags, an
    app-owned appcast, a Homebrew cask — so someone auditing the family for missing pages will
    find it and read the omission as an oversight. It is not: per dragon-kit's
    docs/MAC-APP-RELEASE-LIFECYCLE.md its "purpose is to exercise DragonKit end to end", so its
    audience is the person writing the next Dragon app, not someone choosing a menu-bar app to
    install. A marketing page would be selling a reference fixture.

    Confirmed as a standing decision on 2026-08-11 rather than left implicit, because the failure
    this test produces when a fifth slug is added reads like a stale fixture and invites exactly
    the wrong repair. If a sample-app page is ever genuinely wanted, adding it is not done until
    SEO is: docs/sitemap.xml, docs/robots.txt, and the /seo pass.
    """
    idx = json.load(open(os.path.join(APPS, "_index.json")))
    assert idx == ["ice-2", "clipmenu-2", "yahoo-keykey-2", "spectacle-2"]

def test_each_app_has_required_fields():
    idx = json.load(open(os.path.join(APPS, "_index.json")))
    for slug in idx:
        data = json.load(open(os.path.join(APPS, slug + ".json")))
        assert REQUIRED <= set(data), "%s missing %s" % (slug, REQUIRED - set(data))
        assert data["slug"] == slug
