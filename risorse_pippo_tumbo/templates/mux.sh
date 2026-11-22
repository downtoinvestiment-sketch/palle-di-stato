#!/bin/bash
# Monta fotogrammi + audio + sottotitoli. Uso: bash templates/mux.sh NNN DURATA NOME   (dalla cartella del progetto)
T=$1; DUR=$2; NAME=$3; FONTS=${FONTS:-/usr/share/fonts/truetype/google-fonts}     # FONTS=assets/font per i font della libreria (Luckiest Guy, Bangers...)
mkdir -p out
ffmpeg -y -loglevel error -framerate 24 -start_number 1 -i t$T/final/f%04d.png -i audio/t$T.wav \
  -vf "scale=1080:1920:flags=lanczos,eq=saturation=1.18:contrast=1.03,ass=t$T/captions.ass:fontsdir=$FONTS" \
  -c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p -r 24 -c:a aac -b:a 192k -t $DUR -movflags +faststart out/$NAME.mp4 && ls -la out/$NAME.mp4
