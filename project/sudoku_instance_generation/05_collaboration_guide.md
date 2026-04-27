# Guida Collaborazione

Questa guida serve a chi clona il progetto e deve lavorarci senza ricostruire tutto da zero.

## 1. Clonare il repository

Dalla root dove vuoi tenere il progetto:

```bash
git clone <URL_DEL_REPO>
cd Constraint_Programming/project/sudoku_instance_generation
```

Se il repository e gia stato clonato:

```bash
git pull
cd project/sudoku_instance_generation
```

## 2. Cosa aspettarsi appena clonato

Nel repository sono gia presenti:

- modelli MiniZinc in `models/`
- script Python in `scripts/`
- benchmark gia eseguiti in `results/`
- report markdown in `report/report.md`
- campione di 50 griglie complete in `data/solved/sample_solutions.json`
- zip finale di consegna `sudoku_instance_generation_delivery.zip`

Non sono invece versionati:

- il raw Kaggle completo `data/raw/sudoku.csv`
- i puzzle generati localmente in `data/generated/`
- il PDF del report `report/report.pdf`

Questi file si possono rigenerare.

## 3. Dipendenze minime

Per lavorare bene servono:

- `python3`
- `minizinc`
- `fzn-gecode` nel `PATH`

Per il PDF del report servono anche:

- `pandoc`
- Python package `weasyprint`
- Python package `pypdf`

Per scaricare di nuovo Kaggle, se necessario:

- Python package `kagglehub`

## 4. Installazione rapida consigliata

### macOS con Homebrew

```bash
brew install minizinc pandoc
python3 -m pip install --user weasyprint pypdf kagglehub
```

Controlli rapidi:

```bash
which minizinc
which fzn-gecode
which pandoc
python3 -c "import weasyprint, pypdf"
```

## 5. Primo check del progetto

Dalla cartella `project/sudoku_instance_generation`:

### test Python

```bash
python3 scripts/sudoku_pipeline.py check \
  --input data/test/unique_puzzle.json \
  --backend python \
  --method counting
```

### test MiniZinc

```bash
python3 scripts/sudoku_pipeline.py check \
  --input data/test/unique_puzzle.json \
  --backend minizinc \
  --method counting
```

Se questi due passano, il progetto e operativo.

## 6. Comandi principali

### generare un puzzle

```bash
python3 scripts/sudoku_pipeline.py generate \
  --source data/solved/sample_solutions.json \
  --output data/generated/generated_puzzle.json \
  --backend python \
  --strategy random \
  --seed 7 \
  --method counting
```

### benchmark minimale

```bash
python3 scripts/benchmark.py \
  --input data/test/benchmark_instances.json \
  --output results/benchmark_python.json \
  --backend python
```

### benchmark MiniZinc con timeout

```bash
python3 scripts/benchmark.py \
  --input data/test/benchmark_instances.json \
  --output results/benchmark_minizinc_timeout300.json \
  --backend minizinc \
  --timeout 300
```

### benchmark completo

```bash
python3 scripts/run_full_benchmark.py \
  --source data/solved/sample_solutions.json \
  --output-csv results/full_benchmark.csv \
  --output-json results/full_benchmark.json \
  --backend python \
  --num-grids 20 \
  --strategies random symmetry density \
  --methods counting solve-and-block \
  --seed 42 \
  --timeout 300
```

### rigenerare i grafici del report

```bash
python3 scripts/plot_results.py \
  --input results/full_benchmark.csv \
  --output-dir report/assets
```

### rigenerare il PDF del report

```bash
python3 scripts/render_report_pdf.py
```

### creare lo zip finale

```bash
bash scripts/package_for_delivery.sh
```

## 7. Kaggle: cosa fare davvero

Il progetto usa gia `data/solved/sample_solutions.json`, quindi per lavorare sul codice non serve scaricare subito il dataset raw.

Il raw Kaggle serve solo se vuoi:

- rifare l'estrazione del campione
- cambiare il numero di griglie
- rigenerare `sample_solutions.json` da zero

Se hai il file `data/raw/sudoku.csv`, puoi rigenerare il campione cosi:

```bash
python3 scripts/import_kaggle_solutions.py \
  --input data/raw/sudoku.csv \
  --output data/solved/sample_solutions.json \
  --limit 50 \
  --seed 42
```

## 8. File importanti da conoscere

- `README.md`: panoramica breve del progetto
- `02_todo.md`: stato delle task
- `spec/project_19_notes.md`: testo trascritto della consegna
- `scripts/sudoku_pipeline.py`: logica centrale di solving, unicita e generazione
- `scripts/run_full_benchmark.py`: benchmark completo
- `scripts/render_report_pdf.py`: rendering markdown -> PDF
- `scripts/package_for_delivery.sh`: costruzione dello zip finale

## 9. Cosa non committare

Git ignora gia:

- `data/raw/sudoku.csv`
- `data/generated/*`
- `results/*`
- `report/report.pdf`
- `sudoku_instance_generation_delivery.zip`

Quindi in generale vanno committati:

- codice
- modelli
- documentazione
- report markdown

Non vanno committati gli artefatti rigenerabili, salvo decisione esplicita del team.

## 10. Flusso consigliato per chi collabora

1. Clona il repository e entra in `project/sudoku_instance_generation`.
2. Installa `minizinc` e verifica `fzn-gecode`.
3. Esegui i due check base (`python` e `minizinc`).
4. Leggi `README.md` e `02_todo.md`.
5. Lavora sui file necessari.
6. Se tocchi benchmark o report, rigenera grafici/PDF.
7. Prima di chiudere, prova `bash scripts/package_for_delivery.sh`.

## 11. Stato attuale del progetto

Attualmente il progetto e tecnicamente completo. L'unica voce rimasta aperta nel `TODO` e esterna al codice:

- chiarire col professore la frase anomala su `linear constraints for capacity and cost`

Se quel punto viene confermato come errore di copia-incolla, il progetto e sostanzialmente finito.
