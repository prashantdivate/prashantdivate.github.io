#!/usr/bin/env bash
# CI installer for a checksum-pinned, official Linux x86_64 Hugo release.
set -euo pipefail
cd "$(dirname "$0")/.."
version="$(tr -d '\r\n' < .hugo-version)"
expected='45228f5a52eb118b0ca168068f01d7df0447314a24056f1d29667ed9fc368308'
if [[ "$version" != '0.166.0' ]]; then
  echo 'Update both .hugo-version and the verified checksum in scripts/install-hugo.sh.' >&2
  exit 1
fi
if [[ "$(uname -s)" != 'Linux' || "$(uname -m)" != 'x86_64' ]]; then
  echo 'This CI installer supports Linux x86_64 only. See README for other platforms.' >&2
  exit 1
fi
target="${RUNNER_TEMP:-$PWD/.tools}/hugo-${version}"
mkdir -p "$target"
archive="$target/hugo.tar.gz"
curl --fail --location --retry 3 --connect-timeout 20 \
  "https://github.com/gohugoio/hugo/releases/download/v${version}/hugo_${version}_linux-amd64.tar.gz" \
  --output "$archive"
printf '%s  %s\n' "$expected" "$archive" | sha256sum --check --status
tar -xzf "$archive" -C "$target" hugo
chmod +x "$target/hugo"
"$target/hugo" version
if [[ -n "${GITHUB_PATH:-}" ]]; then
  printf '%s\n' "$target" >> "$GITHUB_PATH"
else
  printf '\nInstalled at %s/hugo\nAdd this directory to PATH for local use.\n' "$target"
fi
