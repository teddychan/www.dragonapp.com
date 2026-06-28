import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def test_about_pages_built():
    subprocess.run([sys.executable, "i18n/build_i18n.py"], cwd=ROOT, check=True)
    for lang in ["", "zh-Hant/", "ja/", "fr/"]:
        assert os.path.exists(os.path.join(ROOT, "docs", lang, "about", "index.html"))
