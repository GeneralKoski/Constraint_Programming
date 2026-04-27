#!/usr/bin/env python3

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Confronto rapido tra strategie di generazione Sudoku")
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--backend", choices=["python", "minizinc"], default="python")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--timeout", type=int, default=None)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    pipeline = project_root / "scripts" / "sudoku_pipeline.py"
    results = []

    for strategy in ("random", "symmetry", "density"):
        output_path = project_root / "results" / f"generated_{strategy}.json"
        cmd = [
            sys.executable,
            str(pipeline),
            "--project-root",
            str(project_root),
            "generate",
            "--source",
            args.source,
            "--output",
            str(output_path),
            "--backend",
            args.backend,
            "--strategy",
            strategy,
            "--seed",
            str(args.seed),
        ]
        if args.timeout is not None:
            cmd.extend(["--timeout", str(args.timeout)])
        proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr or proc.stdout)
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        results.append(
            {
                "strategy": strategy,
                "clues": payload["clues"],
                "uniqueness_checks": payload["uniqueness_checks"],
                "accepted_removals": payload["accepted_removals"],
                "output_file": str(output_path.relative_to(project_root)),
            }
        )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"backend": args.backend, "seed": args.seed, "results": results}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out_path), "strategies": len(results)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
