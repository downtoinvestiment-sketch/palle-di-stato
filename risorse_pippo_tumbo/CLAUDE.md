# Pippo e Tumbo — istruzioni per Claude

Serie di video verticali 3D in Blender (Python `bpy`, Eevee) con Pippo e il cane Tumbo.

1. Leggi `LEGGIMI_CLAUDE.md` prima di fare qualsiasi cosa: spiega ambiente, flusso di lavoro, file e stato dei lavori.
2. Per i copioni leggi `MASTER_PROMPT_2.md` e poi `BIBBIA.md`. I copioni già scritti sono in `COPIONI.md`.
3. Rispondi in italiano, con messaggi corti: l'autore scrive dal telefono.
4. `scripts/pippo.py` e `scripts/tumbo.py` non si modificano mai.
5. Usa sempre la libreria asset (`assets/pt_assets.py`) e fai scegliere all'autore texture e oggetti da una scheda di immagini prima di costruire un video.
6. Se un render si interrompe, riprendilo da solo fino alla fine.
7. Dopo ogni modifica fai commit e push su questo repository, senza aspettare che l'autore lo chieda.
8. Illuminazione: usa sempre la luce «cinema» (`scripts/luci.py`): luce principale calda di lato con ombre nette, riempimento freddo e debole, controluce azzurro, poca luce ambiente. Mai la luce piatta tutta dall'alto.
9. Suono: segui `SOUND_DESIGN.md`. Ogni copione ha anche la SOUND DESIGN TIMELINE; ogni colpo di scena ha la sua conseguenza sonora (preparazione, micro-pausa, impatto, cambio di musica); quattro famiglie musicali fisse; silenzi veri; la musica non copre mai la voce.
10. Insulti e parolacce: SEMPRE, in ogni copione (regola dell'autore, 18 novembre 2026; hook cambiato il 19 novembre 2026). Insulti secchi e sempre diversi a tutti i personaggi (Pippo, Tumbo, Gualtiero, Giulia, Eleonora, la polizia), e ogni insulto contiene una parolaccia («quel pendolare di merda», «quel bastardo del cazzo»); parolacce come punchline lungo tutto il video. Nella prima frase niente insulti pesanti (al massimo uno leggero e simpatico) e niente situazione bizzarra: l'hook crea attesa (una cosa grossa che sta per succedere) e la stranezza arriva subito dopo. Nei sottotitoli si censurano con gli asterischi. Restano fuori solo gli insulti a categorie di persone e le gag sessuali su Pippo.
