# Guida di Studio — Esame Orale Constraint Programming

Indice unico per la preparazione orale del progetto **Sudoku Instance Generation** (progetto 19).

## Stato della consegna

- Codice: completo, tutto in `project/sudoku_instance_generation/02_todo.md` checklist chiusa
- Report: 9 pagine, dentro range 6-10
- Zip di consegna: `project/sudoku_instance_generation/sudoku_instance_generation_delivery.zip`
- Chiarimento col prof su "linear constraints for capacity and cost": confermato come copia-incolla da ignorare

**Resta solo l'orale.**

## Materiali di studio

I due documenti centrali sono nel progetto:

1. **[2_2_code_walkthrough.md](2_2_code_walkthrough.md)** — spiegazione completa di ogni file di codice (modelli MiniZinc, scripts Python, packaging). Per ogni componente: cosa fa, walkthrough commentato, punti da saper difendere.

2. **[3_3_oral_theory_notes.md](3_3_oral_theory_notes.md)** — note di teoria del corso applicate al progetto. 13 sezioni: Régin, NP-completezza, #P-completezza, AC vs BC, strategie di unicità, search strategies, vincoli globali, reificazione, vincoli ridondanti, symmetry breaking, branch and bound, CSP formale, FAQ.

3. **[4_report.md](4_report.md)** — il report finale di consegna. Versione "narrativa" del progetto, da rileggere almeno una volta.

## Piano di studio suggerito

### Giorno 1 — Codice
- Leggere `2_code_walkthrough.md` da cima a fondo, aprendo i file effettivi quando serve un riscontro
- Provare i comandi di test del README per vedere il pipeline in azione
- Tenere a mente: per ogni modello MiniZinc devi saper spiegare *perché* ogni vincolo è lì e *perché* quella search annotation

### Giorno 2 — Teoria
- Leggere `3_oral_theory_notes.md` sezioni 1-5 (Régin, NP/#P, AC vs BC, unicità) — sono le più probabili
- Approfondire 6-7 (search strategies, global constraints) — tipici da CP corso
- Skim 8-12 (reificazione, ridondanti, symmetry, B&B, CSP formale) — meno probabili, ma utili come "carte" da giocare

### Giorno 3 — Demo + ripasso
- Preparare la demo live (esempio in fondo a `2_code_walkthrough.md`)
- Rileggere il report
- Rispondere a voce alle FAQ in `3_oral_theory_notes.md` §13

## Topic checklist (da spuntare mentre studi)

### Modeling MiniZinc
- [ ] Variabili e domini (`array of var`)
- [ ] Vincolo globale `alldifferent` (perché è meglio dei `!=`)
- [ ] Reificazione (cos'è, quando serve, esempio)
- [ ] Vincoli ridondanti (cosa sono, quando aiutano)

### Consistency & Propagation
- [ ] AC, BC: definizioni precise
- [ ] AC-3: algoritmo a coda di archi, complessità
- [ ] Filtering di `alldifferent`: matching nei grafi bipartiti, Régin 1994
- [ ] Berge: matching massimo ⟺ no augmenting path
- [ ] SCC e nodi raggiungibili da nodi liberi → archi rimovibili

### Search
- [ ] Albero di ricerca, branching, propagation, backtracking
- [ ] Variable selection: `first_fail`, `dom_w_deg`, `most_constrained`, principio fail-first
- [ ] Value selection: `indomain_min`, `indomain_random`, `indomain_split`
- [ ] Modalità: `complete`, `bounded` (LDS), `restart`
- [ ] Branch and bound per ottimizzazione

### Symmetry
- [ ] Tipi di simmetria: variable, value, constraint
- [ ] Lex-leader, SBDS, SBDD
- [ ] Sudoku: simmetrie del problema generale vs simmetrie già rotte dalle clue
- [ ] Distinzione "symmetry-aware removal" (estetica) vs "symmetry breaking" (CP)

### Complessità
- [ ] CSP decisionale: NP-completo
- [ ] Sudoku generalizzato `n²×n²`: NP-completo (Yato & Seta 2003)
- [ ] Solution counting: #P-completo
- [ ] `#≥2` (sufficiente per unicità): NP

### Specifico al progetto
- [ ] Differenza solving vs generation
- [ ] Solve-and-block: workflow, pro/contro
- [ ] Solution counting: workflow, pro/contro, equivalenza con `#≥2`
- [ ] Gestione UNKNOWN da timeout
- [ ] Strategie di rimozione (random, symmetry, density) e risultati empirici
- [ ] Limite teorico 17 (McGuire 2012) e perché il greedy si ferma a 22

### Demo da preparare
- [ ] Esempio di check su `unique_puzzle.json` con backend Python + counting
- [ ] Stesso esempio con `solve-and-block`
- [ ] `non_unique_puzzle.json` per mostrare il caso `multiple`
- [ ] Spiegare la differenza tempo/comportamento tra i due metodi

## Riferimenti rapidi

- **Régin**: J.-C. Régin, *A filtering algorithm for constraints of difference in CSPs*, AAAI 1994
- **Berge**: C. Berge, *Graphs and Hypergraphs*, 1970 (teorema sugli augmenting paths)
- **AC-3**: A. Mackworth, *Consistency in Networks of Relations*, AI Journal 1977
- **NP-completezza Sudoku**: T. Yato & T. Seta, *Complexity and Completeness of Finding Another Solution and Its Application to Puzzles*, IEICE 2003
- **17-clue minimum**: G. McGuire, B. Tugemann, G. Civario, *There is no 16-clue Sudoku*, arXiv:1201.0749, 2012
- **Fail-first**: R. Haralick & G. Elliott, *Increasing Tree Search Efficiency for Constraint Satisfaction Problems*, AI 1980
- **dom_w_deg**: F. Boussemart et al., *Boosting Systematic Search by Weighting Constraints*, ECAI 2004

---
*In bocca al lupo per l'orale.*
