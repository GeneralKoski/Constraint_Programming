# Progetto Sudoku Instance Generation

Per una guida rapida visibile dalla root del repository su GitHub, vedi anche [../../README.md](../../README.md).

Questa cartella contiene una base completa e operativa per il progetto di generazione di istanze Sudoku.

## Struttura

- `01_project_overview.md`: panoramica del progetto
- `02_todo.md`: checklist operativa
- `03_spec_notes.md`: note sulla specifica
- `04_architecture_and_risks.md`: architettura e rischi
- `05_collaboration_guide.md`: guida passo-passo per chi clona il progetto
- `models/`: modelli MiniZinc
- `scripts/`: script di orchestrazione e benchmark
- `data/raw/`: dati originali esterni
- `data/solved/`: griglie complete valide
- `data/generated/`: puzzle generati
- `data/test/`: istanze di test
- `results/`: output di benchmark e log
- `report/`: materiale per il report finale
- `spec/`: testo del progetto e note collegate

## Sorgente delle griglie complete

Per i benchmark principali il progetto usa un sottoinsieme di griglie complete estratte dal **Kaggle Sudoku Dataset** (`rohanrao/sudoku`). Il file raw viene tenuto localmente in `data/raw/sudoku.csv` e non viene committato perché è grande; il file versionato `data/solved/sample_solutions.json` contiene invece il sottoinsieme estratto e usato dalla pipeline.

La generazione interna tramite `models/sudoku_generate_full_grid.mzn` resta disponibile come fallback e come verifica autonoma del progetto.

## Backend disponibili

Il progetto è stato impostato con due backend:

- `minizinc`: backend principale previsto dal corso
- `python`: backend di fallback usato per testare la pipeline anche quando `minizinc` non è installato

Il backend Python non sostituisce il progetto MiniZinc, ma permette di validare solver, unicità e generazione nell'ambiente corrente.

## Esecuzione rapida

### 1. Verifica di unicità su un puzzle di test

```bash
python3 scripts/sudoku_pipeline.py check \
  --input data/test/unique_puzzle.json \
  --backend python
```

### 2. Generazione di un nuovo puzzle

```bash
python3 scripts/sudoku_pipeline.py generate \
  --source data/solved/sample_solutions.json \
  --output data/generated/generated_puzzle.json \
  --backend python \
  --strategy random \
  --seed 7
```

### 3. Benchmark minimale

```bash
python3 scripts/benchmark.py \
  --input data/test/benchmark_instances.json \
  --output results/benchmark_python.json \
  --backend python
```

### 4. Confronto tra strategie di generazione

```bash
python3 scripts/compare_strategies.py \
  --source data/solved/sample_solutions.json \
  --output results/strategy_comparison.json \
  --backend python \
  --seed 7
```

### 5. Estrazione del campione dal Kaggle dataset

```bash
python3 scripts/import_kaggle_solutions.py \
  --input data/raw/sudoku.csv \
  --output data/solved/sample_solutions.json \
  --limit 50 \
  --seed 42
```

## Esecuzione con MiniZinc

Se `minizinc` è installato nel sistema, si può usare:

```bash
python3 scripts/sudoku_pipeline.py check \
  --input data/test/unique_puzzle.json \
  --backend minizinc
```

Gli script si aspettano il binario `minizinc` nel `PATH`.

Nota: in questo progetto è inclusa anche la configurazione `spec/gecode_local.msc`, usata dagli script per forzare l'uso di Gecode quando l'installazione di MiniZinc non registra automaticamente il solver CP. La configurazione si aspetta che il binario `fzn-gecode` sia nel `PATH`. Su macOS con Homebrew si trova tipicamente in `/opt/homebrew/bin/fzn-gecode`, su Linux in `/usr/bin/fzn-gecode`.

## File dati

I puzzle e le soluzioni usano un formato JSON semplice:

- `grid`: matrice 9x9
- Negli input puzzle, `0` indica una cella vuota
- Nelle soluzioni complete, ogni cella contiene un valore `1..9`

## Stato del progetto

Questa base include:

- Modello MiniZinc parametrico per solving
- Modello MiniZinc per controllo di non unicità via solve-and-block
- Script Python per solving, conteggio soluzioni, generazione e benchmark
- Loader per estrarre un campione di griglie complete dal Kaggle Sudoku Dataset
- Istanze di test e griglie complete iniziali

Quello che resta da fare per la consegna finale è soprattutto il lavoro sperimentale esteso e la rifinitura del report.
