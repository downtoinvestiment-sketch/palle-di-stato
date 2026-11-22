#!/bin/bash
# rifà senza mosso i fotogrammi attorno agli stacchi del 027, saltando quelli già rifatti (piu' nuovi del segnaposto)
cd /home/claude/pippo
FATTI=$(find t027/final -name 'f*.png' -newer t027/.inizio_tagli | sed -E 's#.*/f0*([0-9]+)\.png#\1#' | sort -n | tr '\n' ',')
echo "gia' rifatti: $FATTI"
cd scripts && FATTI="$FATTI" BLENDNAME=pippo_t027.blend timeout 540 /home/claude/venv/bin/python rifai_tagli.py t027 1080 1920 4 2>&1 | grep -c rifatto
