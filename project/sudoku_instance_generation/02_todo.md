# Generazione di Istanze Sudoku - Cose da Fare

## Chiarimenti Preliminari

- [ ] Scrivere al professore per confermare l'effettivo significato del punto 1, dato che il testo ufficiale contiene un probabile errore di copia-incolla che menziona "linear constraints for capacity and cost"
- [ ] Confermare se il dataset Kaggle è richiesto come sorgente delle griglie complete oppure se può essere sostituito da griglie complete autogenerate

## Impostazione di Base

- [x] Decidere una convenzione di nomi per i modelli MiniZinc, i file dati e il materiale del report
- [x] Raccogliere eventuali esempi del corso che possano essere riutilizzati come punto di partenza
- [x] Copiare il testo del progetto Sudoku da `Elly/00_introduction/projects.pdf` (progetto 19) dentro `spec/`, così tutte le assunzioni restano tracciabili
- [ ] Scaricare il Kaggle Sudoku Dataset e salvarlo in `data/raw/`
- [x] Scrivere un piccolo loader che legga le soluzioni complete dal Kaggle dataset
- [x] Aggiungere un `README.md` a livello di progetto che documenti come riprodurre l'intera pipeline

## Struttura delle Cartelle

- [x] Creare `models/` per i file MiniZinc
- [x] Creare `spec/` per il testo ufficiale del progetto e le note collegate
- [x] Creare `data/raw/` per il Kaggle dataset originale
- [x] Creare `data/solved/` per le griglie Sudoku complete estratte dal dataset
- [x] Creare `data/generated/` per i puzzle generati
- [x] Creare `data/test/` per istanze Sudoku note usate per validare il solver
- [x] Creare `scripts/` per il codice di orchestrazione
- [x] Creare `results/` per benchmark, log e grafici
- [x] Creare `report/` per il documento finale di 6-10 pagine

## Solver

- [x] Scrivere un solver Sudoku base in MiniZinc
- [x] Modellare le righe con `alldifferent`
- [x] Modellare le colonne con `alldifferent`
- [x] Modellare i blocchi 3x3 con `alldifferent`
- [x] Testare il solver su istanze Sudoku note
- [x] Aggiungere un formato di output chiaro per le griglie

## Generazione di Griglie Complete

- [x] Adattare il modello in modo che possa generare griglie complete valide di Sudoku
- [x] Produrre un piccolo insieme di griglie complete di esempio
- [x] Verificare che le griglie complete generate siano corrette dal punto di vista strutturale
- [x] Decidere se le griglie complete generate servano solo come fallback oppure facciano parte della pipeline principale

## Generazione dei Puzzle

- [x] Definire come rimuovere gli indizi da una griglia completa
- [x] Implementare una prima strategia semplice di rimozione degli indizi
- [x] Produrre puzzle incompleti di esempio
- [x] Verificare che i puzzle generati restino input validi per il solver

## Unicità

- [x] Definire come verificare se un puzzle generato ha una soluzione unica
- [x] Implementare un primo workflow di controllo dell'unicità basato su solve-and-block
- [x] Implementare un controllo alternativo dell'unicità basato sul conteggio delle soluzioni (trovare al massimo le prime 2)
- [x] Documentare i limiti di eventuali approcci basati su ragionamento implicito, solo come punto di discussione
- [x] Separare chiaramente la fase di solving dalla fase di controllo dell'unicità
- [x] Testare il controllo di unicità su più puzzle generati
- [x] Confrontare le strategie di unicità in termini di tempo di esecuzione e affidabilità

## Orchestrazione della Pipeline

- [x] Scrivere uno script Python che gestisca l'intera pipeline di generazione
- [x] Lo script dovrà: caricare una griglia completa, rimuovere indizi, chiamare MiniZinc per il controllo di unicità, accettare o annullare ogni rimozione
- [x] Rendere l'ordine di rimozione configurabile, in modo da poter testare strategie diverse
- [x] Rendere configurabili dallo script il solver MiniZinc e il timeout
- [x] Registrare nei log ogni rimozione accettata e rifiutata, per debug e analisi successive
- [x] Salvare i puzzle generati in un formato testuale stabile

## Minimizzazione degli Indizi

- [x] Implementare una strategia casuale di rimozione degli indizi come baseline
- [x] Implementare una strategia di rimozione attenta alle simmetrie
- [x] Implementare una strategia di rimozione attenta alla densità
- [x] Registrare il numero finale di indizi rimanenti per ogni istanza generata
- [x] Produrre un grafico del tempo in funzione degli indizi rimanenti, come richiesto dalla specifica
- [x] Registrare quante chiamate al controllo di unicità sono state necessarie per ogni istanza finale

## Miglioramenti

- [x] Provare diverse strategie di ricerca
- [x] Testare se vincoli ridondanti aiutano le prestazioni
- [x] Confrontare diverse strategie di generazione
- [x] Valutare quanti indizi possano essere rimossi mantenendo l'unicità
- [x] Confrontare un modello semplice con un modello più forte che usa annotazioni di search esplicite

## Esperimenti

- [x] Preparare un benchmark di puzzle generati a partire dal Kaggle dataset
- [ ] Eseguire tutti gli esperimenti con timeout di 5 minuti per test, se questo requisito verrà confermato nel testo ufficiale
- [x] Registrare tempi di esecuzione e comportamento del solver
- [x] Confrontare almeno due varianti del modello o del workflow
- [x] Riassumere i principali risultati empirici
- [x] Separare chiaramente gli esperimenti di correttezza dagli esperimenti di performance

## Report e Preparazione all'Orale

- [x] Scrivere una struttura per il report di progetto
- [ ] Verificare che il report finale sia di 6-10 pagine, se questo requisito verrà confermato nel testo ufficiale
- [x] Documentare le scelte di modellazione
- [x] Documentare la strategia di unicità e il confronto tra le alternative
- [x] Documentare le strategie di rimozione degli indizi e l'analisi tempo vs indizi
- [x] Preparare alcuni esempi rappresentativi da mostrare all'esame orale
- [x] Preparare una breve spiegazione del motivo per cui questo progetto è più di un semplice solver di Sudoku
- [x] Ripassare il teorema di Régin e l'algoritmo di filtering dietro `alldifferent`
- [x] Ripassare la NP-completezza del Sudoku generalizzato e la natura `#P`-completa del conteggio delle soluzioni
- [x] Ripassare la forza dei propagatori: AC vs bounds consistency su Sudoku, come discusso nelle lezioni 7, 10 e 11

## Confezionamento Finale

- [x] Raccogliere modelli, script, dataset, istanze generate, risultati e report in un unico file zip
- [x] Verificare che lo zip sia autosufficiente e che la pipeline possa essere riprodotta a partire da esso

## Milestone

- [x] Milestone 1: solver Sudoku funzionante
- [x] Milestone 2: controllo di unicità funzionante
- [x] Milestone 3: pipeline di rimozione degli indizi funzionante
- [x] Milestone 4: generatore pronto per i benchmark
- [x] Milestone 5: report completo e preparazione all'orale
