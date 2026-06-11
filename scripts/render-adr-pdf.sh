#!/usr/bin/env bash
# Render the 2-page Architecture & Strategy ADR to PDF (the challenge deliverable).
#
# Pipeline: Markdown -> HTML (uvx markdown_py) -> print-CSS wrapper -> PDF via a
# headless Chromium-family browser (Edge/Chrome/Chromium). No pandoc/LaTeX needed.
# The rendered PDF is committed; re-run this whenever the source .md changes.
#
# Usage: scripts/render-adr-pdf.sh [source.md] [out.pdf]
set -euo pipefail

SRC="${1:-docs/architecture/keystone-strategy.md}"
OUT="${2:-docs/architecture/keystone-strategy.pdf}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# 1) Markdown -> HTML body (tables + fenced code blocks for the ASCII diagram).
uvx --from markdown markdown_py -x tables -x fenced_code "$SRC" > "$TMP/body.html"

# 2) Wrap in a print-optimized HTML template tuned to fit two Letter pages.
cat > "$TMP/page.html" <<'HTML'
<!doctype html><html><head><meta charset="utf-8"><style>
@page { size: Letter; margin: 13mm 14mm; }
* { box-sizing: border-box; }
body { font-family: "Segoe UI", Arial, sans-serif; font-size: 10.3px; line-height: 1.34; color: #1a1a1a; margin: 0; }
h1 { font-size: 17px; margin: 0 0 2px; }
h2 { font-size: 12px; margin: 9px 0 3px; padding-bottom: 2px; border-bottom: 1px solid #ccc; page-break-after: avoid; }
p, li { margin: 2px 0; }
ul { margin: 2px 0 5px; padding-left: 16px; }
strong { color: #000; }
table { border-collapse: collapse; width: 100%; font-size: 9.6px; margin: 3px 0; }
th, td { border: 1px solid #bbb; padding: 2px 5px; text-align: left; vertical-align: top; }
th { background: #f0f0f0; }
pre { font-family: "Cascadia Mono", "Consolas", monospace; font-size: 7.4px; line-height: 1.15; background: #f6f8fa; border: 1px solid #ddd; border-radius: 4px; padding: 6px 8px; white-space: pre; overflow: hidden; page-break-inside: avoid; }
code { font-family: "Consolas", monospace; font-size: 9.4px; background: #f0f0f0; padding: 0 2px; border-radius: 2px; }
pre code { background: none; padding: 0; }
</style></head><body>
HTML
cat "$TMP/body.html" >> "$TMP/page.html"
printf '\n</body></html>\n' >> "$TMP/page.html"

# 3) Locate a headless Chromium-family browser.
BROWSER=""
for c in \
  "$(command -v msedge 2>/dev/null || true)" \
  "$(command -v google-chrome 2>/dev/null || true)" \
  "$(command -v chromium 2>/dev/null || true)" \
  "$(command -v chromium-browser 2>/dev/null || true)" \
  "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
  "/c/Program Files/Microsoft/Edge/Application/msedge.exe" \
  "/c/Program Files/Google/Chrome/Application/chrome.exe" \
  "/c/Program Files (x86)/Google/Chrome/Application/chrome.exe"; do
  if [ -n "$c" ] && [ -x "$c" ]; then BROWSER="$c"; break; fi
done
if [ -z "$BROWSER" ]; then
  echo "error: no Chromium-family browser found (Edge/Chrome/Chromium) to render the PDF." >&2
  exit 1
fi

# 4) Print to PDF. Resolve OUT to an absolute path first — a headless browser
# writes --print-to-pdf relative to its OWN cwd, not ours. cygpath keeps
# Windows-native browsers happy under Git Bash.
mkdir -p "$(dirname "$OUT")"
OUT_ABS="$(cd "$(dirname "$OUT")" && pwd)/$(basename "$OUT")"
if command -v cygpath >/dev/null 2>&1; then
  HTML_URI="file:///$(cygpath -w "$TMP/page.html")"
  OUT_ARG="$(cygpath -w "$OUT_ABS")"
else
  HTML_URI="file://$TMP/page.html"
  OUT_ARG="$OUT_ABS"
fi

"$BROWSER" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$OUT_ARG" "$HTML_URI" >/dev/null 2>&1 || \
"$BROWSER" --headless --disable-gpu \
  --print-to-pdf="$OUT_ARG" "$HTML_URI" >/dev/null 2>&1

echo "rendered $OUT"
