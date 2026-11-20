#!/usr/bin/env bash
# Builds the eval PDF: pages 1-2 of NCERT Class 10 Science, Chapter 10 ("The Human Eye"),
# written to evals/docs/jesc110-p1-2.pdf. Only 2 pages, so ingest stays far under the free-tier
# embedding limit (each chunk counts as one request, 100 per minute).
# The PDF is copyrighted, so it is not in git. The full chapter is checked against docs.sha256.
# ncert.nic.in chains to Let's Encrypt "Root YE", which is not in system trust stores yet,
# so the cross-signed copy in certs/ is added to the bundle. TLS verification stays on.
#
# Usage: evals/fetch_docs.sh [local copy of jesc110.pdf]   (skips the download if given)
set -euo pipefail

cd "$(dirname "$0")"
excerpt="docs/jesc110-p1-2.pdf"
if [ -f "$excerpt" ]; then
  echo "skip $excerpt (already present)"
  exit 0
fi
mkdir -p docs

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

if [ $# -ge 1 ]; then
  cp "$1" "$work/jesc110.pdf"
else
  cat /etc/ssl/certs/ca-certificates.crt certs/isrg-root-ye-by-x2.pem > "$work/bundle.pem"
  echo "download jesc110.pdf"
  curl --fail --silent --show-error --location --cacert "$work/bundle.pem" \
    --output "$work/jesc110.pdf" "https://ncert.nic.in/textbook/pdf/jesc110.pdf"
fi

(cd "$work" && sha256sum --check "$OLDPWD/docs.sha256")

python="python"
venv_python="$(cd .. && pwd)/venv/bin/python"
[ -x "$venv_python" ] && python="$venv_python"
"$python" - "$work/jesc110.pdf" "$excerpt" <<'EOF'
import sys
from pypdf import PdfReader, PdfWriter

reader, writer = PdfReader(sys.argv[1]), PdfWriter()
for page in reader.pages[:2]:
    writer.add_page(page)
writer.write(sys.argv[2])
print(f"wrote {sys.argv[2]} (2 pages)")
EOF
