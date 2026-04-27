# Generazione di Istanze Sudoku - Note sulla Specifica

## Verifiche sul Testo del Progetto

Due punti vanno trattati con attenzione prima di finalizzare l'implementazione:

1. Il testo del progetto sembra contenere un probabile errore di copia-incolla:

> "Implement a MiniZinc model using linear constraints for capacity and cost."

Questa frase sembra non avere relazione con Sudoku ed è molto più coerente con il progetto 18 (Transit Line Frequency). Non dovrebbe guidare le scelte di modellazione, a meno che il professore non confermi esplicitamente che fosse previsto qualche termine di ottimizzazione.

2. L'uso di un dataset esterno va chiarito.

Se la specifica del progetto indica esplicitamente un dataset di soluzioni complete di Sudoku, allora è ragionevole usarlo come sorgente di input per la generazione dei puzzle. Se invece il dataset è solo suggerito, allora nel report bisogna spiegare perché è stato usato e quale ruolo ha nella pipeline.

## Dataset di Riferimento

Il testo attuale del progetto sembra rimandare al Kaggle Sudoku Dataset pubblico:

- Https://www.kaggle.com/datasets/rohanrao/sudoku

Contiene soluzioni complete di Sudoku e può essere usato come sorgente di griglie complete valide da cui derivare i puzzle. Questo evita di spendere tempo del solver solo per generare nuove griglie complete e rende gli esperimenti più riproducibili.

## Deliverable

In base al testo attuale del progetto, la consegna finale sembra essere un unico file zip contenente:

- Uno o più modelli MiniZinc
- Lo script di orchestrazione usato per gestire la pipeline di generazione
- Il dataset e le istanze di benchmark generate
- I risultati sperimentali
- Un report scritto di 6-10 pagine

Il report dovrebbe descrivere i modelli, le scelte implementative, la strategia di unicità, la strategia di rimozione degli indizi e i risultati sperimentali.

## Vincoli Sperimentali

La specifica del progetto sembra richiedere:

- Controlli di unicità sui puzzle generati
- Minimizzazione del numero di indizi
- Un confronto tra diverse strategie
- Un limite di 5 minuti per ogni test di benchmark
- Un'analisi che colleghi il tempo di generazione al numero di indizi rimanenti

Prima della stesura finale, questi punti dovrebbero essere ricontrollati sul PDF ufficiale, così il report può distinguere chiaramente tra requisiti stretti e scelte implementative.
