#!/usr/bin/env bash
# Build every documentation artifact from the canonical Markdown.
#   1. audit the docs against the live repository (fails the build on a broken reference)
#   2. regenerate charts from the benchmark CSVs
#   3. regenerate the SVG diagrams and rasterise them for embedding
#   4. compile the master report to DOCX and PDF
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd .. && pwd)"

echo "==> audit"
python3 audit-docs.py

echo "==> charts"
python3 generate-charts.py

echo "==> diagrams"
python3 generate-diagrams.py
for f in "$ROOT"/07_Assets/diagrams/*.svg; do
  magick -density 170 "$f" -background white -alpha remove "${f%.svg}.png"
done

echo "==> master report"
python3 build-docx.py
python3 build-pdf.py

echo
echo "artifacts:"
ls -la "$ROOT/99_Reports/generated/" | awk 'NR>3 {printf "  %8.1f KB  %s\n", $5/1024, $9}'
