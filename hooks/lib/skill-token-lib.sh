#!/usr/bin/env bash
# Shared library for HMAC-signed skill tokens.
# Sourced by skill-token-issuer.sh and by gate hooks.
#
# Token format: <nonce_hex>:<unix_ts>:<skill_name>:<hex_hmac_sha256>
# HMAC is computed over "<nonce>:<ts>:<skill>" with a 256-bit secret at
# ~/.keys/claude-skill-token-secret (sandbox-blocked for Read/Bash-cat in the
# main session; readable by hook scripts).

SKILL_TOKEN_SECRET_FILE="${SKILL_TOKEN_SECRET_FILE:-$HOME/.keys/claude-skill-token-secret}"
SKILL_TOKEN_DIR="${SKILL_TOKEN_DIR:-/tmp/claude/.skill-tokens}"
SKILL_TOKEN_TTL_SECONDS="${SKILL_TOKEN_TTL_SECONDS:-600}"
SKILL_TOKEN_FUTURE_TOLERANCE="${SKILL_TOKEN_FUTURE_TOLERANCE:-10}"

# ensure_secret SECRET_FILE
# Guarantees a non-empty 256-bit secret exists at SECRET_FILE, generating one on
# first use if absent. The secret is a LOCAL self-test HMAC key -- issuer and
# verifier are both local hook scripts that only need to share the same value, so
# auto-generating a random key is safe and makes the skill zero-setup ("easy for
# anyone to use"). Backward-compatible: if the file already exists and is
# non-empty, it is left untouched. Returns 0 if a usable secret is present.
ensure_secret() {
    local secret_file="$1"
    if [ -s "$secret_file" ]; then
        return 0
    fi
    local dir
    dir="$(dirname -- "$secret_file")"
    mkdir -p "$dir" 2>/dev/null || return 1
    chmod 700 "$dir" 2>/dev/null || true
    if command -v openssl >/dev/null 2>&1; then
        ( umask 077; openssl rand -hex 32 >"$secret_file" ) 2>/dev/null || return 1
    elif [ -r /dev/urandom ] && command -v od >/dev/null 2>&1; then
        ( umask 077; od -An -tx1 -N32 /dev/urandom | tr -d ' \n' >"$secret_file" ) 2>/dev/null || return 1
    else
        return 1
    fi
    chmod 600 "$secret_file" 2>/dev/null || true
    [ -s "$secret_file" ]
}


# issue_token SKILL_NAME [OVERRIDE_TS]
# Emits the token string on stdout. Returns 0 on success, non-zero on error.
# OVERRIDE_TS is for tests only.
issue_token() {
    local skill="$1"
    local override_ts="${2:-}"
    local secret_file="$SKILL_TOKEN_SECRET_FILE"
    if ! ensure_secret "$secret_file"; then
        return 10
    fi
    python3 - "$skill" "$secret_file" "$override_ts" <<'PYEOF'
import hmac, hashlib, secrets, time, sys
skill = sys.argv[1]
secret_file = sys.argv[2]
override_ts = sys.argv[3]
try:
    with open(secret_file, "rb") as f:
        secret = f.read().strip()
    if not secret:
        sys.exit(11)
    nonce = secrets.token_hex(16)
    ts = int(override_ts) if override_ts else int(time.time())
    msg = f"{nonce}:{ts}:{skill}".encode()
    sig = hmac.new(secret, msg, hashlib.sha256).hexdigest()
    print(f"{nonce}:{ts}:{skill}:{sig}")
    sys.exit(0)
except SystemExit:
    raise
except Exception:
    sys.exit(12)
PYEOF
}

# verify_token TOKEN EXPECTED_SKILL
# Returns 0 if valid, non-zero otherwise. Exit codes match the failure class
# and are surfaced for logging.
#   1 = malformed input
#   2 = expired
#   3 = timestamp too far in the future
#   4 = wrong skill
#   5 = HMAC mismatch
#   10 = secret file missing
#   11 = secret empty
verify_token() {
    local token="$1"
    local expected_skill="$2"
    local secret_file="$SKILL_TOKEN_SECRET_FILE"
    if ! ensure_secret "$secret_file"; then
        return 10
    fi
    python3 - "$token" "$expected_skill" "$secret_file" "$SKILL_TOKEN_TTL_SECONDS" "$SKILL_TOKEN_FUTURE_TOLERANCE" <<'PYEOF'
import hmac, hashlib, time, sys
token = sys.argv[1]
expected_skill = sys.argv[2]
secret_file = sys.argv[3]
ttl = int(sys.argv[4])
future_tol = int(sys.argv[5])
try:
    with open(secret_file, "rb") as f:
        secret = f.read().strip()
    if not secret:
        sys.exit(11)
    parts = token.strip().split(":")
    if len(parts) != 4:
        sys.exit(1)
    nonce, ts_str, skill, sig = parts
    if not nonce or not sig:
        sys.exit(1)
    try:
        ts = int(ts_str)
    except ValueError:
        sys.exit(1)
    now = int(time.time())
    if now - ts > ttl:
        sys.exit(2)
    if ts - now > future_tol:
        sys.exit(3)
    if skill != expected_skill:
        sys.exit(4)
    msg = f"{nonce}:{ts}:{skill}".encode()
    expected_sig = hmac.new(secret, msg, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_sig, sig):
        sys.exit(5)
    sys.exit(0)
except SystemExit:
    raise
except Exception:
    sys.exit(1)
PYEOF
}

# write_token_file SKILL SESSION_ID TOKEN
# Creates SKILL_TOKEN_DIR if needed, writes token to
# "<dir>/<skill>.<session_id>.token" with mode 600.
write_token_file() {
    local skill="$1"
    local session_id="$2"
    local token="$3"
    mkdir -p "$SKILL_TOKEN_DIR" 2>/dev/null || return 1
    local path="$SKILL_TOKEN_DIR/${skill}.${session_id}.token"
    umask 077
    printf '%s\n' "$token" >"$path" || return 1
    chmod 600 "$path" 2>/dev/null || true
    return 0
}

# read_token_file SKILL SESSION_ID
# Prints token to stdout if present; returns 1 if not found.
read_token_file() {
    local skill="$1"
    local session_id="$2"
    local path="$SKILL_TOKEN_DIR/${skill}.${session_id}.token"
    [ -f "$path" ] || return 1
    cat "$path"
}

# check_skill_grant SESSION_ID SKILL [SKILL ...]
# Succeeds (exit 0) if any listed skill has a valid token for this session.
# Prints the granting skill name on stdout on success; nothing on failure.
check_skill_grant() {
    local session_id="$1"
    shift
    local skill
    for skill in "$@"; do
        local tok
        if tok=$(read_token_file "$skill" "$session_id" 2>/dev/null); then
            if verify_token "$tok" "$skill" >/dev/null 2>&1; then
                printf '%s' "$skill"
                return 0
            fi
        fi
    done
    return 1
}
