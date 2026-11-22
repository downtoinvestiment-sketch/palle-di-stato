# Palle di stato

Video satirici di geopolitica e politica italiana con le «palle di stato» (countryball) in Blender.

## Cosa c'è

**Per tenere l'attenzione:** `ATTENZIONE.md` (regole di struttura, hook, colpi di scena, ritmo, regia, luce, suono e pubblicazione prese da Pippo e Tumbo, senza le cose personalizzate per quel canale). Istruzioni per Claude in `CLAUDE.md`.

| Cartella | Contenuto |
|---|---|
| `palle.py` | Generatore di palle di stato: qualsiasi bandiera, occhi da cartone, espressioni (normale, felice, arrabbiato, triste, sorpreso, furbo, annoiato), sguardo. `python3 palle.py` crea `prova_palle.png`. |
| `modelli_satira/bandiere/` | Bandiere di 271 paesi (flag-icons, licenza MIT) in SVG e PNG 1024×768, più `paesi.json` con nomi, capitali e continenti. |
| `modelli_satira/polyhaven/` | 42 modelli 3D CC0 di Poly Haven (glTF 1k): ufficio e governo, palazzo e vertici, comunicazione (megafono, TV, telecamere), soldi e commercio (barili, registratore di cassa, nave), confini (transenne, recinzione, cancello), cibo. Elenco in `elenco.json`. |
| `strumenti/` | Script per riscaricare bandiere (`scarica_bandiere.py`) e modelli Poly Haven (`scarica_polyhaven.py`, accetta altri id). |
| `risorse_pippo_tumbo/` | Copia completa delle risorse di Pippo e Tumbo: personaggi (`scripts/pippo.py`, `pippo2.py`, `tumbo.py` e gli altri), libreria asset con tutti i modelli e le texture scaricate, mocap, canzone di Pippo, voci, musiche, effetti, copioni e documenti. `extra_machescienza/` contiene gli script del video «popstar che raddoppia». |

## Personaggi politici

| Personaggio | File | Note |
|---|---|---|
| La Signora Platino (nome provvisorio) | `risorse_pippo_tumbo/scripts/platino.py` | Politica biondo platino, occhi azzurro-grigio, alta 165 cm. Versione scelta: A (blazer azzurro polvere). Scheda: `python risorse_pippo_tumbo/scripts/scheda_platino.py [A B C]` → `risorse_pippo_tumbo/schede/platino_versioni.jpg`. Personaggio inventato. |
| Admin World | `risorse_pippo_tumbo/scripts/admin_world.py` | Politico con i capelli grigio-argento pettinati all'indietro e il ciuffo di lato, fronte molto alta, naso e orecchie molto grandi, mento quadrato, completo blu notte. Alto 180 cm. Scheda: `python risorse_pippo_tumbo/scripts/scheda_admin_world.py [A B C]` → `risorse_pippo_tumbo/schede/admin_world_versioni.jpg`. Emozioni: `scheda_admin_world_emozioni.py` → `schede/admin_world_emozioni.jpg`. Movimenti pronti: `aw.motion(W, f0, 'parla'|'respira'|'comizio'|'nega'|'annuisce')`, prova in `video/admin_world_motion.mp4`. Personaggio inventato. |

## Licenze
- Bandiere: flag-icons, MIT (vedi `modelli_satira/bandiere/LICENSE_flag-icons.txt`).
- Modelli Poly Haven: CC0.
- Le risorse di Pippo e Tumbo seguono le licenze indicate in `risorse_pippo_tumbo/assets/LEGGIMI.md`.
