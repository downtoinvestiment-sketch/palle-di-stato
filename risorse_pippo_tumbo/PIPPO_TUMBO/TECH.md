# Documentazione tecnica dell'agenzia

Audit del 19 novembre 2026 (Fase A del brief), interrotto su richiesta dell'autore prima delle analytics. Qui ci sono solo cose verificate.

## Dove si produce: ambiente cloud

| Voce | Stato verificato |
| --- | --- |
| Processori e memoria | 2 core, 7,8 GB di RAM, nessuna GPU |
| Disco | 4,5 GB liberi; 21 GB sono la libreria scaricata (`/home/claude/pippo_assets`). Dopo ogni video vanno cancellati i fotogrammi |
| Blender | `bpy` 5.3.0 con Python 3.13, render Eevee funzionante |
| Librerie | numpy 2.5.3, Pillow 12.3.0, faster-whisper 1.2.1, ffmpeg 6.1.1, git 2.43 |
| Repository | `downtoinvestiment-sketch/pippo-tumbo-video`, push funzionante |
| Tempi di render | circa 20 s a fotogramma a 1080x1920 con 6 campioni (misure del LEGGIMI): un video da 40 s richiede 5–6 ore |

## Librerie di animazione

- **Personaggi della serie:** Pippo, Tumbo, Gualtiero, Giulia, Eleonora e gli animali si animano con chiavi scritte dagli script (`scripts/animNNN_body.py`), con le emozioni di `pippo2` ed `eleonora`.
- **Comparse già animate:** KayKit (76 animazioni) e Kenney mini-characters (32 animazioni), dalla libreria asset.
- **Fuori da questo repository:** il modulo `cartoon_character` (repository lume-studio, ramo `cartoon-character`) ha 31 movimenti, retargeting di mocap BVH e FBX e controllo delle collisioni, ma su uno scheletro diverso: per Pippo servirebbe un adattamento.

## Computer dell'autore (collegato tramite l'app desktop)

| Voce | Stato verificato |
| --- | --- |
| Sistema | Windows x64 |
| Cartelle collegate | nessuna: per leggere o scrivere file locali l'autore deve collegarne una |
| Blender | installato: `C:\Program Files\Blender Foundation\Blender 5.2` |
| Scheda grafica | non verificata; tra i programmi non ci sono cartelle NVIDIA o AMD (ipotesi: grafica integrata) |
| Altri programmi | tra gli altri Git, Chrome, MATLAB, Microsoft Office |

## Browser e account

- **Claude in Chrome:** collegato. TikTok Studio è aperto con l'account @pippoetumbo; YouTube Studio mostra il canale personale dell'autore, vuoto. L'autore ha chiesto di non analizzare gli account esistenti.
- **Meta Business Suite e Instagram:** non controllati.

## Connettori

- **vidIQ:** autorizzato solo per il canale Lumeconomy.
- **Metricool:** un solo brand, con gli account Lumeconomy.
- **Canale nuovo:** andrà collegato a vidIQ e a Metricool, oppure i dati si leggeranno da Chrome.

## Cosa si può automatizzare

- **Da solo:** ricerca, copioni, schede di opzioni, scene Blender, fotogrammi di prova, render, audio, sottotitoli, montaggio, controllo dei mosaici, titoli, descrizioni, hashtag, copertine, database e report.
- **Con l'autore:** la voce (ElevenLabs, sul suo account), le scelte dalle schede, l'approvazione di ogni pubblicazione.
- **Pubblicazione:** solo dopo l'approvazione, da Chrome o con un connettore di programmazione.
