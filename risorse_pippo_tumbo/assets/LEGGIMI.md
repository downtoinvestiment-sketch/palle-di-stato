# Libreria asset Pippo e Tumbo

Asset gratuiti da usare nelle scene Blender di Pippo e Tumbo, in due stili: realistici (alberi, piante, rocce, oggetti, materiali, cieli HDRI che illuminano la scena come una foto vera, modelli veri della NASA) e cartoon leggerissimi (case, alberi, auto, mobili, cibo, personaggi già animati). Più effetti (fumo, botti, schizzi, faccine, luci) e font per i sottotitoli.

Tutto viene da **Poly Haven**, **ambientCG**, **Kenney** e **KayKit** con licenza **CC0**: uso commerciale libero, nessun obbligo di citazione. I modelli **NASA** sono senza copyright; la NASA chiede solo di non far sembrare che sponsorizzi il video. I font sono CC0 (Kenney) oppure con licenza libera SIL OFL / Apache (Google Fonts): si possono usare nei video anche a pagamento.

## Cosa c'è

| Tipo | Quanti | Dove |
|---|---|---|
| Modelli 3D realistici | 556 (522 Poly Haven + 34 cibi ambientCG) | `modelli/`, `ambientcg/` |
| Modelli 3D cartoon | 4.451 in 46 pacchetti Kenney (285 pezzi di case ed edifici, 127 alberi, auto, mobili, cibo...) | `kenney/` |
| Modelli 3D cartoon più morbidi | 903 in 10 pacchetti KayKit (città, mobili, cucina e cibo, Halloween, base spaziale, dungeon, medioevo, 9 personaggi con 76 animazioni pronte) | `kaykit/` |
| Modelli veri della NASA | 257 (astronauti e tute, Saturn V, Shuttle, modulo lunare, rover, Hubble, stazione spaziale, satelliti, attrezzi) | `nasa/` |
| Texture / materiali PBR a 1K | 3.101 (870 Poly Haven + 2.231 ambientCG, cioè tutti i materiali di ambientCG più decalcomanie e atlanti di foglie) | `texture/`, `ambientcg/` |
| Cieli HDRI a 1K | 1.436 (997 Poly Haven, di cui 83 anche in 4K, + 439 ambientCG) | `hdri/`, `ambientcg/` |
| Sagome di alberi e piante con sfondo trasparente | 152 (gli alberi anche visti da tre lati) | `alberi_cartonati/` |
| Effetti: immagini con sfondo trasparente | 374 (80 particelle, 9 esplosioni, 9 lampi, 9 nuvolette verdi, 25 sbuffi bianchi, 25 fumi neri, 36 schizzi, 29 faccine, 152 forme di luce) | `effetti/` |
| Font per sottotitoli e titoli | 28 | `font/` |

`scarica-tutto` riprende tutti i materiali; le 191 decalcomanie e atlanti di foglie si scaricano da soli la prima volta che li usi per nome.

La libreria completa pesa circa 22 GB, quindi non viaggia dentro questo zip (effetti, font e sagome invece sì, sono piccoli): **si ricostruisce da sola** in qualunque sessione con un comando (qualche minuto, dipende dalla rete), oppure scarica solo quello che serve al momento dell'uso.

## Modelli cartoon (Kenney)

- Si usano come gli altri: `A.modello('kenney/city-kit-suburban/building-type-a', posizione=(12, 0, 0), altezza=7.5, rotazione=-90)`.
- Sono piccoli di loro (una casa è alta circa 1): indica sempre `altezza=` in metri.
- La facciata guarda verso -Y: con `rotazione=-90` guarda verso -X, con `rotazione=90` verso +X.
- Pesano pochissimo: in media 296 triangoli a modello (la casa di esempio 1.174, un albero 196). La via di `esempio_quartiere.py`, con 21 tipi di casa e 12 di albero, si renderizza in circa 10 secondi a fotogramma a 1080×1920.
- Per cercarli: `python pt_assets.py cerca casa --origine kenney`, oppure il filtro «Cartoon» nel catalogo visivo.

## Modelli cartoon KayKit

- Id `kaykit/<pacchetto>/<nome>`: `A.modello('kaykit/city-builder-bits/car_taxi', posizione=(2, 0, 0), altezza=1.5)`. Anche qui indica sempre `altezza=`.
- Vengono appoggiati a terra da soli (molti hanno l'origine a metà altezza). Per i pezzi da incastrare tra loro (tessere esagonali, muri del dungeon) passa `appoggia=False`.
- Pacchetti: `city-builder-bits` (palazzi, auto, semafori, idranti), `furniture-bits`, `restaurant-bits` (cucina e cibo, 144 pezzi), `halloween-bits`, `space-base-bits`, `prototype-bits`, `dungeon-remastered`, `medieval-hexagon-pack` (case e castelli in 4 colori), `character-pack-adventures`, `character-pack-skeletons`.
- **Personaggi già animati** (Knight, Mage, Barbarian, Rogue, Rogue_Hooded e 4 scheletri: Skeleton_Mage, Skeleton_Minion, Skeleton_Rogue, Skeleton_Warrior): hanno 76 animazioni pronte.

```python
cav = A.modello('kaykit/character-pack-adventures/Knight', posizione=(0, 0, 0), altezza=1.8)
A.animazioni(cav)                                  # elenco: Idle, Walking_A, Running_A, Cheer, Sit_Floor_Idle, Lie_Idle, Throw, Death_A...
A.anima(cav, 'Walking_A', inizio=1, ripeti=4)      # cammina dal fotogramma 1, quattro passi di fila
A.anima(cav, 'Cheer', inizio=97)                   # poi esulta
A.accessori(cav)                                   # cosa può tenere in mano: 1H_Sword, Round_Shield...
A.accessori(cav, '1H_Sword', 'Round_Shield')       # mostra questi (di partenza ha le mani vuote)
```

  Di partenza il personaggio è nella posa di riposo (`Idle`). Gli scheletri hanno 95 animazioni. `anima()` e `animazioni()` funzionano anche con i personaggi Kenney (`kenney/mini-characters/...`, 32 animazioni: `idle`, `walk`, `sprint`, `jump`, `sit`, `die`, `emote-yes`...). Le durate vengono convertite ai fotogrammi al secondo della scena nel momento in cui carichi il personaggio: imposta prima `scene.render.fps`.
- Si scaricano da GitHub con `git` (70 MB in tutto), un pacchetto alla volta al primo uso.

## Modelli veri della NASA

- Id `nasa/<nome>`: `A.modello('nasa/astronaut', posizione=(0, -3, 0), altezza=1.9, max_triangoli=40000)`.
- Le misure dei file non sono in metri (l'astronauta è «alto» 74, il Saturn V 13): `altezza=` è obbligatoria. Il modello viene centrato su `posizione` e appoggiato a terra da solo.
- Alcuni sono molto pesanti (la stazione spaziale ha 2,7 milioni di triangoli, la metà dei modelli ne ha più di 23.000): usa `max_triangoli=` per alleggerirli. I triangoli di ognuno sono nel catalogo.
- 221 su 257 sono compressi in un formato (Draco) che il Blender installato con pip non sa aprire: il kit li riscrive in formato normale la prima volta che li usi. Serve il pacchetto Python `DracoPy`, che il kit prova a installare da solo.
- Per cercarli: `python pt_assets.py cerca razzo --origine nasa`, oppure «Spazio (NASA)» nel catalogo visivo.

## Un modello tuo

`A.modello('/percorso/file.glb', altezza=2)` apre anche un file che non è nel catalogo (glb, gltf, fbx, obj): basta caricarlo in chat o metterlo nel repository. Serve per i pacchetti che vanno scaricati a mano (vedi «Cosa non è entrato»).

## Effetti

Immagini piatte con sfondo trasparente che brillano di luce propria e guardano sempre la camera. Stanno in `effetti/<gruppo>/`; l'elenco si ottiene con `A.effetti()` o `python pt_assets.py effetti fumo`.

```python
A.effetto('esplosione/explosion03', posizione=(0, 0, 1.5), larghezza=2.6, luce=2.0)        # botto fermo
A.effetto('esplosione/explosion03', posizione=(0, 0, 1.5), larghezza=2.6, animazione=(40, 14))  # compare al fotogramma 40, si allarga e svanisce in 14
A.effetto('fumo_nero/blacksmoke05', posizione=(0, 0.2, 3), larghezza=2.2)
A.effetto('emoticon/hearts', posizione=(1, 0, 2.2), larghezza=0.45)                         # faccina sopra la testa
A.effetto('particelle/star_05', posizione=(0, 0, 2.5), larghezza=0.8, colore=(1, 0.85, 0.1), luce=3)
A.effetto('schizzi/splat07', posizione=(0, -2, 0.02), larghezza=1.6, colore=(0.9, 0.1, 0.5), verso_camera=False).rotation_euler = (0, 0, 0.4)   # macchia stesa a terra
```

- Particelle, schizzi e forme di luce sono bianchi: si tingono con `colore=`. Esplosioni, fumo, nuvolette verdi e faccine hanno già i loro colori.
- L'oggetto restituito si sposta e si anima come gli altri; l'opacità sta in `oggetto.color[3]`.
- **Costo misurato** (scena di prova a 1080×1920, 6 campioni, 8 effetti grandi in vista): con i bordi morbidi (`sfumato=True`, di default) il fotogramma passa da 20,0 a 24,9 secondi; con `sfumato=False` resta a 19,5 ma fumo e botti hanno i bordi granulosi. Gli effetti durano pochi fotogrammi, quindi conviene tenerli morbidi.
- Non proiettano ombra.

## Font

28 font in `font/`: `A.font()` dà l'elenco, `A.font('luckiest')` il percorso del file. Nei sottotitoli ASS si usa il nome della famiglia e a `ffmpeg` si passa `fontsdir=assets/font`.

| Famiglia (nome da scrivere nello stile ASS) | Carattere |
|---|---|
| Poppins (Black, ExtraBold) | quello usato finora nei sottotitoli |
| Luckiest Guy, Bangers, Carter One, Chewy | fumetto |
| Titan One, Lilita One, Bowlby One, Sigmar, Modak, Rubik Mono One | grassi e tondi, da titolo |
| Anton | stretto e alto, da meme |
| Fredoka, Baloo 2, DynaPuff | morbidi, ma sottili nella versione di base |
| Kenney Blocks, Future, High, Mini, Pixel, Rocket (12 file) | da videogioco |

## Cosa non è entrato

- **Smithsonian (scansioni 3D di dinosauri e reperti):** i file si scaricano, ma dentro c'è scritto «tutti i diritti riservati» e la pagina che dice quali sono liberi non si lascia leggere in automatico. Senza una conferma modello per modello sono rimasti fuori.
- **Quaternius (animali e personaggi cartoon, CC0):** il suo sito manda a itch.io, che vieta ai programmi di scaricare. OpenGameArt, che ne ha una copia, vieta l'accesso a Claude. Si possono scaricare a mano da quaternius.com e caricare in chat: il kit li apre con `A.modello('/percorso/file.gltf')`.
- **Suoni dei meme:** restano fuori per il diritto d'autore.

## Come si usa in una nuova sessione

1. Copia la cartella del kit dove lavori (per esempio `/home/claude/pippo/assets/`).
2. Negli script delle scene:

```python
import sys; sys.path.insert(0, '/home/claude/pippo/assets')
import pt_assets as A

A.qualita_eevee(preset='equilibrato')                 # 1080x1920, 6 campioni, riflessi, ombre, AgX
A.cielo('snowy_field', forza=1.2, rotazione=84)       # luce, ombre del sole e sfondo
ghiaccio = A.materiale('Ice004', dimensione=5, ruvidita=0.25, tinta=(1.5, 1.95, 2.4), vernice=1.0)
A.applica(pavimento, ghiaccio)
A.bosco_cartonato('fir_tree_01', 40, area=(-38, 38, 24, 48), altezza=(19, 27))   # sfondo di bosco
A.modello('street_lamp_01', posizione=(-6.5, 11.6, 0), altezza=4.2)
A.sparpaglia('boulder_01', 3, area=(4, 8, 10, 11), altezza=(0.5, 1.1))
```

Ogni funzione scarica da sola l'asset se non è ancora su disco.

Per avere tutto subito: `python pt_assets.py scarica-tutto` (oppure `--tipo hdri`, `--tipo texture`, `--tipo modello`).

Per cercare: `python pt_assets.py cerca neve`, `python pt_assets.py cerca albero --tipo modello`. Le parole italiane più comuni vengono tradotte; per il resto cerca in inglese.

`esempio_pista_ghiacciata.py` è una scena realistica costruita solo con la libreria (pista ghiacciata, bosco, tribuna, lampioni, neve che cade). `esempio_quartiere.py` è una via di quartiere dove case e alberi sono tutti diversi; cambiando il numero finale (il seme) cambia la disposizione.

## Impostazioni di render: qualità e tempo

`A.qualita_eevee(preset='equilibrato')` applica le impostazioni con il miglior rapporto trovato misurando 47 combinazioni sulla scena di esempio (Eevee senza scheda video, 2 processori). La somiglianza è l'indice SSIM rispetto a un render di riferimento a 1080×1920 con 64 campioni (1 = identico).

| Impostazione | Secondi a fotogramma | Somiglianza | 45 s di video a 24 fps |
|---|---|---|---|
| Metodo di prima: 540×960, 16 campioni, poi ingrandito | 29,0 | 0,935 | 8,7 ore |
| `veloce`: 1080×1920, 4 campioni | 13,7 | 0,957 | 4,1 ore |
| `equilibrato`: 1080×1920, 6 campioni | 19,3 | 0,969 | 5,8 ore |
| `alto`: 1080×1920, 8 campioni | 25,3 | 0,975 | 7,6 ore |
| `massimo`: 1080×1920, 16 campioni | 57,6 | 0,988 | 17,3 ore |

Cosa hanno detto le misure:

- **Il tempo dipende dai campioni, molto meno dalla risoluzione.** A 16 campioni: 29 s a 540×960, 36 s a 720×1280, 58 s a 1080×1920. Quattro volte i pixel costano il doppio, non il quadruplo. Quindi conviene la risoluzione piena con pochi campioni: 4 campioni a 1080×1920 sono più nitidi di 32 campioni a 540×960 ingranditi, in un quarto del tempo (14 s contro 55 s).
- **Le ombre sono più di metà del tempo** (29 s con, 12,5 s senza) e le opzioni delle ombre spostano poco: il limite di risoluzione e l'esclusione di terreno, fiocchi e alberelli insieme valgono l'11%. Si risparmia abbassando i campioni, non togliendo le ombre.
- **Riflessi:** costano circa un quarto del tempo (`equilibrato` scende da 19,3 a 14,4 s). Con ghiaccio, acqua o pavimenti lucidi tienili; altrimenti `riflessi=False`.
- **Sfocatura (profondità di campo):** 10% del tempo; a diaframma chiuso non cambia l'immagine. Tienila spenta se non serve.
- **Da non toccare:** il cielo a 1K al posto del 4K fa risparmiare il 6% ma sfoca lo sfondo; abbassare la risoluzione della sonda del mondo rovina l'immagine.
- **Due render in parallelo non reggono:** con 8 GB di memoria uno dei due processi si interrompe.
- **Movimento:** su 10 fotogrammi con camera e personaggio in movimento, 4, 6 e 8 campioni hanno uno sfarfallio quasi uguale (12,0 / 11,1 / 10,9 sugli alberi). A 4 campioni resta un po' di grana sui bordi delle sagome.

Le misure sono sulla scena di esempio: su altre scene i secondi cambiano, le proporzioni dovrebbero restare simili.

## Quanto pesa sul render

Quanto aggiungono gli asset rispetto a una scena a colori piatti. Misure sulla scena di esempio, a 540×960 con 16 campioni, tempo per fotogramma a regime:

| Scena | Secondi | Memoria |
|---|---|---|
| Stessa scena con colori piatti, cielo a tinta unita e lampada Sun | 19,0 | 1,9 GB |
| Con cielo HDRI e texture su neve, ghiaccio e legno | 20,4 | 2,2 GB |
| Completa: più 52 sagome d'albero, 3 gruppi di abetini veri, lampioni, panchina, secchio, ceppo, massi | 26,2 | 3,3 GB |

Quindi texture e cieli costano circa il 7%, la scena completa circa il 38% in più.

Due cose rallentano molto e la libreria le evita da sola:

- **Sagome con ombra.** 52 sagome che proiettano ombra portavano il fotogramma da 20 a 42 secondi; senza ombra a 23. Per questo `albero_cartonato()` e `bosco_cartonato()` hanno `ombra=False` di default. Usa `ombra=True` solo sulle poche sagome vicine.
- **Vetri "blended".** I due lampioni con il vetro originale costavano circa 14 secondi a fotogramma. `modello()` converte questi materiali in "dithered" (`veloce=True`).

Altre regole:

- **Alberi veri:** quelli leggeri costano poco (3 gruppi di `fir_sapling_medium`, 96.000 triangoli in tutto: mezzo secondo). Quelli fitti no: con 11 gruppi di `fir_tree_01` e 5 di abetini, a 540×960 il render si è interrotto per memoria esaurita. Abeti e pini grandi vanno messi come sagome.
- **Texture su oggetti creati da script:** `materiale()` usa la proiezione a scatola, quindi funziona anche senza UV e mantiene la misura reale su oggetti scalati. `dimensione` è il lato in metri di una ripetizione.
- **Riflessi:** bastano `qualita_eevee()` e un materiale poco ruvido (`ruvidita=0.25, vernice=1.0`). Non aggiungere sonde di riflesso piane: in questo tipo di render li spengono.
- **Il sole è nell'HDRI.** `rotazione` lo sposta. Non serve una lampada Sun.
- **Sfondo nitido:** il 1K basta per la luce; per vedere bene il paesaggio dietro usa un cielo che ha il 4K (`ris='4k'` lo scarica al volo).

## Catalogo visivo

Le anteprime di tutti gli asset, con ricerca e filtri, sono nella pagina «Libreria asset Pippo e Tumbo» tra i tuoi artefatti. I nomi mostrati lì sono quelli da passare alle funzioni.

## File

- `pt_assets.py`: tutto il codice. Basta da solo: se manca il catalogo lo ricostruisce dalla rete.
- `catalogo.json.gz`: indice degli asset, con triangoli e altezza verificati per i modelli.
- `alberi_cartonati/`: sagome già pronte. `crea_sagome.py` ne genera altre da qualunque modello, anche da più lati (`python crea_sagome.py jacaranda_tree --angoli 0,120,240`): scarica il modello da solo e salta quelle già fatte. I file `<nome>_<n>_a120.webp` sono lo stesso albero girato di 120 gradi; `albero_cartonato()` e `bosco_cartonato()` li pescano come viste in più.
- `effetti/`, `font/`: immagini degli effetti e font, con i file di licenza.
- `esempio_pista_ghiacciata.py`, `esempio_quartiere.py`: scene di esempio.
