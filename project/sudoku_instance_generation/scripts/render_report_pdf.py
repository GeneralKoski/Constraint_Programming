#!/usr/bin/env python3

"""Renderizza report/report.md in report/report.pdf.

Dipendenze esterne:
- pandoc (per la conversione markdown -> HTML)
- weasyprint (per la conversione HTML -> PDF)

Su macOS le librerie native richieste da weasyprint (gobject, pango) si trovano
sotto /opt/homebrew/lib quando vengono installate via Homebrew. Lo script aggiunge
quel percorso a DYLD_FALLBACK_LIBRARY_PATH se necessario.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def ensure_lib_path() -> None:
    if sys.platform != "darwin":
        return
    brew_lib = "/opt/homebrew/lib"
    if not Path(brew_lib).is_dir():
        return
    current = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    if brew_lib in current.split(":"):
        return
    new_value = brew_lib if not current else f"{brew_lib}:{current}"
    os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = new_value


def main() -> int:
    parser = argparse.ArgumentParser(description="Renderizza il report markdown in PDF")
    parser.add_argument("--input", default="report/report.md")
    parser.add_argument("--output", default="report/report.pdf")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    input_path = project_root / args.input
    output_path = project_root / args.output
    base_dir = input_path.parent

    if shutil.which("pandoc") is None:
        print("Errore: pandoc non disponibile nel PATH", file=sys.stderr)
        return 1

    ensure_lib_path()
    try:
        from weasyprint import HTML
    except OSError as exc:
        print(f"Errore: weasyprint non riesce a caricare le librerie native: {exc}", file=sys.stderr)
        return 1
    except ImportError:
        print("Errore: weasyprint non installato. Esegui: pip install --user weasyprint", file=sys.stderr)
        return 1

    html_path = output_path.with_suffix(".html")
    subprocess.run(
        [
            "pandoc",
            str(input_path),
            "-o",
            str(html_path),
            "--standalone",
            "--metadata",
            "title=Sudoku Instance Generation",
            f"--resource-path={base_dir}",
        ],
        check=True,
    )
    HTML(filename=str(html_path), base_url=str(base_dir)).write_pdf(str(output_path))
    html_path.unlink()

    try:
        from pypdf import PdfReader

        pages = len(PdfReader(str(output_path)).pages)
        print(f"Generato {output_path} ({pages} pagine)")
    except ImportError:
        print(f"Generato {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
