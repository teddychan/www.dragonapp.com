import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def test_legacy_redirects():
    subprocess.run([sys.executable, "i18n/build_i18n.py"], cwd=ROOT, check=True)
    for old, new in [("clipmenu", "clipmenu-2"), ("keykey", "yahoo-keykey-2")]:
        html = open(os.path.join(ROOT, "docs", old, "index.html")).read()
        assert "/%s/" % new in html
        assert 'http-equiv="refresh"' in html
        assert "canonical" in html
