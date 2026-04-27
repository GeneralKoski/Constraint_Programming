#!/usr/bin/env bash
set -euo pipefail

# Costruisce il file zip finale per la consegna del progetto.
# Esegui dalla root del progetto:
#   bash scripts/package_for_delivery.sh

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

PROJECT_NAME="sudoku_instance_generation"
ZIP_NAME="${PROJECT_NAME}_delivery.zip"
STAGE_DIR=".package_stage"

rm -rf "$STAGE_DIR" "$ZIP_NAME"
mkdir -p "$STAGE_DIR/$PROJECT_NAME"

# Renderizza il PDF del report se possibile, in modo che lo zip lo contenga.
if python3 scripts/render_report_pdf.py >/dev/null 2>&1; then
  echo "Report PDF rigenerato in report/report.pdf"
else
  echo "Avviso: rendering PDF non disponibile, lo zip conterrà solo report.md"
fi

INCLUDE=(
  "01_project_overview.md"
  "02_todo.md"
  "03_spec_notes.md"
  "04_architecture_and_risks.md"
  "README.md"
  "models"
  "scripts"
  "spec"
  "report"
  "data/solved/sample_solutions.json"
  "data/test"
  "results/full_benchmark.csv"
  "results/full_benchmark.json"
)

for item in "${INCLUDE[@]}"; do
  if [ -e "$item" ]; then
    mkdir -p "$STAGE_DIR/$PROJECT_NAME/$(dirname "$item")"
    cp -R "$item" "$STAGE_DIR/$PROJECT_NAME/$item"
  else
    echo "Avviso: '$item' non esiste, saltato."
  fi
done

# Garantisci che le cartelle vuote previste dalla README esistano nello zip
mkdir -p "$STAGE_DIR/$PROJECT_NAME/data/raw"
mkdir -p "$STAGE_DIR/$PROJECT_NAME/data/generated"
touch "$STAGE_DIR/$PROJECT_NAME/data/raw/.gitkeep"
touch "$STAGE_DIR/$PROJECT_NAME/data/generated/.gitkeep"

# Pulizia file rigenerabili
find "$STAGE_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$STAGE_DIR" -name "*.pyc" -type f -delete 2>/dev/null || true
find "$STAGE_DIR" -name ".DS_Store" -type f -delete 2>/dev/null || true

# Crea zip
(cd "$STAGE_DIR" && zip -rq "../$ZIP_NAME" "$PROJECT_NAME")

# Cleanup
rm -rf "$STAGE_DIR"

echo
echo "Zip creato: $PROJECT_ROOT/$ZIP_NAME"
ls -lh "$ZIP_NAME" | awk '{print "  size:", $5}'
echo "  files:"
unzip -l "$ZIP_NAME" | tail -n 1
