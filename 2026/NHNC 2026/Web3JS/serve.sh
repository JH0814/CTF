#!/bin/bash
# Per-connection handler: read one line of base64 from the client, decode it
# into run.js, and execute it with d8.
set -u

CHAL_DIR=/opt/chal
WORKDIR=$(mktemp -d /tmp/run.XXXXXX) || exit 1
cd "$WORKDIR" || exit 1
trap 'rm -rf "$WORKDIR"' EXIT

printf 'Send your base64-encoded d8 script on a single line:\n'

IFS= read -r LINE || exit 0
LINE=${LINE%$'\r'}

printf '%s' "$LINE" | base64 -d > run.js 2>/dev/null
if [ ! -s run.js ]; then
    printf 'error: input was not valid base64 (or was empty)\n'
    exit 1
fi

printf 'running...\n'
exec timeout 60 "$CHAL_DIR/d8" ./run.js
