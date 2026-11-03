# i18n/tests/test_build.py
import importlib.util
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_spec = importlib.util.spec_from_file_location("build_i18n", os.path.join(ROOT, "i18n", "build_i18n.py"))
BUILD = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(BUILD)

def run_build():
    return subprocess.run(
        [sys.executable, "i18n/build_i18n.py"],
        cwd=ROOT, capture_output=True, text=True
    )

def test_build_runs_clean():
    r = run_build()
    assert r.returncode == 0, r.stderr
    assert "Built" in r.stdout
    assert "Traceback" not in r.stderr

def test_known_pages_exist():
    run_build()
    for rel in ["docs/index.html", "docs/zh-Hant/index.html", "docs/support.html"]:
        assert os.path.exists(os.path.join(ROOT, rel)), rel

def _keys(table, prefix=""):
    out = set()
    for k, v in table.items():
        if isinstance(v, dict):
            out |= _keys(v, prefix + k + ".")
        else:
            out.add(prefix + k)
    return out

def test_every_language_has_every_english_key():
    """A key missing from a locale renders English there without failing the build.

    render_app() merges each locale's common table over English, so a missing
    common key does not even reach the build's [fallback] report.
    """
    strings = BUILD.load_strings()
    english = _keys(strings["en-US"]) - {"_lang"}
    for lang in BUILD.LANGS:
        assert lang in strings, lang
        assert english <= _keys(strings[lang]), (lang, sorted(english - _keys(strings[lang])))

def test_the_build_reports_no_fallback():
    r = run_build()
    assert r.returncode == 0, r.stderr
    assert "[fallback]" not in r.stdout, r.stdout
    assert "[note]" not in r.stdout, r.stdout
    assert ("languages: %s" % ", ".join(BUILD.LANGS)) in r.stdout, r.stdout

def test_every_page_and_sitemap_entry_exists_in_every_language():
    run_build()
    sitemap = open(os.path.join(ROOT, "docs", "sitemap.xml")).read()
    slugs = json.load(open(os.path.join(ROOT, "i18n", "apps", "_index.json")))
    for lang in BUILD.LANGS:
        urls = [BUILD.url_for(lang, p) for p in BUILD.I18N_PAGES]
        urls += [BUILD.app_url(lang, s) for s in slugs]
        for url in urls:
            rel = url[len(BUILD.SITE) + 1:]
            path = os.path.join(ROOT, "docs", rel, "index.html") if rel.endswith("/") or rel == "" \
                else os.path.join(ROOT, "docs", rel)
            assert os.path.exists(path), path
            assert "<loc>%s</loc>" % url in sitemap, url
            assert 'hreflang="%s" href="%s"' % (lang, url) in open(path).read(), (path, lang)

def test_the_browser_runtime_knows_every_built_language():
    """docs/shared/i18n.js keeps its own copy of LANGS for redirects and the switcher.

    A language missing there is built and listed, but never auto-selected for a
    visitor whose browser asks for it.
    """
    js = open(os.path.join(ROOT, "docs", "shared", "i18n.js")).read()
    runtime = json.loads(re.search(r"var LANGS = (\[[^\]]*\]);", js).group(1))
    assert runtime == BUILD.LANGS
