#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

port="${PORT:-1313}"
bind="${BIND:-127.0.0.1}"
drafts="${DRAFTS:-0}"
version="$(tr -d '\r\n' < .hugo-version)"
local_hugo=".tools/hugo-${version}/hugo"

if [[ -x "$local_hugo" ]]; then
  hugo_bin="$local_hugo"
elif command -v hugo >/dev/null 2>&1; then
  hugo_bin="$(command -v hugo)"
else
  echo "Hugo ${version} was not found. Installing the pinned Linux x86_64 release..." >&2
  RUNNER_TEMP="${RUNNER_TEMP:-$PWD/.tools}" scripts/install-hugo.sh
  hugo_bin="$local_hugo"
fi

base_url="http://${bind}:${port}/"
args=(server --bind "$bind" --baseURL "$base_url" --port "$port" --disableFastRender)
if [[ "$drafts" == "1" || "$drafts" == "true" ]]; then
  args+=(-D)
fi

echo "Serving Edge Systems Lab at ${base_url}"
exec "$hugo_bin" "${args[@]}"
