"""Scarica le bandiere di tutti i paesi (flag-icons, licenza MIT) e le converte in PNG per le palle di stato.
Uso: python3 strumenti/scarica_bandiere.py   -> modelli_satira/bandiere/{svg,png}/<codice>.(svg|png), paesi.json, LICENSE_flag-icons.txt"""
import os, json, urllib.request, cairosvg
QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(QUI, 'modelli_satira', 'bandiere')
BASE = 'https://raw.githubusercontent.com/lipis/flag-icons/main/'
def get(url): return urllib.request.urlopen(url, timeout=60).read()
os.makedirs(os.path.join(OUT, 'svg'), exist_ok=True); os.makedirs(os.path.join(OUT, 'png'), exist_ok=True)
paesi = json.loads(get(BASE + 'country.json'))
open(os.path.join(OUT, 'paesi.json'), 'w').write(json.dumps(paesi, ensure_ascii=False, indent=1))
open(os.path.join(OUT, 'LICENSE_flag-icons.txt'), 'wb').write(get(BASE + 'LICENSE'))
for p in paesi:
    c = p['code']; svg = os.path.join(OUT, 'svg', c + '.svg'); png = os.path.join(OUT, 'png', c + '.png')
    if not os.path.exists(svg): open(svg, 'wb').write(get(BASE + p['flag_4x3']))
    if not os.path.exists(png): cairosvg.svg2png(url=svg, write_to=png, output_width=1024, output_height=768)
print(len(paesi), 'bandiere')
