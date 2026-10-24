#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p sources56
while read -r _ file; do
  curl --fail --location --retry 3 "https://packages.sury.org/php/pool/main/p/php5.6/$file" -o "sources56/$file"
done < sources56.sha256
(cd sources56 && shasum -a 256 -c ../sources56.sha256)
