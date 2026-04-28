# Testo del Progetto 19

Trascrizione del progetto 19 da `Elly/00_introduction/projects.pdf`.

## 19. Sudoku Instance Generation With Uniqueness Guarantee

The goal of this project is to automatically generate Sudoku instances of the standard size 9 × 9 that:

- have at least one valid solution
- have exactly one admissible solution
- contain as few clues (pre-filled cells) as possible while preserving uniqueness

The final instances must be generated and then validated through a MiniZinc model.

For experiments and for comparing the quality of the generated instances, use a list of complete Sudoku solutions taken from public datasets: Kaggle Sudoku Dataset (https://www.kaggle.com/datasets/rohanrao/sudoku).

1. Implement a MiniZinc model using linear constraints for capacity and cost.
2. Measure time vs required clues.
3. Evaluate different strategies for testing the uniqueness of the solution.
4. Write a 6–10 page report describing the models, the implementation choices made, the results, and the obtained runtimes. Prepare programs, datasets, and report in a zip file.

## Punti già emersi

- Il progetto riguarda la generazione di istanze Sudoku
- Il tema centrale è l'unicità della soluzione
- Va minimizzato il numero di indizi
- È richiesto un confronto sperimentale tra strategie

## Conferma del docente

Il Prof. Dal Palù ha confermato via email l'assegnazione del progetto 19 a Martin Trajkovski (matricola 397464). Non è prevista una prenotazione formale: la scelta è considerata effettiva da quel momento. Il docente ha invitato esplicitamente a scrivere in caso di dubbi sulle specifiche.

## Punto da verificare

Il punto 1 sembra contenere un errore di copia-incolla:

> "Implement a MiniZinc model using linear constraints for capacity and cost."

Questa frase è presa pari pari dal progetto 18 (Transit Line Frequency) e non ha senso applicata al Sudoku, che non ha né capacity né cost. Va chiesto al professore se l'intento era diverso (per esempio, un termine di ottimizzazione collegato al numero di clue) oppure se la frase va semplicemente ignorata.
