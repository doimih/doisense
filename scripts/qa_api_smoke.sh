#!/usr/bin/env sh
set -eu

# Smoke tests for a dedicated QA API endpoint.
# Usage examples:
#   API_BASE=https://qa-api.example.com/doisense/api ./scripts/qa_api_smoke.sh
#   API_BASE=... QA_EMAIL=user@example.com QA_PASSWORD=secret ./scripts/qa_api_smoke.sh

API_BASE=${API_BASE:-http://localhost:8000/api}
API_BASE=$(printf '%s' "$API_BASE" | sed 's#/*$##')
TMP_DIR=$(mktemp -d)
COOKIE_JAR="$TMP_DIR/cookies.txt"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

pass() {
  printf '[PASS] %s\n' "$1"
}

fail() {
  printf '[FAIL] %s\n' "$1" >&2
  exit 1
}

http_get() {
  url="$1"
  shift || true
  curl -sS -L -m 20 -o "$TMP_DIR/body.json" -w '%{http_code}' "$url" "$@"
}

http_post_json() {
  url="$1"
  json="$2"
  shift 2 || true
  curl -sS -L -m 20 -o "$TMP_DIR/body.json" -w '%{http_code}' \
    -H 'Content-Type: application/json' \
    -d "$json" \
    "$url" "$@"
}

printf 'QA API smoke target: %s\n' "$API_BASE"

# 1) Health check
status=$(http_get "$API_BASE/health")
[ "$status" = "200" ] || fail "Health endpoint expected 200, got $status"
if grep -q '"status"[[:space:]]*:[[:space:]]*"ok"' "$TMP_DIR/body.json"; then
  pass "Health endpoint is OK"
else
  fail "Health payload does not contain status=ok"
fi

# 2) Optional auth flow using credentials if provided
if [ -n "${QA_EMAIL:-}" ] && [ -n "${QA_PASSWORD:-}" ]; then
  login_payload=$(cat <<EOF
{"email":"$QA_EMAIL","password":"$QA_PASSWORD"}
EOF
)

  status=$(http_post_json "$API_BASE/auth/login" "$login_payload" -c "$COOKIE_JAR")
  [ "$status" = "200" ] || fail "Login expected 200, got $status"
  if grep -q '"access"' "$TMP_DIR/body.json"; then
    pass "Login returned access token"
  else
    fail "Login response missing access token"
  fi

  status=$(http_get "$API_BASE/me" -b "$COOKIE_JAR")
  [ "$status" = "200" ] || fail "GET /me expected 200, got $status"
  pass "Authenticated /me access is OK"

  status=$(http_post_json "$API_BASE/auth/refresh" '{}' -b "$COOKIE_JAR" -c "$COOKIE_JAR")
  [ "$status" = "200" ] || fail "Refresh expected 200, got $status"
  pass "Auth refresh via cookies is OK"

  status=$(http_post_json "$API_BASE/auth/logout" '{}' -b "$COOKIE_JAR" -c "$COOKIE_JAR")
  [ "$status" = "200" ] || fail "Logout expected 200, got $status"
  pass "Logout endpoint is OK"
else
  printf '[SKIP] Auth flow skipped (set QA_EMAIL and QA_PASSWORD to enable)\n'
fi

printf '\nAll enabled QA API smoke checks completed successfully.\n'
