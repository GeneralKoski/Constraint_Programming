# Generazione di Istanze Sudoku - Cose da Fare

## Chiarimenti Preliminari

- [ ] Scrivere al professore per confermare l'effettivo significato del punto 1, dato che il testo ufficiale contiene un probabile errore di copia-incolla che menziona "linear constraints for capacity and cost"
- [ ] Confermare se il dataset Kaggle è richiesto come sorgente delle griglie complete oppure se può essere sostituito da griglie complete autogenerate

## Impostazione di Base

- [ ] Decidere una convenzione di nomi per i modelli MiniZinc, i file dati e il materiale del report
- [ ] Raccogliere eventuali esempi del corso che possano essere riutilizzati come punto di partenza
- [ ] Copiare il testo del progetto Sudoku da `Elly/00_introduction/projects.pdf` (progetto 19) dentro `spec/`, così tutte le assunzioni restano tracciabili
- [ ] Scaricare il Kaggle Sudoku Dataset e salvarlo in `data/raw/`
- [ ] Scrivere un piccolo loader che legga le soluzioni complete dal Kaggle dataset
- [ ] Aggiungere un `README.md` a livello di progetto che documenti come riprodurre l'intera pipeline

## Struttura delle Cartelle

- [ ] Creare `models/` per i file MiniZinc
- [ ] Creare `spec/` per il testo ufficiale del progetto e le note collegate
- [ ] Creare `data/raw/` per il Kaggle dataset originale
- [ ] Creare `data/solved/` per le griglie Sudoku complete estratte dal dataset
- [ ] Creare `data/generated/` per i puzzle generati
- [ ] Creare `data/test/` per istanze Sudoku note usate per validare il solver
- [ ] Creare `scripts/` per il codice di orchestrazione
- [ ] Creare `results/` per benchmark, log e grafici
- [ ] Creare `report/` per il documento finale di 6-10 pagine

## Solver

- [ ] Scrivere un solver Sudoku base in MiniZinc
- [ ] Modellare le righe con `alldifferent`
- [ ] Modellare le colonne con `alldifferent`
- [ ] Modellare i blocchi 3x3 con `alldifferent`
- [ ] Testare il solver su istanze Sudoku note
- [ ] Aggiungere un formato di output chiaro per le griglie

## Generazione di Griglie Complete

- [ ] Adattare il modello in modo che possa generare griglie complete valide di Sudoku
- [ ] Produrre un piccolo insieme di griglie complete di esempio
- [ ] Verificare che le griglie complete generate siano corrette dal punto di vista strutturale
- [ ] Decidere se le griglie complete generate servano solo come fallback oppure facciano parte della pipeline principale

## Generazione dei Puzzle

- [ ] Definire come rimuovere gli indizi da una griglia completa
- [ ] Implementare una prima strategia semplice di rimozione degli indizi
- [ ] Produrre puzzle incompleti di esempio
- [ ] Verificare che i puzzle generati restino input validi per il solver

## Unicità

- [ ] Definire come verificare se un puzzle generato ha una soluzione unica
- [ ] Implementare un primo workflow di controllo dell'unicità basato su solve-and-block
- [ ] Implementare un controllo alternativo dell'unicità basato sul conteggio delle soluzioni (trovare al massimo le prime 2)
- [ ] Documentare i limiti di eventuali approcci basati su ragionamento implicito, solo come punto di discussione
- [ ] Separare chiaramente la fase di solving dalla fase di controllo dell'unicità
- [ ] Testare il controllo di unicità su più puzzle generati
- [ ] Confrontare le strategie di unicità in termini di tempo di esecuzione e affidabilità

## Orchestrazione della Pipeline

- [ ] Scrivere uno script Python che gestisca l'intera pipeline di generazione
- [ ] Lo script dovrà: caricare una griglia completa, rimuovere indizi, chiamare MiniZinc per il controllo di unicità, accettare o annullare ogni rimozione
- [ ] Rendere l'ordine di rimozione configurabile, in modo da poter testare strategie diverse
- [ ] Rendere configurabili dallo script il solver MiniZinc e il timeout
- [ ] Registrare nei log ogni rimozione accettata e rifiutata, per debug e analisi successive
- [ ] Salvare i puzzle generati in un formato testuale stabile

## Minimizzazione degli Indizi

- [ ] Implementare una strategia casuale di rimozione degli indizi come baseline
- [ ] Implementare una strategia di rimozione attenta alle simmetrie
- [ ] Implementare una strategia di rimozione attenta alla densità
- [ ] Registrare il numero finale di indizi rimanenti per ogni istanza generata
- [ ] Produrre un grafico del tempo in funzione degli indizi rimanenti, come richiesto dalla specifica
- [ ] Registrare quante chiamate al controllo di unicità sono state necessarie per ogni istanza finale

## Miglioramenti

- [ ] Provare diverse strategie di ricerca
- [ ] Testare se vincoli ridondanti aiutano le prestazioni
- [ ] Confrontare diverse strategie di generazione
- [ ] Valutare quanti indizi possano essere rimossi mantenendo l'unicità
- [ ] Confrontare un modello semplice con un modello più forte che usa annotazioni di search esplicite

## Esperimenti

- [ ] Preparare un benchmark di puzzle generati a partire dal Kaggle dataset
- [ ] Eseguire tutti gli esperimenti con timeout di 5 minuti per test, se questo requisito verrà confermato nel testo ufficiale
- [ ] Registrare tempi di esecuzione e comportamento del solver
- [ ] Confrontare almeno due varianti del modello o del workflow
- [ ] Riassumere i principali risultati empirici
- [ ] Separare chiaramente gli esperimenti di correttezza dagli esperimenti di performance

## Report e Preparazione all'Orale

- [ ] Scrivere una struttura per il report di progetto
- [ ] Verificare che il report finale sia di 6-10 pagine, se questo requisito verrà confermato nel testo ufficiale
- [ ] Documentare le scelte di modellazione
- [ ] Documentare la strategia di unicità e il confronto tra le alternative
- [ ] Documentare le strategie di rimozione degli indizi e l'analisi tempo vs indizi
- [ ] Preparare alcuni esempi rappresentativi da mostrare all'esame orale
- [ ] Preparare una breve spiegazione del motivo per cui questo progetto è più di un semplice solver di Sudoku
- [ ] Ripassare il teorema di Régin e l'algoritmo di filtering dietro `alldifferent`
- [ ] Ripassare la NP-completezza del Sudoku generalizzato e la natura `#P`-completa del conteggio delle soluzioni
- [ ] Ripassare la forza dei propagatori: AC vs bounds consistency su Sudoku, come discusso nelle lezioni 7, 10 e 11

## Confezionamento Finale

- [ ] Raccogliere modelli, script, dataset, istanze generate, risultati e report in un unico file zip
- [ ] Verificare che lo zip sia autosufficiente e che la pipeline possa essere riprodotta a partire da esso

## Milestone

- [ ] Milestone 1: solver Sudoku funzionante
- [ ] Milestone 2: controllo di unicità funzionante
- [ ] Milestone 3: pipeline di rimozione degli indizi funzionante
- [ ] Milestone 4: generatore pronto per i benchmark
- [ ] Milestone 5: report completo e preparazione all'orale
