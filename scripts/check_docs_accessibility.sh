#!/usr/bin/env bash

set -euo pipefail

readonly AXE_VERSION="4.12.1"
readonly DRIVER_MANAGER_VERSION="2.0.1"
readonly A11Y_PORT="8766"
readonly A11Y_BASE_URL="http://127.0.0.1:${A11Y_PORT}"

a11y_temp_dir="$(mktemp -d)"
a11y_server_pid=""

cleanup() {
  if [[ -n "${a11y_server_pid}" ]]; then
    kill "${a11y_server_pid}" 2>/dev/null || true
  fi
  rm -rf "${a11y_temp_dir}"
}
trap cleanup EXIT

driver_locations="$(
  npx --yes "browser-driver-manager@${DRIVER_MANAGER_VERSION}" which
)"
chrome_test_path="$(
  printf '%s\n' "${driver_locations}" |
    sed -n 's/^CHROME_TEST_PATH="\(.*\)"$/\1/p'
)"
chromedriver_test_path="$(
  printf '%s\n' "${driver_locations}" |
    sed -n 's/^CHROMEDRIVER_TEST_PATH="\(.*\)"$/\1/p'
)"

if [[ -z "${chrome_test_path}" || -z "${chromedriver_test_path}" ]]; then
  echo "Chrome for Testing is not installed." >&2
  echo \
    "Run: npx --yes browser-driver-manager@${DRIVER_MANAGER_VERSION} install chrome" \
    >&2
  exit 1
fi

uv run --locked python -m http.server "${A11Y_PORT}" --directory site \
  >"${a11y_temp_dir}/server.log" 2>&1 &
a11y_server_pid="$!"

for _ in {1..30}; do
  if curl --fail --silent "${A11Y_BASE_URL}/" >/dev/null; then
    break
  fi
  sleep 0.1
done

if ! curl --fail --silent "${A11Y_BASE_URL}/" >/dev/null; then
  cat "${a11y_temp_dir}/server.log" >&2
  exit 1
fi

npx --yes "@axe-core/cli@${AXE_VERSION}" \
  "${A11Y_BASE_URL}/" \
  "${A11Y_BASE_URL}/learn/python-basics/" \
  "${A11Y_BASE_URL}/learn/natural-numbers/" \
  "${A11Y_BASE_URL}/learn/integers/" \
  "${A11Y_BASE_URL}/learn/rationals/" \
  "${A11Y_BASE_URL}/learn/polynomials/" \
  "${A11Y_BASE_URL}/learn/algebraic-roots/" \
  "${A11Y_BASE_URL}/playground/" \
  "${A11Y_BASE_URL}/about/" \
  "${A11Y_BASE_URL}/reference/implementation/" \
  "${A11Y_BASE_URL}/en/" \
  "${A11Y_BASE_URL}/en/learn/python-basics/" \
  "${A11Y_BASE_URL}/en/learn/natural-numbers/" \
  "${A11Y_BASE_URL}/en/learn/integers/" \
  "${A11Y_BASE_URL}/en/learn/rationals/" \
  "${A11Y_BASE_URL}/en/learn/polynomials/" \
  "${A11Y_BASE_URL}/en/learn/algebraic-roots/" \
  "${A11Y_BASE_URL}/en/playground/" \
  "${A11Y_BASE_URL}/en/about/" \
  "${A11Y_BASE_URL}/en/reference/implementation/" \
  --tags wcag2a,wcag2aa,wcag21a,wcag21aa,wcag22aa,best-practice \
  --exit \
  --load-delay 1500 \
  --chrome-options='--headless=new' \
  --chrome-path="${chrome_test_path}" \
  --chromedriver-path="${chromedriver_test_path}"
