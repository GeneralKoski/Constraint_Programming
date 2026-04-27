#!/usr/bin/env python3

import argparse
import json
import subprocess
import sys
from pathlib import Path


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark minimale per puzzle Sudoku")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--backend", choices=["python", "minizinc"], default="python")
    parser.add_argument("--timeout", type=int, default=None)
    args = parser.parse_args()

    input_path = Path(args.input)
    project_root = Path(__file__).resolve().parents[1]
    pipeline = project_root / "scripts" / "sudoku_pipeline.py"
    payload = read_json(input_path)
    instances = payload.get("instances", [])
    results = []

    for item in instances:
        temp_path = project_root / "results" / "_benchmark_tmp.json"
        write_json(temp_path, {"grid": item["grid"]})
        cmd = [
            sys.executable,
            str(pipeline),
            "--project-root",
            str(project_root),
            "check",
            "--input",
            str(temp_path),
            "--backend",
            args.backend,
        ]
        if args.timeout is not None:
            cmd.extend(["--timeout", str(args.timeout)])
        proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
        result = json.loads(proc.stdout)
        result["name"] = item["name"]
        results.append(result)

    temp_path = project_root / "results" / "_benchmark_tmp.json"
    if temp_path.exists():
        temp_path.unlink()

    write_json(Path(args.output), {"backend": args.backend, "results": results})
    print(json.dumps({"output": args.output, "instances": len(results)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
