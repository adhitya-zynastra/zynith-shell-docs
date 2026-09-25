#!/usr/bin/env bash
# One A/B round: install the given binary, restart the shell identically, warm, measure.
set -uo pipefail
BIN="$1"; TAG="$2"; D=~/Documents/Dev/ZynithShell/scripts
DST=~/.local/opt/noctalia/bin/noctalia
# A running executable cannot be overwritten in place ("Text file busy"). Write alongside and
# rename: the running process keeps its inode, the next exec gets the new file.
cp "$BIN" "$DST.new" && mv -f "$DST.new" "$DST" || { echo "SWAP FAILED for $TAG" >&2; exit 3; }
cmp -s "$BIN" "$DST" || { echo "SWAP MISMATCH for $TAG" >&2; exit 3; }
OLD=$(pgrep -x noctalia|head -1); kill "$OLD"; sleep 1.5
pgrep -x noctalia >/dev/null || (setsid ~/.local/opt/noctalia/bin/noctalia >/dev/null 2>&1 &)
sleep 60
media=$(pactl list sink-inputs 2>/dev/null | awk '/^Sink Input/{c=""} /Corked:/{c=$2} /application.name/{if (c=="no" && $0 !~ /Noctalia/) k++} END{print k+0}')
RUN=$(readlink -f /proc/$(pgrep -x noctalia|head -1)/exe); cmp -s "$BIN" "$RUN" || { echo "RUNNING BINARY IS NOT $TAG" >&2; exit 4; }
echo "# $TAG version=$(~/.local/opt/noctalia/bin/noctalia --version|awk '{print $3}') media_playing=$media"
"$D/measure-cc-openclose.sh" "$TAG-openclose-a" 20 0.35; sleep 2
"$D/measure-cc-openclose.sh" "$TAG-openclose-b" 20 0.35; sleep 2
"$D/measure-cc.sh" "$TAG-complete-a" 30 0.45; sleep 2
"$D/measure-cc.sh" "$TAG-complete-b" 30 0.45
