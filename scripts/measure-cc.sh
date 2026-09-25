#!/usr/bin/env bash
# Cost of Control Center section navigation. Usage: measure-cc.sh <label> <switches> <dwell_s>
# dwell >= transition length -> complete legs; dwell < transition length -> retargets mid-flight.
set -uo pipefail
LABEL="$1"; N="${2:-30}"; DWELL="${3:-0.4}"
NOC="$HOME/.local/opt/noctalia/bin/noctalia"; HZ=$(getconf CLK_TCK)
P=$(pgrep -x noctalia | head -1); NI=$(pgrep -x niri | head -1)
cpu() { awk '{print $14+$15}' "/proc/$1/stat"; }
ctx() { local s=0 v; for f in /proc/"$1"/task/*/status; do v=$(awk '/ctxt_switches/{t+=$2} END{print t+0}' "$f" 2>/dev/null); s=$((s+v)); done; echo "$s"; }
S=(network bluetooth audio system weather calendar)
"$NOC" msg panel-open control-center home >/dev/null 2>&1; sleep 1.2
c0=$(cpu "$P"); n0=$(cpu "$NI"); x0=$(ctx "$P"); r0=$(awk '/VmRSS/{print $2}' /proc/"$P"/status)
for ((i=0;i<N;i++)); do "$NOC" msg panel-open control-center "${S[$((i % ${#S[@]}))]}" >/dev/null 2>&1; sleep "$DWELL"; done
sleep 0.6
c1=$(cpu "$P"); n1=$(cpu "$NI"); x1=$(ctx "$P"); r1=$(awk '/VmRSS/{print $2}' /proc/"$P"/status)
"$NOC" msg panel-toggle control-center >/dev/null 2>&1
printf '%s,%d,%s,%.1f,%.1f,%.0f,%+d\n' "$LABEL" "$N" "$DWELL" \
  "$(echo "($c1-$c0)*1000/$HZ/$N" | bc -l)" "$(echo "($n1-$n0)*1000/$HZ/$N" | bc -l)" \
  "$(echo "($x1-$x0)/$N" | bc -l)" "$((r1-r0))"
