# Generazione di Istanze Sudoku

## Obiettivo

Il progetto si concentra sulla modellazione e sulla generazione di istanze di Sudoku con Constraint Programming, usando MiniZinc come linguaggio principale.

In base alla descrizione del progetto attualmente disponibile, le istanze 9x9 generate devono:

- Avere almeno una soluzione valida
- Avere esattamente una soluzione ammissibile (unicità)
- Contenere il minor numero possibile di indizi iniziali (celle precompilate), mantenendo l'unicità

L'idea centrale non è solo risolvere una griglia Sudoku, ma studiare come:

- Generare una soluzione completa valida di Sudoku
- Rimuovere indizi per ottenere un puzzle
- Verificare che il puzzle generato resti valido
- Imporre o verificare l'unicità della soluzione
- Minimizzare il numero di indizi mantenuti nell'istanza finale
- Confrontare diverse scelte di modellazione e di ricerca

## Perché Questo Progetto È Interessante

Questo progetto è molto adatto al corso perché combina:

- Modellazione classica di CSP
- Vincoli globali come `alldifferent`
- Scelte sulle strategie di ricerca
- Qualità della propagazione
- Generazione, non solo semplice solving
- Un livello ulteriore di difficoltà dato dal controllo di unicità

Per questo motivo è più ricco di un semplice solver di Sudoku e offre materiale sufficiente sia per l'implementazione sia per la discussione orale.

## Direzione Tecnica Principale

Il progetto può essere sviluppato per fasi.

### 1. Solver Sudoku

Per prima cosa, bisogna costruire un modello MiniZinc pulito per risolvere Sudoku:

- Griglia 9x9 di variabili decisionali
- Domini `1..9`
- `alldifferent` sulle righe
- `alldifferent` sulle colonne
- `alldifferent` su ogni blocco 3x3

Questa parte costituisce la base per tutto il lavoro successivo.

### 2. Generazione di Griglie Complete

Una volta che il solver è corretto, le griglie complete valide di Sudoku possono essere ottenute in due modi:

- Generate direttamente dal solver
- Caricate da un dataset esterno di griglie già risolte

Entrambi gli approcci sono ragionevoli. Il secondo di solito è migliore per gli esperimenti, perché separa la generazione del puzzle dalla costruzione della griglia completa.

### 3. Generazione del Puzzle

Partendo da una griglia completa valida, si rimuovono alcuni valori e si mantengono gli altri come indizi.

L'obiettivo è ottenere un'istanza Sudoku giocabile, non solo una soluzione completa.

### 4. Controllo di Unicità

Il passaggio avanzato più importante è verificare che il puzzle generato abbia una soluzione unica.

È questo che rende il progetto significativamente più interessante del normale solving di Sudoku. Inoltre fornisce un punto teorico e pratico forte da discutere all'esame.

In base al testo del progetto attualmente disponibile, un obiettivo rilevante è valutare diverse strategie per verificare l'unicità della soluzione. I principali approcci da confrontare sono:

- Solve-and-block: si trova una soluzione, si aggiunge un vincolo che la proibisce, poi si cerca di nuovo. Se la seconda ricerca restituisce UNSAT, il puzzle è unico.
- Conteggio delle soluzioni: si enumerano le soluzioni usando il flag del solver per trovare tutte le soluzioni, fermandosi non appena se ne trova una seconda.
- Ragionamento implicito: si usa la propagazione per argomentare l'unicità senza enumerazione completa. Questo approccio è corretto solo in casi limitati ed è soprattutto interessante da discutere come limite.

In pratica, il progetto dovrebbe basarsi sui primi due approcci. Il terzo è soprattutto un punto di discussione teorico.

### 5. Minimizzazione degli Indizi

Una volta che l'unicità può essere verificata, il flusso di lavoro dovrebbe puntare a produrre puzzle con il minor numero possibile di indizi, mantenendo la soluzione unica. Questa parte si collega direttamente all'interpretazione attuale del requisito di progetto:

- Rimuovere iterativamente indizi da una griglia completa
- Dopo ogni rimozione, eseguire il controllo di unicità
- Accettare la rimozione solo se il puzzle resta risolvibile in modo univoco
- Confrontare diverse strategie di rimozione (ordine casuale, attento alle simmetrie, attento alla densità)

Nel report finale bisogna collegare chiaramente il numero di indizi rimanenti con il tempo necessario per verificare l'unicità.

### 6. Confronto Sperimentale

Dopo che la versione base funziona, conviene confrontare:

- Diverse annotazioni di search
- Diverse strategie di rimozione degli indizi
- Diversi livelli di ridondanza nel modello
- Tempi di esecuzione e comportamento del solver su più istanze generate
- Tempo in funzione del numero di indizi rimanenti, come richiesto dalla specifica del progetto

Se il testo del progetto viene confermato come letto correttamente, il benchmark dovrebbe essere eseguito con un timeout di 5 minuti per test.

## Deliverable Attesi

La consegna finale consiste in un unico file zip contenente modelli, script, dataset, istanze generate, risultati e un report scritto di 6-10 pagine.

Per l'elenco completo dei deliverable e per i punti ancora da confermare rispetto al testo ufficiale del progetto, vedi [03_spec_notes.md](03_spec_notes.md).

## Valore per l'Orale

Questo progetto è molto adatto per l'esame orale perché permette di discutere:

- Scelte di modellazione CSP
- Ruolo dei vincoli globali, in particolare `alldifferent`
- Teorema di Régin e algoritmo di filtering dietro `alldifferent`
- Propagazione ed efficienza del solver, inclusi AC e bounds consistency su Sudoku
- Euristiche di ricerca
- Differenza tra solving e generation
- Come l'unicità cambia la struttura del problema
- Osservazioni di complessità: NP-completezza del Sudoku generalizzato e natura `#P`-completa del conteggio delle soluzioni

In sintesi, il progetto dovrebbe essere presentato come un progetto di Constraint Programming sulla generazione di Sudoku, non solo sul solving di Sudoku.

## Note Correlate

Il materiale più dettagliato è diviso nei seguenti file:

- [02_todo.md](02_todo.md): checklist di implementazione e milestone
- [03_spec_notes.md](03_spec_notes.md): note sul testo ufficiale del progetto, dataset, deliverable, vincoli sperimentali e assunzioni
- [04_architecture_and_risks.md](04_architecture_and_risks.md): architettura, separazione del workflow, strategie di unicità e principali rischi tecnici
