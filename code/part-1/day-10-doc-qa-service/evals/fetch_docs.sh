#!/usr/bin/env bash
# Downloads the eval PDFs (NCERT Class 10 Science, chapters 9 to 11) into evals/docs/
# and checks them against docs.sha256. The PDFs are copyrighted, so they are not in git.
# ncert.nic.in chains to Let's Encrypt "Root YE", which is not in system trust stores yet,
# so the cross-signed copy in certs/ is added to the bundle. TLS verification stays on.
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p docs

bundle="$(mktemp)"
trap 'rm -f "$bundle"' EXIT
cat /etc/ssl/certs/ca-certificates.crt certs/isrg-root-ye-by-x2.pem > "$bundle"

for chapter in jesc109 jesc110 jesc111; do
  file="docs/$chapter.pdf"
  if [ -f "$file" ]; then
    echo "skip $file (already present)"
    continue
  fi
  echo "download $file"
  curl --fail --silent --show-error --location --cacert "$bundle" \
    --output "$file.part" "https://ncert.nic.in/textbook/pdf/$chapter.pdf"
  mv "$file.part" "$file"
done

(cd docs && sha256sum --check ../docs.sha256)
