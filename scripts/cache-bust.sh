#!/usr/bin/env bash
# Stamp ?v=<contenthash> onto cache-busted assets across all docs/**/*.html.
# Run before committing/deploying. Idempotent: re-run anytime; only changed
# files get a new hash. GitHub Pages caps headers at max-age=600, so the
# fingerprint is the only reliable way to force browsers off stale CSS/JS/img.
set -euo pipefail
cd "$(dirname "$0")/.."

# URL paths to fingerprint (file lives at docs<path>).
ASSETS="/shared/dragon.css /shared/consent.js /shared/i18n.js /appicon.png /keykey/appicon.png"

HTML=()
while IFS= read -r f; do HTML+=("$f"); done < <(find docs -name '*.html')

for p in $ASSETS; do
  f="docs$p"
  [ -f "$f" ] || { echo "skip (missing): $f" >&2; continue; }
  h=$(shasum -a 256 "$f" | cut -c1-8)
  P="$p" H="$h" perl -pi -e \
    's{(href|src)="\Q$ENV{P}\E(\?v=[0-9a-f]+)?"}{$1.q{="}.$ENV{P}.q{?v=}.$ENV{H}.q{"}}ge' \
    "${HTML[@]}"
  echo "$p -> $h"
done
