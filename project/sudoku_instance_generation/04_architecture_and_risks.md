# Generazione di Istanze Sudoku - Architettura e Rischi

## Architettura Consigliata

Un'implementazione pulita può essere divisa nelle seguenti parti:

- Un modello MiniZinc per risolvere e validare istanze Sudoku
- Un modello MiniZinc o una configurazione dedicata ai test di unicità
- Uno script di orchestrazione che rimuove indizi e invoca ripetutamente MiniZinc
- Una cartella dati contenente griglie complete risolte e puzzle generati
- Una cartella risultati contenente tempi, statistiche e grafici

Questa separazione è importante perché la rimozione degli indizi è procedurale, mentre fattibilità e unicità del Sudoku vengono delegate al solver CP.

## Sorgenti delle Griglie Complete

Una volta che il solver è corretto, le griglie complete valide di Sudoku possono essere ottenute in due modi:

- Generate direttamente dal solver
- Caricate da un dataset esterno di griglie già risolte

Entrambi gli approcci sono ragionevoli. Il secondo di solito è migliore per gli esperimenti, perché separa la generazione del puzzle dalla costruzione della griglia completa.

## Strategie di Unicità

I principali approcci che vale la pena confrontare sono:

- Solve-and-block: trovare una soluzione, aggiungere un vincolo che la proibisce, poi cercare di nuovo
- Conteggio delle soluzioni: enumerare le soluzioni e fermarsi non appena se ne trova una seconda
- Ragionamento implicito: utile soprattutto come limite teorico, non come strategia principale di implementazione

In pratica, l'implementazione dovrebbe basarsi sui primi due.

## Rischi Principali

I principali rischi tecnici sono:

- Spendere troppo tempo sulla generazione delle griglie complete quando un dataset sarebbe sufficiente
- Mescolare la logica di generazione del puzzle con il modello MiniZinc invece di mantenere un chiaro livello di orchestrazione
- Rendere i controlli di unicità troppo costosi rieseguendo un modello base inefficiente
- Provare a ottimizzare la minimizzazione degli indizi troppo presto, prima che la pipeline di validazione sia stabile

## Esiti del Controllo di Unicità

Ogni controllo di unicità può produrre tre esiti che il livello di orchestrazione deve gestire esplicitamente:

- La seconda ricerca restituisce UNSAT entro il timeout: il puzzle è unico
- Viene trovata una seconda soluzione: il puzzle non è unico e l'ultima rimozione di indizio deve essere annullata
- Scatta il timeout prima di ottenere un verdetto: il risultato è sconosciuto

Il terzo caso non deve essere trattato in silenzio come "unico", altrimenti la pipeline può produrre puzzle non unici. Una scelta prudente è annullare l'ultima rimozione quando il risultato è sconosciuto e registrare l'evento nei log, così nel report si può quantificare quante volte è successo.

## Ordine di Sviluppo Consigliato

1. Ottenere un solver corretto.
2. Ottenere un controllo di unicità corretto.
3. Costruire la pipeline di rimozione degli indizi.
4. Solo dopo ottimizzare il numero di indizi e le prestazioni dei benchmark.

## Principio di Funzionamento

Il progetto dovrebbe trattare la generazione di Sudoku come un workflow ibrido:

- MiniZinc gestisce fattibilità e controlli di unicità
- Uno script esterno controlla la rimozione degli indizi
- Gli esperimenti misurano l'effetto delle scelte di modellazione e di ricerca

Questa separazione rende il progetto più facile da fare debug, spiegare e benchmarkare.
