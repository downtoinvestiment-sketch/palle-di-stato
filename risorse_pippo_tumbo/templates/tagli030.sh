#!/bin/bash
# rifà senza mosso i fotogrammi attorno agli stacchi del 030, saltando quelli già rifatti (piu' nuovi del segnaposto t030/.inizio_tagli)
cd "$(dirname "$0")/.."
[ -f t030/.inizio_tagli ] || touch t030/.inizio_tagli
FATTI=$(find t030/final -name 'f*.png' -newer t030/.inizio_tagli | sed -E 's#.*/f0*([0-9]+)\.png#\1#' | sort -n | tr '\n' ',')
echo "gia' rifatti: $FATTI"
cd scripts && FATTI="$FATTI" BLENDNAME=pippo_t030.blend timeout ${1:-540} /home/claude/venv/bin/python rifai_tagli.py t030 1080 1920 3 2>&1 | grep -c rifatto
