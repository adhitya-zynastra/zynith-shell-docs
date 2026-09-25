#!/usr/bin/env bash
# Control Center section-navigation stress, for the MorphTransition refactor (Phase 6A).
#
# Drives real section switches through the shell's own IPC and samples the process for the
# failure modes that matter after a transition refactor: growth that never comes back,
# animations that never settle, and surfaces or threads that accumulate per cycle.
#
# Deliberately NOT a pass/fail oracle — it prints a table and leaves the judgement to a human
# reading it next to the documented baseline. Usage:
#
#   stress-control-center.sh [cycles] [dwell_seconds]
#
# dwell is how long to leave each section selected. A dwell SHORTER than the transition
# duration (animNormal = 300 ms base, scaled by [shell.animation].speed) is the interesting
# case: it retargets mid-flight, which is the path the refactor changed.

set -uo pipefail

CYCLES="${1:-20}"
DWELL="${2:-0.12}"

NOC="${NOCTALIA_BIN:-$HOME/.local/opt/noctalia/bin/noctalia}"
SECTIONS=(network bluetooth audio media system weather calendar notifications power home)

pid() { pgrep -x noctalia | head -1; }
rss_kb() { awk '/VmRSS/{print $2}' "/proc/$1/status" 2>/dev/null; }
threads() { ls "/proc/$1/task" 2>/dev/null | wc -l; }
ctxsw() {
  local total=0 v
  for f in /proc/"$1"/task/*/status; do
    v=$(awk '/ctxt_switches/{s+=$2} END{print s+0}' "$f" 2>/dev/null)
    total=$((total + v))
  done
  echo "$total"
}
fds() { ls "/proc/$1/fd" 2>/dev/null | wc -l; }

P=$(pid)
if [ -z "$P" ]; then
  echo "noctalia is not running" >&2
  exit 1
fi

echo "Control Center navigation stress"
echo "  pid=$P  cycles=$CYCLES  dwell=${DWELL}s  sections=${#SECTIONS[@]}"
echo "  binary: $("$NOC" --version 2>/dev/null)"
echo

CORES_BEFORE=$(coredumpctl list --no-pager 2>/dev/null | grep -c noctalia || true)
printf '%-10s %10s %8s %10s %6s\n' phase rss_kb threads ctxsw fds
printf '%-10s %10s %8s %10s %6s\n' before "$(rss_kb "$P")" "$(threads "$P")" "$(ctxsw "$P")" "$(fds "$P")"

for ((c = 1; c <= CYCLES; c++)); do
  "$NOC" msg panel-open control-center home >/dev/null 2>&1
  sleep 0.2
  # Forward sweep, then an immediate reversal at each step: the reversal is what exercises
  # retarget-from-current-visual-state rather than a fresh leg.
  for s in "${SECTIONS[@]}"; do
    "$NOC" msg panel-open control-center "$s" >/dev/null 2>&1
    sleep "$DWELL"
  done
  for ((i = ${#SECTIONS[@]} - 1; i >= 0; i--)); do
    "$NOC" msg panel-open control-center "${SECTIONS[$i]}" >/dev/null 2>&1
    sleep "$DWELL"
  done
  # Close mid-transition: no dwell after the last switch.
  "$NOC" msg panel-open control-center audio >/dev/null 2>&1
  "$NOC" msg panel-toggle control-center >/dev/null 2>&1

  if ! P_NOW=$(pid) || [ -z "$P_NOW" ] || [ "$P_NOW" != "$P" ]; then
    echo >&2
    echo "SHELL DIED during cycle $c (pid was $P, now '${P_NOW:-none}')" >&2
    exit 2
  fi
  if ((c % 5 == 0 || c == CYCLES)); then
    printf '%-10s %10s %8s %10s %6s\n' "cycle $c" "$(rss_kb "$P")" "$(threads "$P")" "$(ctxsw "$P")" "$(fds "$P")"
  fi
done

# Let anything still animating settle, then sample again: growth that comes back is cache
# behaviour, growth that does not is the thing worth investigating.
sleep 3
printf '%-10s %10s %8s %10s %6s\n' settled "$(rss_kb "$P")" "$(threads "$P")" "$(ctxsw "$P")" "$(fds "$P")"

CORES_AFTER=$(coredumpctl list --no-pager 2>/dev/null | grep -c noctalia || true)
echo
echo "shell alive:      yes (pid $P, up $(ps -o etimes= -p "$P" | tr -d ' ')s)"
echo "noctalia cores:   before=$CORES_BEFORE after=$CORES_AFTER"
[ "$CORES_BEFORE" = "$CORES_AFTER" ] && echo "verdict:          no new coredumps" || echo "verdict:          NEW COREDUMP — investigate"
