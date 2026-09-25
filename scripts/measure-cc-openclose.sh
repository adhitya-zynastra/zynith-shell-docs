#!/usr/bin/env bash
# Cost of opening and closing the Control Center. Usage: measure-cc-openclose.sh <label> <cycles> <hold_s>
set -uo pipefail
LABEL="$1"; N="${2:-20}"; HOLD="${3:-0.35}"
NOC="$HOME/.local/opt/noctalia/bin/noctalia"; HZ=$(getconf CLK_TCK); P=$(pgrep -x noctalia | head -1)
cpu() { awk '{print $14+$15}' "/proc/$1/stat"; }
c0=$(cpu "$P"); r0=$(awk '/VmRSS/{print $2}' /proc/"$P"/status); t0=$(ls /proc/"$P"/task | wc -l)
for ((i=0;i<N;i++)); do "$NOC" msg panel-toggle control-center >/dev/null 2>&1; sleep "$HOLD"; "$NOC" msg panel-toggle control-center >/dev/null 2>&1; sleep "$HOLD"; done
sleep 1
c1=$(cpu "$P"); r1=$(awk '/VmRSS/{print $2}' /proc/"$P"/status); t1=$(ls /proc/"$P"/task | wc -l)
printf '%s,%d,%s,%.1f,%+d,%+d\n' "$LABEL" "$N" "$HOLD" "$(echo "($c1-$c0)*1000/$HZ/$N" | bc -l)" "$((r1-r0))" "$((t1-t0))"
