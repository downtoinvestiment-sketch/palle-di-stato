#!/bin/bash
# rifà senza mosso i fotogrammi attorno agli stacchi del 026, saltando quelli già rifatti (piu' nuovi del segnaposto)
cd /home/claude/pippo
FATTI=$(find t026/final -name 'f*.png' -newer t026/.inizio_tagli | sed -E 's#.*/f0*([0-9]+)\.png#\1#' | sort -n | tr '\n' ',')
echo "gia' rifatti: $FATTI"
cd scripts && FATTI="$FATTI" BLENDNAME=pippo_t026.blend timeout 540 /home/claude/venv/bin/python rifai_tagli.py t026 1080 1920 4 2>&1 | grep -c rifatto
