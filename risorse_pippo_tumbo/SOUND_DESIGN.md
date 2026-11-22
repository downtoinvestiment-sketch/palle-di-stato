# Sound design e musica — Pippo e Tumbo

Direzione data dall'autore il 17 novembre 2026. Vale per tutti i video e si somma al Master Prompt 2.0: **ogni copione deve avere anche una SOUND DESIGN TIMELINE** (vedi punto 7).

## Testo dell'autore

**SOUND DESIGN & MUSIC DIRECTION — PIPPO E TUMBO**

Agisci come un Sound Designer professionista specializzato in animazione comica, cartoon, YouTube Shorts e retention. L'obiettivo è progettare un'esperienza sonora estremamente dinamica, capace di mantenere alta l'attenzione dello spettatore dall'inizio alla fine.

1. **Principio fondamentale.** La musica non deve limitarsi ad accompagnare le immagini: deve amplificare la comicità, creare aspettative, manipolare le emozioni e rendere i colpi di scena memorabili. Ogni cambiamento narrativo importante deve avere una precisa conseguenza sonora. Evita una colonna sonora piatta, ripetitiva o sempre uguale.
2. **Gestione musicale.** Usa dinamicamente: COMEDY (pizzicati, xilofoni, tromboni, ritmi buffi), SUSPENSE (tensione crescente, note ripetute, droni, suoni misteriosi), EPIC (orchestra, ottoni, percussioni, cori per escalation assurde), CHAOS (frenetica, ritmi imprevedibili, cambi improvvisi), DRAMATIC (musica eccessivamente seria per situazioni stupide), SILENCE (interruzioni improvvise per aumentare l'impatto delle gag).
3. **Colpi di scena.** Ogni twist è progettato musicalmente: 1) preparazione con tensione crescente; 2) micro-pausa subito prima della rivelazione; 3) impatto (cinematic boom, bass hit, orchestral hit); 4) reazione, anche cambiando genere musicale; 5) secondo twist con un ulteriore cambio sonoro. Non usare sempre la stessa formula.
4. **Effetti sonori** sincronizzati con le azioni, precisi e mai casuali: whoosh per movimenti rapidi, bass drop per rivelazioni, cartoon boing per gag fisiche, record scratch per interruzioni, cinematic impact per eventi enormi, riser per anticipare, glitch per eventi assurdi, suoni ambientali per rendere credibile il mondo.
5. **Retention.** Nei primi 2 secondi un evento sonoro interessante; niente introduzioni musicali lente; variazioni frequenti quando la storia le giustifica; nessuna traccia invariata per tutto il video; alternare pieni e silenzi; gli impatti più forti solo nei momenti più importanti; non anticipare musicalmente ogni gag, alcune devono sorprendere.
6. **Identità sonora.** Quattro famiglie musicali ricorrenti: tema comico, tema suspense, tema epico, tema del caos e dei doppi twist. Coerenti con l'universo di Pippo e Tumbo, ma possono cambiare radicalmente quando la situazione degenera.
7. **Output obbligatorio.** Con ogni copione una sezione SOUND DESIGN TIMELINE: per ogni momento timestamp preciso, musica, tipo di effetto, entrata e uscita, intensità relativa, eventuale silenzio, motivazione narrativa.
8. **Regole finali.** Non sovraccaricare ogni secondo; la musica valorizza la narrazione e non compete con la voce. Priorità: 1) comprensibilità della scena, 2) impatto comico, 3) sorprendere, 4) ritmo narrativo, 5) identità sonora. Il risultato deve sembrare una produzione animata professionale con tempi comici precisissimi.

## Come si applica nel progetto

**Le quattro famiglie (brani di Kevin MacLeod in `audio/musica`, da citare nella descrizione):**

| Famiglia | Brano principale | Alternative |
| --- | --- | --- |
| Comico (tema di Pippo) | «Sneaky Snitch» | «Monkeys Spinning Monkeys», «Fluffing a Duck», «Scheming Weasel» |
| Suspense | «Spy Glass» | «Thief in the Night», «Hitman» |
| Epico | «Strength of the Titans» | «Five Armies», «Heroic Age» |
| Caos e doppi twist | «Galactic Rap» | «Circus of Freaks», «Hall of the Mountain King» |

Per variare tra un video e l'altro si cambia brano dentro la stessa famiglia, non la famiglia.

**Strumenti:** `scripts/audio017.py` è il modello. Contiene: `boom` (impatto cinematografico), `bass_drop`, `riser`, `whoosh`, `boing`, `glitch`, `grilli` (silenzio comico), `colpo_orchestra`, `stacco_drammatico` (accordo grave + timpani), `dun`, `trombetta`, `fischietto`, `tape_stop` (la musica si ferma come un giradischi), `ovatta` (musica dietro una porta), più il limitatore finale e l'abbassamento automatico della musica sotto la voce. Gli effetti registrati sono quelli Kenney di `audio/sfx/kenney` (record scratch = `scratch_00N`).

**Livelli di riferimento (RMS, misurati dallo script):** voce 0,09-0,18; musica sotto la voce 0,02-0,05; impatti solo sui colpi di scena principali.

## Sound design timeline del video 017 «Il bambino non esce»

| Tempo | Musica | Effetto | Intensità | Perché |
| --- | --- | --- | --- | --- |
| 00:00 | EPICO entra subito | colpo d'orchestra + sirena | alta | evento sonoro nei primi 2 s: un camion dei pompieri |
| 00:02 | l'epico si ovatta e si abbassa | whoosh, pop, boing | media | la musica viene risucchiata con il camion |
| 00:03.9 | stop | porta che sbatte + boom corto | alta, poi silenzio | «e non è più uscito» nel vuoto |
| 00:05.6 | COMICO basso | — | bassa | si torna indietro: la storia comincia |
| 00:10.3 | micro-pausa del comico | clac del cartello | media | «Occupato» |
| 00:13-15 | comico | boing della manina, whoosh del panino, pop | media | gag fisiche |
| 00:17.9 | stop secco | grilli | silenzio | «Tumbo non torna» |
| 00:19.1 | SUSPENSE | bip del telefono, passi, riser | media in salita | arriva la polizia |
| 00:21.4 | stop | un colpo grave (dun) | media | «Non torna» |
| 00:22.4 | EPICO più forte | sirena | alta | «Chiama i pompieri!» |
| 00:23.8 | epico | boom cinematografico + colpo d'orchestra + macerie | massima | il camion sfonda il muro |
| 00:25.2 | l'epico si ovatta e si spezza | whoosh + glitch + pop | media | anche il camion viene risucchiato |
| 00:25.4 | SILENZIO totale | solo la pagina della rivista | minima | «Indovinate» |
| 00:26.6 | bordone di tensione | riser fino al tuffo | in salita | «Allora entra Pippo» |
| 00:27.8 | silenzio (buio) | pop e porta | — | micro-pausa prima della rivelazione |
| 00:28.1 | CAOS ovattato da dentro | — | bassa | «Ma che c***o» |
| 00:29.6 | CAOS esplode | bass drop + boom + scintille | massima | «Una DISCOTECA!» |
| 00:31-32 | caos | risatine dei neonati, fischietto | media | gag |
| 00:33.5 | stop di un attimo | record scratch, poi trombetta + boom | alta | secondo twist: «il DJ è Tumbo» |
| 00:35.2 | il disco si ferma (tape stop) | passi pesanti | media | arriva il buttafuori |
| 00:37.2 | caos lontano, ovattato | stacco drammatico (accordo grave + timpani) | alta | «Gualtiero», serissimo per una cosa stupida |
| 00:38.7 | — | cartellina, ronzio di errore | bassa | «Pippo non è in lista» |
| 00:39.8 | caos dietro la porta | porta che sbatte, cartello, pagina | media, poi sfuma | finale secco |
