#!/usr/bin/env bash
# Controlled idle sample for noctalia + niri. See 03_Performance/baselines/idle-conditions.md
# for the conditions this assumes (no panel open, no audio, clean build, quiet workspace).
# Usage: measure-idle.sh [seconds] [label]
set -uo pipefail
DUR="${1:-60}"; LABEL="${2:-idle}"
HZ=$(getconf CLK_TCK)
P=$(pgrep -x noctalia | head -1); N=$(pgrep -x niri | head -1)
cpu() { awk '{print $14+$15}' "/proc/$1/stat"; }
ctx() { local s=0 v; for f in /proc/"$1"/task/*/status; do v=$(awk '/ctxt_switches/{t+=$2} END{print t+0}' "$f" 2>/dev/null); s=$((s+v)); done; echo "$s"; }
GPU=/sys/class/drm/card1/gt_act_freq_mhz
# pactl prints Corked: before application.name, so decide at the name line. Noctalia's own
# cue stream is always present and uncorked while idle; it is not media.
playing=$(pactl list sink-inputs 2>/dev/null | awk '/^Sink Input/{c=""} /Corked:/{c=$2} /application.name/{if (c=="no" && $0 !~ /Noctalia/) k++} END{print k+0}')
c0=$(cpu "$P"); n0=$(cpu "$N"); x0=$(ctx "$P"); t0=$(date +%s%N); g=0; k=0
end=$((SECONDS + DUR))
while [ $SECONDS -lt $end ]; do g=$((g + $(cat "$GPU" 2>/dev/null || echo 0))); k=$((k+1)); sleep 0.25; done
c1=$(cpu "$P"); n1=$(cpu "$N"); x1=$(ctx "$P"); t1=$(date +%s%N)
el=$(echo "scale=3;($t1-$t0)/1000000000" | bc)
printf '%s,%s,%s,%.2f,%.2f,%.1f,%s,%.0f,%s,%s,%s\n' "$LABEL" "$("$HOME/.local/opt/noctalia/bin/noctalia" --version | awk '{print $3}' | tr -d '()')" "$el" \
  "$(echo "($c1-$c0)*100/$HZ/$el" | bc -l)" "$(echo "($n1-$n0)*100/$HZ/$el" | bc -l)" \
  "$(awk '/VmRSS/{print $2/1024}' /proc/"$P"/status)" "$(ls /proc/"$P"/task | wc -l)" \
  "$(echo "($x1-$x0)/$el" | bc -l)" "$((g / (k>0?k:1)))" "$(swapon --show=USED --noheadings --bytes 2>/dev/null | awk '{s+=$1} END{printf "%.0f", s/1048576}')" "$playing"
