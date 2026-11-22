#!/bin/bash
# rifà senza mosso i fotogrammi attorno agli stacchi del 028, saltando quelli già rifatti (piu' nuovi del segnaposto t028/.inizio_tagli)
cd "$(dirname "$0")/.."
[ -f t028/.inizio_tagli ] || touch t028/.inizio_tagli
FATTI=$(find t028/final -name 'f*.png' -newer t028/.inizio_tagli | sed -E 's#.*/f0*([0-9]+)\.png#\1#' | sort -n | tr '\n' ',')
echo "gia' rifatti: $FATTI"
cd scripts && FATTI="$FATTI" BLENDNAME=pippo_t028.blend timeout ${1:-540} /home/claude/venv/bin/python rifai_tagli.py t028 1080 1920 3 2>&1 | grep -c rifatto
