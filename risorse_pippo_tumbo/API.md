# Indice delle funzioni (generato dagli script)


## scripts/common.py

Helper condivisi per il progetto PIPPO SATISFYING TEST 001 (Blender 5.x).

- `reset_scene()`
- `collection(name, parent=None)`
- `_link(o, coll)`
- `shared_mesh(kind)` — Mesh unitarie condivise (sfera, cono) -> tutte le istanze usano gli stessi dati.
- `material(name, color, rough=0.5, metallic=0.0, spec=0.5, coat=0.0, coat_rough=0.1, emit=None, emit_strength=0.0)`
- `empty(name, loc=(0, 0, 0), parent=None, coll=None, size=0.08)`
- `shape(name, kind, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), parent=None, mat=None, coll=None)`
- `key(o, prop, value, frame, index=-1, interp=None)`
- `all_fcurves(obj_or_data)` — Compatibile con le Action a livelli di Blender 4.4+/5.x.
- `set_interp(obj, kind='BEZIER')`

## scripts/render_setup.py

- `setup_render(scene, w, h, samples=16, fps=24, frames=240)`
- `world(scene, top=(0.75, 0.88, 1.0), bottom=(0.95, 0.9, 0.85), strength=0.9)`
- `area_light(name, loc, target, energy, size, color=(1, 1, 1), coll=None)`
- `camera(name, loc, target, lens=35, coll=None)`

## scripts/set004.py

Ambiente Test 003: città, letto del campo con 4 stati, porte, attrezzi.

- `box0()` — cubo unitario con origine nell'angolo minimo (scalare = crescere da quell'angolo).
- `box_c()`
- `prism()` — prisma triangolare (tetto a capanna): base 1x1 in xy, colmo lungo y a z=0.5 (centrato in z da -0.5 a 0.5)
- `obj(name, mesh, loc, scale, mat, coll, rot=(0, 0, 0), parent=None)`
- `bx(name, p0, p1, mat, coll)` — scatola dall'angolo p0 all'angolo p1 (origine in p0).
- `cyl(name, r, h, loc, mat, coll, rot=(0, 0, 0), parent=None)`
- `ball_(name, r, loc, mat, coll, parent=None, sc=(1, 1, 1))`
- `noise_mat(name, c1, c2, scale=6.0, rough=0.9)`
- `glassy(name, color, alpha, rough=0.1)`
- `grid_mat(name, col, dark, pz, px, rough=0.85)` — colore con righe orizzontali (ogni pz in Z locale) e giunti verticali sfalsati (ogni px in X): doghe / tegole.
- `house_mats(M, wi, ri, si)`
- `window_geo(mb, cx, y, cz, ww=0.62, wh=0.78, face=-1, shutters=True, flowerbox=False, axis='x')` — finestra su una parete: axis='x' parete a y costante (larghezza lungo x), axis='y' parete a x costante.
- `roof_geo(mb, w, d, h, rh=1.25, ov=0.34)` — tetto a due falde con colmo lungo X, gronde sporgenti, timpani nel colore del muro, camino.
- `house_geo(mb, w, d, h, two, rng)`
- `tower_geo(mb, tw, h, rng)` — palazzo: 0 muro, 1 vetro, 2 bianco, 3 cemento, 4 scuro, 5 accento.
- `make_mats()`
- `build_city(coll, M, rng)` — Strade, marciapiedi e quartiere di casette tutto attorno al campo.
- `build_field(coll, M, rng)` — Letto campo, cordoli, 6 strisce di terreno sconnesso (con shape key 'flat'). Ritorna dict di handle.
- `ribbon(name, pts, width, mat, coll, zfun, flat_z=None, build=None)` — Nastro bianco lungo una polilinea; (zfun(x,y) = quota). Se flat_z: shape key 'flat'. build=(frame_start, duration).
- `goal(name, side, M, coll)` — porta: side=+1 (x=+PX) o -1. Ritorna root; la rete e' un oggetto separato (net) per animarla.

## scripts/pippo.py

Pippo v2 - stile 3D cartoon pulito (capsule, materiali opachi, occhi grandi con riflesso).
Solo primitive: capsule, ellissoidi, ciocche a goccia. Rig a empty gerarchici.
Pippo guarda verso -Y con rot_z = 0. Altezza ~1.95 m con i capelli.

- `build_materials()`
- `_bolt(M, parent)` — Fulmine estruso, proiettato sulla capsula del busto.
- `build_pippo(coll=None)`
- `express(R, f, brow=0.0, brow_lift=0.0, eye_open=1.0, smile=0.0, mouth_open=0.0, look=(0.0, 0.0), eye_scale=1.0)` — brow>0 = determinate, <0 = sorpresa/triste; brow_lift alza le sopracciglia;

## scripts/tumbo.py

Tumbo, il cane di Pippo - stesso stile (capsule, ellissoidi, materiali opachi).
Guarda verso -Y con rot_z = 0.

- `build_tumbo(coll=None, scale=0.75)`
- `tumbo_express(R, f, tongue=0.0, brow=0.0, eye_scale=1.0, eye_open=1.0, look=(0, 0))`

## scripts/props004.py

Attrezzi, giocatori, nuvole e pioggia per Test 003.

- `cart(coll, M)` — segnalinee: origine al suolo sotto il corpo, fronte -Y. Maniglia verso +Y (verso chi spinge).
- `bulldozer(coll, M)` — fronte +X; origine al suolo.
- `roller(coll, M)` — rullo compressore, fronte +X.
- `brush_machine(coll, M)` — spazzola/distributore: avanza lungo +X, larga lungo Y.
- `sprinkler(coll, M)`
- `flag(coll, M)`
- `floodlight(coll, M)`
- `player(coll, name, shirt, shorts, skin, hair, scale=1.0)` — giocatore semplice (non e' Pippo): fronte -Y, piedi a z=0.
- `cloud(coll, M, loc, s=1.0)`
- `rain_layer(coll, M, seed, n=700, area=(10.0, 7.0), zmax=11.0)`

## scripts/props007.py

Test 007 - oggetti: nano da giardino, cuore, staccionata a piani, merli, scale, tappeto elastico, catapulta, palloncini, cartelli.

- `mats007()`
- `_bm_obj(name, bm, mats, coll, smooth=True)`
- `_sph(bm, c, r, sc=(1, 1, 1), mi=0, seg=16, rings=10)`
- `_cone(bm, c, r1, r2, h, mi=0, seg=16, rot=None)`
- `gnome_mesh(M, hat=0, coat=0)` — nano da giardino alto ~0.8, rivolto a -Y, origine ai piedi.
- `heart_mesh(M)`
- `fence_tier(coll, M, x0, x1, h, seed, name='Staccionata', axis='x')` — un piano di staccionata di assi (lungo X, spessore su Y), origine alla base. Assi storte e di colori diversi.
- `battlements(coll, M, x0, x1, z)` — merli di pietra, due torrette a pagoda e bandiera: la 'muraglia cinese'. Restituisce [oggetti] (origine a quota z).
- `ladder(coll, M, L, name='Scala')`
- `trampoline(coll, M, R=1.45, H=0.9)` — restituisce (root, telo, telo strappato).
- `catapult(coll, M)` — catapulta di legno: avanti = -Y. Restituisce (root, braccio); il braccio ruota su X attorno al perno (0,0,1.45), punta a +Y lunga 2.6.
- `balloons(coll, M, parent, loc, n=7, seed=2)` — mazzo di palloncini: restituisce (root, [palloncini]).
- `text_obj(coll, name, body, size, mat, loc, rot=(math.pi / 2, 0, 0), parent=None)`
- `sign(coll, M, body, w=1.2, h=0.34, size=0.17, post=0.9)` — cartello di legno su paletto, scritta verso -Y. Origine a terra.

## scripts/props009.py

Test 009 - PIPPO CONTRO GUALTIERO ep. 1: il vicino Gualtiero (pupazzo ricorrente) e gli oggetti della neve ad agosto.

- `mats009()`
- `gualtiero(coll, M)` — Gualtiero, il vicino: canottiera, pancia, baffi, calzini e ciabatte. Fronte -Y, piedi a z=0.
- `gex(R, f, brow=0.3, mouth=0.25, tongue=0.0, look=(0, 0))` — brow>0 arrabbiato, <0 spaventato; mouth 0..1; tongue 0..1.
- `hand_tool(coll, M, sh, kind)` — attrezzo nella mano (figlio della spalla): la canna prosegue il braccio lungo -Z. kind = 'phon' | 'gun'.
- `backpack(coll, M, root)`
- `flame(coll, M, parent, loc)` — fiamma lungo -Z (figlia dell'attrezzo): due gocce emissive. Scala l'empty per accenderla.
- `snowman(coll, M)`
- `disc(coll, name, mat, r=1.0, h=0.02)`
- `beanie(coll, M, head, cz=0.61, r=0.43)`
- `sun(coll, M, r=2.0)`
- `freezer(coll, M)` — congelatore a pozzetto: origine sullo spigolo basso ovest (ci ruota sopra per rovesciarsi verso -X). Restituisce (root, coperchio).
- `ice_pile(coll, M, n=46, seed=5)`
- `barbecue(coll, M)` — restituisce (root, [fiamme]).
- `popsicle_parts(coll, M, pts)` — stecchi (una mesh sola) + teste (un oggetto per ghiacciolo). pts = [(x, y)] -> lista di oggetti testa.
- `vacuum(coll, M)`
- `cannon_tube(coll, M, L=1.3)` — tubo-cannone: origine all'impugnatura, asse +Z verso la bocca.
- `armchair(coll, M)`
- `heap(coll, M, name='Mucchio', n=16, seed=3, r=1.0, mat='snow')` — mucchio bianco bitorzoluto, origine a terra, raggio ~r, altezza ~0.75 r.
- `truck(coll, M)` — camion ribaltabile: fronte -Y, lungo 6.4. Restituisce (root, cassone[perno posteriore], carico).
- `car(coll, M)` — utilitaria: fronte -Y.

## scripts/giulia.py

Giulia, la moglie di Gualtiero: grossa, sgraziata, naso lungo a penzoloni che dondola.
Stesso stile di Gualtiero (capsule e sfere). Fronte -Y, piedi a z = 0, alta 2,2 m con i bigodini, larga 1,8 m.
L'autore ha scelto l'aspetto A (17 novembre 2026): e' quello predefinito. B e C restano come travestimenti.

    import giulia
    GM = giulia.mats_giulia()
    J = giulia.giulia(chc, GM, stile='A')      # 'A' bigodini e vestaglia a fiori, 'B' permanente e leopardato,
                                              # 'C' crocchia, occhiali e grembiule
    giulia.giex(J, frame, brow=0.6, mouth=0.4, lid=0.3, look=(0, 0), naso=0.5)
    giulia.mattarello(chc, GM, J)              # mattarello nella mano destra

Dizionario restituito: root, head, belly, shoulderL/R, hipL/R, browL/R, pupilL/R, lidL/R, mouth, lip, tooth, nose.
Le braccia a riposo sono aperte di 25 gradi perche' la pancia e' piu' larga delle spalle.

- `_fantasia(name, base, punti, scala=7.0, soglia=0.32, rough=0.75, punti2=None)` — Stoffa a pallini o macchie: colore di base con punti di un altro colore (ed eventualmente di un terzo).
- `mats_giulia()`
- `giulia(coll, M, stile='A')` — Costruisce Giulia. stile: 'A' | 'B' | 'C' (vedi in testa al file).
- `giex(R, f, brow=0.4, mouth=0.15, lid=0.45, look=(0, 0), naso=0.0)` — Faccia di Giulia al fotogramma f (f=None: imposta senza chiavi).
- `mattarello(coll, M, R, lato='R')` — Mattarello stretto nella mano (figlio della spalla): punta in avanti, verso -Y.

## scripts/pippo2.py

Pippo con le emozioni nuove (17 novembre 2026). Decisione finale dell'autore: l'aspetto resta quello di sempre,
cambiano solo le emozioni (gli occhi non cambiano mai misura, le sopracciglia si inclinano di piu'). Le varianti P/Q/R
restano qui solo come prove scartate.
pippo.py NON viene toccato: qui si costruisce il Pippo di sempre e gli si cambiano i pezzi.
Stessa interfaccia di pippo.py, quindi in un episodio basta cambiare l'import:

    import pippo2 as pippo
    P = pippo.build_pippo(chc)                       # con le scelte dell'autore (vedi SCELTE)
    P = pippo.build_pippo(chc, capelli='P2', occhi='Q1', corpo='R1')
    pippo.express(P, frame, smile=1.0, ...)          # stessi parametri di pippo.py, ma gli occhi non cambiano mai misura (regola dell'autore)

Opzioni (lo 0 e' sempre il Pippo di prima):
    capelli  P0 di prima | P1 ciuffo a onda | P2 ciuffo alto | P3 ricci (scartati dall'autore)
             P4 spettinato in avanti | P5 di lato | P6 punte all'insu' (ciocche a punta che seguono la testa)
             P7 ricci (scartati: «orrendi») | P8 ordinati, pettinati all'indietro (scartati: li vuole spettinati)
             P9 spettinati e bassi (scelto dall'autore) | P10 spettinati, piu' alti e selvaggi
    occhi    Q0 di prima | Q1 iride castana | Q2 iride azzurra | Q3 a bottone | Q4 come Gualtiero | Q5 come Gualtiero, piu' grandi
    corpo    R0 di prima | R1 spalle e fianchi | R2 spalle e fianchi piu' larghi (busto in un pezzo solo)

- `_via(o)`
- `_ciocca(nome, punti, raggi, mat, parent, coll)` — Ciocca liscia che segue i punti (coordinate locali alla testa) con lo spessore dato in ogni punto.
- `_fibonacci(n)` — n direzioni ben distribuite sulla sfera.
- `_attaccatura(d)` — quota (sulla sfera unitaria) sotto la quale non ci sono capelli: alta sulla fronte, bassa sulla nuca.
- `_flusso(stile, d)` — direzione in cui vanno pettinati i capelli nel punto d della testa (sfera unitaria).
- `_ciuffi_ordinati(R, coll, M)` — I capelli di sempre (ciocche a goccia, stesso colore) ma in ordine: tutti pettinati all'indietro e un po' verso l'alto,
- `_spettinati(R, coll, M, selvaggio=False)` — Spettinati ma fatti bene: ciocche grosse a goccia, a strati, ognuna con la sua direzione ma entro un limite
- `_nuca(R, coll)` — Capelli dietro la testa per il Pippo di sempre: due giri di ciocche che scendono sulla nuca e sopra le orecchie,
- `_ricci(R, coll, M)` — Capelli ricci e pieni: una massa di riccioli tondi in due strati, piu' alta in cima, e boccoli a molla sulla fronte e ai lati.
- `_punte(R, coll, stile, M)` — ciocche a punta: partono dentro la testa, scorrono sulla superficie nel verso del flusso e si staccano in punta.
- `_capelli(R, coll, stile)`
- `_occhi(R, coll, stile)`
- `_corpo(R, coll, stile)` — Il busto diventa un pezzo solo che si allarga dolcemente alle spalle e ai fianchi (niente pezzi attaccati).
- `express(R, f, brow=0.0, brow_lift=0.0, eye_open=1.0, smile=0.0, mouth_open=0.0, look=(0.0, 0.0), eye_scale=1.0)` — Come pippo.express, ma gli occhi restano sempre della stessa misura: niente occhi che si rimpiccioliscono o si ingrandiscono
- `build_pippo(coll=None, capelli=None, occhi=None, corpo=None)` — Costruisce Pippo con i pezzi scelti. Senza argomenti usa SCELTE (le scelte dell'autore).
- `_segni(P)` — Costruisce (spenti) i segni da cartone animato attaccati alla testa.
- `emozione(P, f, nome, forza=1.0)` — Emozione esagerata al fotogramma f: faccia, posa e segni da cartone. forza 0..1 per dosarla.

## scripts/props010.py

Test 010 - PIPPO CONTRO GUALTIERO ep. 2: IL PROCESSO AL SOLE. Il Sole (personaggio), polizia, carcere, tribunale.

- `mats010()`
- `sun_char(coll, M, R=0.8)` — il Sole: disco con raggi, faccia, braccine, occhiali, manette, aureola. Fronte -Y, origine al centro.
- `sex(S, f, brow=0.0, mouth=0.3, tongue=0.0, look=(0, 0), eye=1.0)` — brow>0 cattivo, <0 triste/spaventato; mouth 0..1 (aperta); eye = scala degli occhi.
- `sunbed(coll, M)` — sdraio lungo X: testa a -X. Origine a terra, ai piedi (+X).
- `phone(coll, M, sh)`
- `police_car(coll, M, G9)`
- `cop(coll, name='Agente')`
- `ext_ladder(coll, M, L)` — scala lungo +Z dall'origine (si allunga scalando Z).
- `jail_set(coll, M, x0, label='SOLE  N. 0001', sub='USTIONI AGGRAVATE')` — parete con righe d'altezza + pavimento; restituisce (sbarre, cartello).
- `court_set(coll, M, x0, motto2='(TRANNE PER IL SOLE)')` — tribunale: parete, pavimento, banco del giudice (piano a z=1.55), gabbia dell'imputato a sinistra. Restituisce sbarre della gabbia.
- `cage(coll, M, w=2.6, h=3.4)` — gabbia dell'imputato: origine a terra al centro, sbarre davanti e ai lati.
- `wig(coll, M, head, c=(0, 0.02, 0.22), s=1.0)`
- `gavel(coll, M, parent, loc)` — martelletto: perno all'impugnatura, manico lungo +Z.
- `tie(coll, M, root)`
- `briefcase(coll, M, sh)`
- `raincloud(coll, M)`

## scripts/props011.py

Test 011 - PIPPO E IL TORNADO: il Tornado (personaggio), macerie, cappello volante.

- `mats011()`
- `ring_r(k)`
- `ring_z(k)`
- `tornado(coll, M)` — Tornado: 9 anelli che ondeggiano, faccia sull'anello 4, braccine con manette. Origine a terra (punta).
- `tornex(T, f, brow=0.6, mouth=0.3, tongue=0.0, look=(0, 0), eye=1.0)`
- `rubble(coll, mats, w=6.5, d=4.5, n=46, seed=2)` — macerie: scatole sparse (materiali della casa). Origine al centro a terra.
- `fly_cap(coll, M)`
- `crack(coll, M, L=9.0, seed=4)`

## scripts/props012.py

Test 012 - PIPPO E LA ZUCCHINA ELEONORA: zucchina, tavolino, rosa, bomba, orto, fungo, moto-prete.

- `mats012()`
- `zucchina(coll, M)` — Eleonora: zucchina lunga ZL, asse +Z, origine alla base. Occhi/bocca/gambe/velo si accendono a parte. Fronte -Y.
- `table(coll, M, name='ELEONORA')` — tavolino con cuscino e cartellino: piano a z=0.80.
- `rose(coll, M, sh)` — rosa nella mano (figlia della spalla): stelo lungo il braccio.
- `bulb(coll, M)`
- `bomb(coll, M)` — bomba atomica da cartone: asse +Z (punta in alto), origine al centro. Lunga ~1.5.
- `orto(coll, M, w=5.0, d=4.0, seed=3)` — orto del vicino: aiuole con cavoli, carote, pomodori. Origine al centro.
- `mushroom(coll, M)` — fungo atomico: origine a terra, alto ~14 (scalare l'empty).
- `moto(coll, M)` — moto-prete: fronte -Y, origine a terra sotto il centro. Sella a z~0.85. Restituisce (root, faro[empty per la 'faccia'], ruote).
- `mats_nuke()`
- `mushroom2(coll, M)` — fungo atomico grande: origine a terra, alto ~14 unita' (da scalare). Restituisce (root, anello del cappello che rotola).
- `ruins(coll, M, items, trunks, seed=5)` — macerie al posto di case/palazzi: items = [(x, y, w, d, h, rotz)], trunks = [(x, y)]. Una mesh sola.
- `fire(coll, M, s=1.0)` — focolaio: fiamme (da scalare a ogni fotogramma) + colonna di fumo. Restituisce (root, [fiamme]).
- `moto_extras(coll, M, moto_root, face)` — rifiniture della moto: serbatoio tondo, parafanghi, colletto da prete ben visibile, targa OGGI SPOSI.

## scripts/eleonora.py

Eleonora con le emozioni (17 novembre 2026). props012.py NON viene toccato: qui si costruisce la zucchina di sempre
e le si aggiungono due sopracciglia sottili, una bocca che sorride o si apre, e un perno per piegare il corpo.
Regola dell'autore (come per Pippo): gli occhi non cambiano mai misura.

    import props012, eleonora
    Z12 = props012.mats012()
    Z = eleonora.zucchina(chc, Z12)               # stesso dizionario di props012.zucchina (eyes, mouth, legs, veil...)
    eleonora.express(Z, frame, brow=0.8, smile=-1, mouth_open=0.3, look=(0, 0), piega=(0, 0), schiaccia=0)
    eleonora.emozione(Z, frame, 'felice')         # una delle EMOZIONI pronte

brow > 0 arrabbiata, < 0 triste/spaventata; brow_lift alza le sopracciglia; smile -1..1; mouth_open 0..1;
look (x, z) sguardo; piega (avanti, di lato) in radianti, il corpo si piega dalla base; schiaccia > 0 si accascia, < 0 si allunga.
Z['mouth'] ora e' un gruppo (bocca nuova), quindi show()/pop() sugli episodi vecchi funzionano uguale.

- `zucchina(coll, M)`
- `velo(Z, acceso)` — Mostra o nasconde il velo da sposa (anche i pezzi figli).
- `express(Z, f, brow=0.0, brow_lift=0.0, smile=0.0, mouth_open=0.0, look=(0.0, 0.0), piega=(0.0, 0.0), schiaccia=0.0)` — Chiavi al fotogramma f (f=None: solo la posa). Gli occhi non cambiano misura.
- `emozione(Z, f, nome)`

## scripts/props013.py

Test 013 - PIPPO E TUMBO IN AEREO: aereo, cabina di pilotaggio, cabina passeggeri, ospedale, città, accessori da vacanza.

- `mats013()`
- `airplane(coll, M, L=16.0, R=1.25)` — aereo di linea da cartone: muso verso +X, origine a terra sotto il centro (carrello giu'). Restituisce dict(root, gear).
- `sunglasses(coll, M, head, y=-0.36, z=0.32, dx=0.13, w=0.27, h=0.22)`
- `lei(coll, M, parent, loc, r=0.3, tilt=0.35, n=22, s=0.07)`
- `suitcase(coll, M)`
- `gelato(coll, M, parent, loc)` — gelato gigante: cono verso il basso, tre palline. Origine all'impugnatura.
- `pilot_cap(coll, M, head)`
- `mic(coll, M, parent, loc)`
- `manual(coll, M)` — manuale di volo, morsicato: due stadi (intero/mangiato).
- `cockpit_set(coll, M, x0)` — cabina di pilotaggio aperta in alto: guarda verso +X. Sedili a (x0-0.3, ±0.65). Restituisce dict.
- `cabin_set(coll, M, x0, rows=5)` — cabina passeggeri lungo X, guardando verso +X (cockpit). Corridoio a y=0. Porta WC in fondo (x0-0.6). Restituisce (sedili [(x, y)], porta).
- `drinks_cart(coll, M)`
- `hospital_set(coll, M, x0)` — stanza d'ospedale: letto con il cuscino verso -Y? No: letto lungo X, testata a -X. Restituisce posizione del cuscino.
- `airport(coll, M, x0, y0)`
- `lowcity(coll, Mset, M, x0, y0, rng)` — citta' di case basse (niente grattacieli), ospedale con croce rossa al centro. Restituisce la posizione dell'ospedale.

## scripts/props014.py

Test 014 - IL TOAST DI PIPPO: fetta di pane, forno industriale, vulcano, torri di raffreddamento, catena di montaggio, cucina.

- `mats014()`
- `lathe(name, profile, mat, coll, seg=32, loc=(0, 0, 0), cap=False)` — solido di rivoluzione attorno a Z: profile = [(r, z), ...] dal basso in alto.
- `bread(coll, M, name='Fetta', toast=False)` — fetta di pane in piedi: larga 1, alta ~1, spessa 0.13, faccia verso -Y. Origine alla base.
- `oven(coll, M, W=5.0, D=4.0, H=4.2)` — forno industriale: fronte -Y, origine a terra al centro. Restituisce dict(root, door, dim, bright, needle, chimney).
- `volcano(coll, M, R=6.0, H=9.0)` — vulcano: lathe con cratere e colate. Origine a terra al centro. Restituisce dict(root, crater).
- `cooling_tower(coll, M, R=4.5, H=15.0, name='Torre')`
- `pipe(coll, M, p0, p1, r=0.45, name='Tubo')`
- `conveyor(coll, M, x, y0, y1, z=0.9, w=1.0)` — nastro trasportatore lungo Y da y0 a y1 (y1 < y0), piano a quota z. Una mesh sola.
- `intake(coll, M, x, y, z=0.9)` — la 'macchina' all'ingresso del forno: tramoggia con due rulli giganti e un varco in mezzo. Restituisce (root, [rulli]).
- `kitchen(coll, M, x0)` — cucina: parete a y=+2, bancone lungo la parete con lo spazio vuoto del tostapane al centro.

## scripts/props015.py

Test 015 - IL PARTO DI ELEONORA: neonati, culle, corridoio, mucca con le ali da fata, nuvola di puzza, maschere antigas.

- `mats015()`
- `baby(coll, M, name='Neonato')` — neonato da cartone seduto: origine sotto il pannolino. Fronte -Y.
- `crib(coll, M, name='Culla')` — culla: piano a z=0.72. Origine a terra.
- `corridor(coll, M, x0)` — corridoio d'ospedale: parete a y=+1.6 con porta 'SALA PARTO' e sedie.
- `sandwich(coll, M, parent, loc)`
- `cow(coll, M)` — mucca con le ali da fata: fronte -Y, origine sotto la pancia (zampe fino a z=-0.75). Restituisce dict(root, wings[], legs[], tail, rear).
- `stink_cloud(coll, M, name='Puzza', n=14, R=0.9, seed=1)` — nuvola verde di puzza. Origine al centro.
- `gas_mask(coll, M, head)`
- `window(coll, M, loc, w=1.2, h=1.3, rotz=0.0)`
- `hospital_ext(coll, M, x, y, W=16.0, D=7.5, H=10.5)` — facciata dell'ospedale verso -Y (fronte a y). Restituisce dict(win_esc=posizione finestra della fuga).
- `magnifier(coll, M, parent, loc)`
- `torus_mesh(name, R, r, nu=40, nv=14)`
- `cuffs(coll, M, parent, loc, s=1.0)`

## scripts/props016.py

Test 016 - GUALTIERO E IL METEORITE: ruspa, meteorite con etichetta, autogru, limonata, buco nel muro, macerie, cratere,
fumo e fuoco, negozio di ferramenta, salotto di Pippo con le foto. Gli oggetti realistici arrivano dalla libreria (pt_assets, parametro A).

- `mats016()`
- `bulldozer(coll, M)` — ruspa: lama davanti verso -Y, origine a terra al centro. Restituisce dict(root, blade).
- `meteor(coll, M, A, size=2.6)` — meteorite: masso vero della libreria + alone di fuoco + etichetta di spedizione. Origine al centro. Restituisce dict(root, rock, flames, label).
- `crane(coll, M, boom=13.0)` — autogru: muso verso -Y, origine a terra. turret ruota su Z, boom si alza su X (0 = orizzontale verso +Y). Restituisce dict(root, turret, boom, boom_len, pivot_h).
- `lemonade(coll, M, parent=None, loc=(0, 0, 0), s=1.0)`
- `hole(coll, M, w=2.4, h=2.0, seed=1, n=13)` — buco frastagliato da mettere davanti a un muro (piano XZ, guarda verso -Y). Origine al centro.
- `rubble(coll, mats, n=40, R=1.6, seed=1, size=(0.18, 0.42), heap=0.7)` — mucchio di macerie (mattoni e pezzi di intonaco). Origine a terra al centro.
- `crater(coll, M, R=4.5, seed=2)` — cratere: disco bruciato, anello di terra smossa, crepe. Origine a terra al centro.
- `smoke_column(coll, M, n=14, h=9.0, r0=0.9, seed=4, name='Fumo')`
- `flames(coll, M, n=7, R=1.2, seed=5, name='Fiamme')`
- `ferramenta_set(coll, M, x0, A)` — negozio di ferramenta: facciata verso -Y a y=3, insegna, vetrina con i martelli veri, porta, tenda a strisce, marciapiede. Restituisce la posizione della porta.
- `photo_frame(coll, M, path, loc, w=0.8, h=1.0, rotz=0.0, name='Foto')` — quadro con una foto (immagine su file): guarda verso -Y.
- `salotto_set(coll, M, x0, A, photos=())` — salotto di Pippo: pavimento di legno, pareti, divano vero, tappeto, foto di Pippo alle pareti, porta sulla parete sinistra.

## scripts/props016b.py

Test 016 - IL SECONDO PARTO: cocomero (senza faccia), camion dei pompieri, pianoforte, busta di patatine, cartella clinica, porta, scotch.

- `mats016b()`
- `melon_mat(name)` — buccia di cocomero: strisce verdi scure e chiare lungo l'asse, un po' mosse.
- `watermelon(coll, M, r=0.3, name='Cocomero')` — cocomero liscio, senza faccia: origine al centro, asse lungo Z.
- `firetruck(coll, M, L=2.6)` — camion dei pompieri: muso verso -Y, origine a terra. Restituisce dict(root, lights=[(rossa, blu)], ladder).
- `piano(coll, M)` — pianoforte verticale: tastiera verso -Y, origine a terra.
- `chips_bag(coll, M, parent=None, loc=(0, 0, 0), s=1.0)`
- `clipboard(coll, M, parent=None, loc=(0, 0, 0), word='NORMALE')` — cartella clinica: faccia scritta verso -Y.
- `door(coll, M, loc, rotz=0.0, label='USCITA')` — porta su una parete: pivot del battente sul lato sinistro. Restituisce il pivot (ruota su Z per aprire).
- `tape_patch(coll, M, parent, loc, rot=(0, 0, 0), size=(0.14, 0.01, 0.035))`
- `room_shell(coll, A13, W15, x0)` — sala parto vuota (senza letto): pavimento, pareti, soffitto, croce rossa. Si arreda con i modelli della libreria.
- `corridor_shell(coll, W15, x0)` — corridoio vuoto (senza sedie): pavimento, pareti, soffitto, porta 'SALA PARTO'.
- `kplace(A, aid, coll, x, y, z=0.0, s=2.3, rot=0.0, center=True, name=None)` — mette un modello Kenney con scala fissa; center=True: (x, y) e' il centro della sua base (i mobili Kenney hanno l'origine in un angolo).

## scripts/animali.py

Animali nello stile di Pippo e Tumbo: capsule, ellissoidi, occhi grandi, materiali opachi. Niente modelli a cubo.
Tutti guardano verso -Y con rot_z = 0, origine a terra. Ogni funzione restituisce un dizionario:
root, body, head, eyeL/R, pupilL/R, legs[] (dove ci sono), tail (dove c'e').
Uso: import animali; A = animali.crea('mucca', coll); A['root'].location = (x, y, 0)

- `_mat(name, col, **k)`
- `_kit(coll, pfx)`
- `_eyes(R, S, E, head, M, dx, y, z, k=1.0, brow=None)` — occhi come quelli di Tumbo: ellissoide bianco, pupilla scura, riflesso.
- `_tube(S, name, pts, r0, r1, par, mat, n=14)` — tubo morbido fatto di sfere lungo una spezzata (proboscidi, code, colli).
- `_spot(S, name, a, y, rx, rz, sy, sz, par, mat, thick=0.045)` — macchia piatta appoggiata sul fianco di un corpo con asse lungo Y (a = angolo attorno all'asse).
- `_start(coll, pfx, name, zbody, scale)`
- `mucca(coll=None, scale=1.15)`
- `elefante(coll=None, scale=1.0)`
- `pinguino(coll=None, scale=0.85)`
- `giraffa(coll=None, scale=1.0)`
- `maiale(coll=None, scale=1.0)`
- `leone(coll=None, scale=1.0)`
- `scimmia(coll=None, scale=0.9)`
- `pulcino(coll=None, scale=0.75)`
- `granchio(coll=None, scale=0.85)`
- `fantasma(coll=None, scale=1.0)`
- `pupazzo_neve(coll=None, scale=1.0)`
- `crea(nome, coll=None, scale=None)` — crea l'animale per nome (vedi ANIMALI). scale=None usa la misura naturale accanto a Pippo.

## scripts/paesaggi.py

paesaggi.py - mattoni per posti ricchi e non piatti: terreno con colline, mare, bosco di alberi veri, oggetti sparsi che seguono il terreno,
piu' qualche oggetto costruito a mano (tenda, fuoco, semaforo, strisce pedonali).
Regola dell'autore: un posto non deve sembrare "un mondo piatto di Minecraft". Quindi sempre: rilievo sullo sfondo, alberi realistici,
tanti dettagli vicini (erba, cespugli, sassi), qualcosa in primo piano ai bordi dell'inquadratura.
Uso (dopo kitlook.upgrade):  import paesaggi as PS;  h = PS.colline(amp=6);  PS.terreno(envc, x0, mat, h);  PS.bosco(A, envc, x0, h, ...)

- `sm(x)`
- `onde(x, y, s=1.0)` — rumore morbido tra -1 e 1 fatto di seni: basta per colline e dune.
- `colline(amp=6.0, rx=12.0, ry=10.0, cy=3.0, bordo=16.0, lontano=9.0, fase=0.0)` — altezza(x, y) con x relativo al centro del posto: piano dove recitano i personaggi (ellisse rx, ry), poi colline, poi una cresta lontana.
- `isola(rx=22.0, ry=18.0, cy=6.0, fondo=-2.2, colli=((-15, 16, 7.0, 70.0), (17, 14, 4.5, 45.0)), lontane=((-45, 80, 9.0, 500.0), (55, 100, 7.0, 400.0)))` — altezza(x, y) di un'isola: spiaggia piana al centro, piccole dune, colli (x, y, altezza, larghezza), riva che scende nel mare, isole lontane.
- `terreno(coll, x0, mat, h, xr=(-110, 110), yr=(-30, 190), passo=2.0, nome='Terreno')` — maglia del terreno centrata in x0 con le altezze date da h(x, y). Ombreggiatura morbida.
- `mare(coll, x0, z=-0.35, colore=(0.02, 0.3, 0.48), mezzo=260, nome='Mare')` — piano d'acqua lucido con increspature.
- `posa(objs, x0, h, giu=0.0)` — appoggia gli oggetti sul terreno (z = altezza nel punto).
- `bosco(A, coll, x0, h, specie, quanti, r0=11.0, r1=48.0, alt=(9.0, 14.0), seme=1, rx=1.0, ry=1.0, cy=3.0, a0=-0.25, a1=PI + 0.25, ombra_vicini=0, giu=0.25, evita=())` — anello di alberi realistici (sagome fotografiche) intorno alla scena, appoggiati al terreno. a0..a1: arco in radianti (0 = destra, pi/2 = fondo).
- `tenda(coll, loc, rot=0.0, colore=(0.95, 0.45, 0.08), largo=2.4, lungo=3.0, alto=1.7, nome='Tenda')` — tenda canadese: apertura verso -Y con rot = 0.
- `fuoco(coll, loc, scala=1.0, luce=700.0, nome='Fuoco')` — fiamme stilizzate luminose piu' una luce calda. Restituisce (radice, luce).
- `semaforo(coll, loc, rot=0.0, acceso='verde', nome='Semaforo')` — semaforo su palo: le luci guardano verso -Y con rot = 0.
- `strisce(coll, x0, y0, mezza=6.0, lunghe=3.2, passo=1.1, nome='Strisce')` — strisce pedonali che attraversano una strada lungo X (la strada corre lungo Y).
- `kenney(A, aid, coll, x, y, z=0.0, h=None, w=None, s=None, rot=0.0, rx=0.0)` — modello cartoon del kit (id senza 'kenney/'): h = altezza in metri, w = lato piu' lungo in pianta, s = scala fissa; (x, y) = centro della base.
- `pulisci()` — le copie della stessa texture caricate piu' volte diventano una sola e i dati rimasti orfani vengono liberati: risparmia molta memoria.
- `alleggerisci(radice, lato=512)` — rende definitiva la semplificazione della geometria e rimpicciolisce le texture del modello (lato massimo in pixel).
- `modello(A, coll, x0, h, aid, x, y, alt, rot=0.0, tri=None, z=None, lato=512)` — modello realistico appoggiato al terreno, gia' alleggerito.
- `sparsi(KL, coll, x0, h, aid, n, area, alt, seed, shadow=False, keep=None, via=((0.7, 0.0, 1.6),), lato=512)` — ciuffi, cespugli e fiori sparsi sul terreno (varianti del modello), lontani dai punti 'via' (x, y, raggio). KL = modulo kitlook.
- `sparsi2(A, coll, x0, h, aid, n, area, alt, seed, tri=None, lato=512)` — copie dello stesso modello sparse sul terreno (sassi, cespugli a variante unica).
- `rss()` — memoria usata dal processo, in MB.

## scripts/posti.py

posti.py - posti ricchi costruiti in una scena vuota, senza il quartiere: isola dei pirati, campeggio nel bosco, centro citta'.
Niente mondi piatti: terreno con rilievo, alberi realistici, tanti dettagli vicini, modelli veri dove ci sono, auto grandi.
Come modulo in un episodio:  import posti;  info = posti.isola_pirati(0.0, envc, prc)   ->  dict(h=altezza del terreno, cam=(posizione, mira, lente), luci=[...])
Da terminale, per le schede:  python posti.py N3      (un posto per volta: scrive ../t016/opt3/N3.png)

- `_alb(coll, x0, h, aid, x, y, alt, vista=0, near=False)`
- `_luce(coll, loc, energy, color, r=0.3)`
- `bandiera_pirata(coll, loc, alta=5.2, nome='Bandiera')` — bandiera nera con teschio e ossa su un palo di legno: guarda verso -Y.
- `isola_pirati(x0, envc, prc)` — spiaggia, colli con alberi, scogli, mare, galeone vero, forziere, cannone, botti.
- `campeggio(x0, envc, prc)` — radura tra le colline: abeti e pini veri, sottobosco, fuoco acceso, tende, ceppo con l'ascia, lanterna.
- `citta(x0, envc, prc, M=None, seme=7)` — strada tra palazzi fitti: marciapiedi con lampioni, alberi, panchine, idrante, semafori, strisce, traffico di auto grandi.
- `mats()`
- `T(aid, dim, ril=0.8, tinta=None, **k)` — materiale realistico dalla libreria, creato una volta sola.
- `_casa(coll, loc, rotz, w, d, two, muro, tetto, seme=1, si=0, alto=None)` — casa con finestre, porta e comignolo (stessa geometria del quartiere) con muro e tetto a scelta.
- `_sentiero(coll, x0, h, pts, largo, mat, dz=0.03, nome='Sentiero')` — striscia (vialetto, strada) che segue il terreno lungo i punti (x, y).
- `_disco(coll, cx, cy, z, rx, ry, mat, nome='Disco', n=48, mosso=0.1)`
- `_fiocchi(coll, x0, n=260, seme=3, area=(-12, 12, -6, 24), zr=(0.3, 10.0))`
- `_stelle(coll, x0, n=280, seme=5)`
- `_zucca(coll, loc, s=0.4, rot=0.0)` — zucca di Halloween con la faccia accesa, verso -Y.
- `_lampione(coll, x0, x, y, z, luci, alt=5.2, energia=250.0)`
- `cimitero(x0, envc, prc)` — cimitero al crepuscolo: lapidi di pietra, mausoleo, statua, cancellata, vialetto di ciottoli, lanterne e zucche accese, fantasma, luna.
- `_terra_mat()`
- `razzo(coll, loc, nome='Razzo')` — razzo a mano: corpo bianco lucido, punta e pinne rosse, oblo'. Alto circa 7 m, origine a terra.
- `luna(x0, envc, prc)` — superficie lunare con crateri veri nel terreno, rocce, base a cupole, razzo, bandiera, la Terra nel cielo nero pieno di stelle.
- `neve(x0, envc, prc)` — paesaggio di neve: colline bianche, abeti fitti, lago ghiacciato, baita con le finestre accese, pupazzo di neve, slitta, lampione, fiocchi che cadono.
- `castello(x0, envc, prc)` — castello di pietra su un'altura in fondo a una strada di ciottoli; ai suoi piedi un accampamento: tende, banco del mercato, pozzo, botti, torce, balle di fieno.
- `faro(coll, loc, alto=17.0, nome='Faro')` — faro a fasce bianche e rosse con la lanterna accesa.
- `porto(x0, envc, prc)` — porto antico: banchina di ciottoli, pontile di legno, galeone ormeggiato, altre navi, case colorate, magazzino, botti e casse, lampioni, faro sullo scoglio.
- `ferrovia(x0, envc, prc)` — stazione di campagna: banchina con pensilina, cartello, orologio, panchina; due binari veri con traversine e ghiaia, treno merci e treno veloce, pali della luce, colline e alberi.

## scripts/lookdev.py

Look 2.0: luci morbide, GI/AO, materiali procedurali, fili d'erba, 1080x1920. upgrade(scene) si applica a una scena gia' costruita.

- `_bsdf(m)`
- `_tex(m, scale_big, scale_fine, c0, c1, bump=0.3, rough=None, bands=None, fine=0.45)` — colore = miscela di due toni su rumore grande + fine; rilievo dal rumore fine (o a fasce per le tegole).
- `_var(m, amt=0.12, scale=3.0, bump=0.15, bands=None)`
- `grass_blades(coll, x0, x1, y0, y1, dens=260, seed=1, skip=None)`
- `upgrade(scene, w=1080, h=1920, samples=24, blades=None, exposure=-0.15, rt=True, look='AgX - High Contrast', world=0.5, sun_e=5.5)`

## scripts/kitlook.py

Scelte dell'autore (16 nov 2026): A2 albero largo, B1 prato folto, C5 mattoni rossi, D1 tegole colorate, E2 cielo con nuvole grandi.
kitlook.py - veste le scene di Pippo e Tumbo con la libreria asset (assets/pt_assets.py):
cielo HDRI, prato / asfalto / intonaco / tegole / legno con texture vere, alberi a sagoma, cespugli, fiori, lampioni.
Uso (dopo aver creato la camera):  kitlook.upgrade(scene, M, envc, prc)

- `_k(c, g, sat=1.0)`
- `setmat(o, mat)` — per gli oggetti creati con set004.obj/bx (mesh condivisa, materiale sull'oggetto): MAI A.applica.
- `remap(old, new)`
- `variants(aid, n, area, height, seed=1, coll=None, shadow=True, z=0.0, keep=None)` — sparge n esemplari scegliendo a caso tra le varianti del modello (ciuffi d'erba, fiori, cespugli).
- `tune_cutouts(gain=1.9, sat=1.25)` — sagome: foglie piu' chiare e verdi (le foto sono scure rispetto ai personaggi).
- `add_trees(envc, kinds=TREE_MIX, background=True)` — alberi veri (sagome fotografiche) al posto di quelli a palla: specie, altezze e verso mescolati
- `upgrade(scene, M, envc, prc, sky='sunflowers_puresky', sky_rot=43.0, sky_force=1.1, preset='equilibrato', trees=True, extras=True, exposure=0.25, keep_sun=0.0, grass_dim=3.0, tree_gain=1.9)`

## scripts/render_t004.py


## scripts/trascrivi.py

Trascrive la voce con i tempi di ogni parola.
Uso:  python scripts/trascrivi.py /percorso/voce.mp3 016
Crea: audio/voce_t016.mp3 (copia), audio/voce16_t016.wav (16 kHz mono), audio/words_t016.json = [[inizio, fine, parola], ...]
Serve: pip install faster-whisper ; ffmpeg. Modello: Systran/faster-whisper-small (si scarica da solo la prima volta).


## scripts/kit_options.py

Test 015 - IL PARTO DI ELEONORA. Salva ../t015/pippo_t015.blend
Personaggi: Pippo e Tumbo ESISTENTI (pippo.py, tumbo.py) invariati; Gualtiero = nuovo vicino ricorrente (props009.gualtiero).

- `fr(t)`
- `sm(x)`
- `ramp(t, a, b)`
- `lerp(a, b, u)`
- `add(a, b)`
- `house_at(x, y, rotz, wi, ri, si, two, w=None, d=None)`
- `tower_at(x, y, rz=0.0)`
- `tree(x, y, s=1.0)`
- `qdir(d, rest=(0, 0, -1))`
- `shot(name, cl, tl, lens=26, w=540, h=960, samples=4)`
- `kill(objs)`
- `swap(cur_name, options, cam_a, cam_b, lens, col, gain, sat, dim)`

## scripts/sheet_opts.py

Compone le schede di scelta con etichette: python3 sheet_opts.py

- `font(sz)`

## scripts/sheet_opts3.py

Compone le schede di scelta 3 (altre cose del pacchetto) con etichette: python3 sheet_opts3.py [cose enormi posti animali]

- `font(sz)`

## scripts/foto_pippo.py

Foto di Pippo (e Tumbo) per i quadri del salotto: ../t016/foto_pippo_N.png

- `qdir(d, rest=(0, 0, -1))`

## assets/pt_assets.py

pt_assets.py - Libreria di asset gratuiti (CC0) per i video di Pippo e Tumbo.

Fonti: Poly Haven (modelli 3D realistici, texture PBR, cieli HDRI), ambientCG (materiali PBR, cieli, cibo 3D),
Kenney (4.451 modelli cartoon leggerissimi: case, alberi, auto, mobili, cibo...), KayKit (903 modelli cartoon
piu' morbidi: citta', mobili, cucina, personaggi) e NASA (257 modelli veri: astronauta, razzi, rover, satelliti).
Licenza: CC0 (uso commerciale libero, senza obbligo di citazione). I modelli NASA sono senza copyright:
basta non far sembrare che la NASA sponsorizzi il video.

USO DA TERMINALE (senza Blender):
    python pt_assets.py cerca neve                 # cerca per nome / tag / categoria
    python pt_assets.py cerca albero --tipo modello
    python pt_assets.py cerca casa --origine kenney   # solo i modelli cartoon di Kenney
    python pt_assets.py cerca auto --origine kaykit   # modelli cartoon KayKit
    python pt_assets.py cerca razzo --origine nasa    # modelli veri della NASA
    python pt_assets.py effetti fumo                  # immagini per effetti (fumo, esplosioni, schizzi...)
    python pt_assets.py font                          # font per i sottotitoli
    python pt_assets.py scarica fir_tree_01 Ice003 # scarica (o ri-scarica) asset per nome
    python pt_assets.py scarica-tutto              # ricostruisce l'intera libreria (~18 GB)
    python pt_assets.py scarica-tutto --tipo hdri  # solo un tipo: modello | texture | hdri
    python pt_assets.py stato                      # quanti asset sono gia' su disco
    python pt_assets.py aggiorna-catalogo          # rilegge gli elenchi dalle due fonti (nuovi asset)

USO DENTRO BLENDER (negli script delle scene):
    import pt_assets as A
    A.cielo('snowy_forest_path_01', forza=1.0, rotazione=40)        # luce + sfondo realistico
    ghiaccio = A.materiale('Ice003', dimensione=3.0)                # materiale PBR pronto
    A.applica(pavimento, ghiaccio)
    A.modello('fir_tree_01', posizione=(4, 8, 0), altezza=9)        # albero (versione leggera)
    A.sparpaglia('fir_tree_01', 25, area=(-20, 20, 10, 30), altezza=(7, 11))
    A.albero_cartonato('fir_tree_01', posizione=(0, 30, 0), altezza=12)  # sagoma piatta, senza ombra
    A.bosco_cartonato('fir_tree_01', 40, area=(-30, 30, 25, 45))         # bosco di sfondo fatto di sagome
    A.modello('kaykit/city-builder-bits/car_taxi', altezza=1.5)     # modello cartoon KayKit
    A.modello('nasa/astronaut', altezza=1.9, max_triangoli=40000)   # modello vero della NASA
    A.modello('/percorso/mio_modello.glb', altezza=2)               # un file tuo (glb, gltf, fbx, obj)
    A.effetto('esplosione/explosion03', posizione=(0, 0, 1), larghezza=2, animazione=(40, 14))  # botto
    A.font('LuckiestGuy')                   # percorso del file .ttf per i sottotitoli
    A.qualita_eevee(preset='equilibrato')   # 1080x1920, 6 campioni: il miglior rapporto qualita'/tempo
    A.niente_ombra(terreno, fiocchi)        # oggetti che non devono proiettare ombra

La cartella della libreria e' quella in cui si trova questo file, oppure la variabile
d'ambiente PT_ASSETS. Gli asset mancanti vengono scaricati da soli al primo uso.
Questo file basta da solo: se manca catalogo.json.gz lo ricostruisce dalla rete.

- `catalogo()` — Indice di tutti gli asset: {id: {tipo, nome, categorie, tag, ...}}.
- `aggiorna_catalogo(verboso=True, kenney=True, kaykit=True, nasa=True)` — Ricostruisce catalogo.json.gz interrogando Poly Haven, ambientCG, Kenney, KayKit e NASA
- `info(aid)`
- `percorso(rel)`
- `cerca(*parole, tipo=None, limite=40, solo_presenti=False, origine=None)` — Cerca per parole in id, nome, tag e categorie (in inglese; le parole italiane piu' comuni
- `presente(aid)` — True se i file base dell'asset sono gia' su disco.
- `scarica(aid, verboso=False)` — Si assicura che l'asset sia su disco (scarica solo quello che manca). Restituisce l'info.
- `scarica_hdri(aid, ris='4k')` — Scarica un cielo HDRI a risoluzione piu' alta (2k, 4k, 8k) per usarlo come sfondo nitido.
- `scarica_tutto(tipo=None, thread=10)` — Ricostruisce la libreria (tutti gli asset segnati 'base' nel catalogo).
- `cielo(aid, forza=1.0, rotazione=0.0, ris='auto', sfondo=True, colore_sfondo=(0.5, 0.7, 1.0), ombre_sole=True, scena=None)` — Imposta il cielo HDRI come luce (e sfondo) della scena.
- `qualita_eevee(campioni=None, riflessi=True, scena=None, preset='equilibrato', risoluzione=(1080, 1920))` — Impostazioni Eevee con il miglior rapporto qualita'/tempo trovato con le misure.
- `niente_ombra(*oggetti)` — Toglie la proiezione dell'ombra a oggetti che non ne hanno bisogno (terreno piatto, fiocchi di neve,
- `materiale(aid, dimensione=None, rilievo=1.0, proiezione='box', ruvidita=1.0, tinta=None, vernice=0.0, spostamento=False, nome=None)` — Crea un materiale PBR realistico da una texture (Poly Haven o ambientCG).
- `applica(oggetto, mat)` — Assegna il materiale a un oggetto (sostituisce quelli presenti).
- `modello(aid, posizione=(0, 0, 0), rotazione=0.0, scala=1.0, altezza=None, lod='leggero', max_triangoli=None, variante=None, collezione=None, nome=None, veloce=True, appoggia=None)` — Aggiunge un modello 3D alla scena e restituisce l'oggetto radice (un Empty che lo contiene).
- `accessori(radice, *nomi)` — Oggetti in mano ai personaggi KayKit (spade, scudi, balestre...): di partenza sono nascosti.
- `animazioni(radice)` — Nomi delle animazioni gia' pronte di un personaggio. KayKit (76-95): Idle, Walking_A, Running_A, Cheer,
- `anima(radice, nome, inizio=1, ripeti=1, velocita=1.0)` — Fa partire un'animazione pronta del personaggio dal fotogramma 'inizio'.
- `sparpaglia(aid, quanti, area, altezza=None, scala=(0.85, 1.15), seme=1, lod='leggero', max_triangoli=None, z=0.0, collezione=None)` — Sparge copie di un modello in un rettangolo area=(xmin, xmax, ymin, ymax): bosco, sassi, cespugli.
- `albero_cartonato(aid, posizione=(0, 0, 0), altezza=10.0, rotazione=0.0, verso_camera=True, collezione=None, vista=0, ombra=False)` — Sagoma piatta con la foto dell'albero (sfondo trasparente): realistica da lontano.
- `bosco_cartonato(ids, quanti, area, altezza=(10, 16), seme=1, z=0.0, collezione=None, ombra=False)` — Riempie un rettangolo area=(xmin, xmax, ymin, ymax) di sagome d'albero: uno sfondo di bosco
- `effetti(*parole)` — Nomi degli effetti disponibili (immagini con sfondo trasparente in effetti/), es. 'esplosione/explosion03'.
- `effetto(nome, posizione=(0, 0, 0), larghezza=1.0, colore=None, luce=1.0, opacita=1.0, rotazione=0.0, verso_camera=True, animazione=None, sfumato=True, collezione=None)` — Immagine piatta che brilla di luce propria: fumo, botto, schizzo, stellina, emoticon sopra la testa.
- `font(nome=None)` — Senza argomenti: elenco dei font per i sottotitoli (cartella font/).
