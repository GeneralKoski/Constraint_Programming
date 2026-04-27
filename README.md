# Constraint Programming

Repository del corso di Constraint Programming, con materiale del corso e progetto finale.

## Progetto principale

Il progetto attivo e completo si trova in:

- [project/sudoku_instance_generation](project/sudoku_instance_generation)

Tema del progetto:

- **Sudoku Instance Generation**

Il progetto include:

- modelli MiniZinc
- pipeline Python per solving, controllo di unicita e generazione
- benchmark
- report finale
- packaging della consegna

## Da dove iniziare

Se devi collaborare sul progetto, leggi prima questi file:

1. [project/sudoku_instance_generation/README.md](project/sudoku_instance_generation/README.md)
2. [project/sudoku_instance_generation/05_collaboration_guide.md](project/sudoku_instance_generation/05_collaboration_guide.md)
3. [project/sudoku_instance_generation/02_todo.md](project/sudoku_instance_generation/02_todo.md)

## Setup rapido

Entra nella cartella del progetto:

```bash
cd project/sudoku_instance_generation
```

Dipendenze minime:

- `python3`
- `minizinc`
- `fzn-gecode` nel `PATH`

Per il PDF del report:

- `pandoc`
- `weasyprint`
- `pypdf`

## Check rapido

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

### creare lo zip finale

```bash
bash scripts/package_for_delivery.sh
```

## Note pratiche

- Il dataset Kaggle raw non e versionato nel repo.
- Il file `data/solved/sample_solutions.json` e gia presente e basta per lavorare.
- Il PDF del report e rigenerabile con `scripts/render_report_pdf.py`.

## Stato

Il progetto e tecnicamente completo. L'unico punto ancora aperto nel `TODO` e esterno al codice:

- chiarire col professore la frase su `linear constraints for capacity and cost`
