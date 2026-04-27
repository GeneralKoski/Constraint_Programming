#!/usr/bin/env python3

import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import List, Optional, Tuple

Grid = List[List[int]]


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")


def validate_grid(grid: Grid, allow_zero: bool) -> None:
    if len(grid) != 9 or any(len(row) != 9 for row in grid):
        raise ValueError("La griglia deve essere 9x9")
    for row in grid:
        for value in row:
            if allow_zero:
                ok = 0 <= value <= 9
            else:
                ok = 1 <= value <= 9
            if not ok:
                raise ValueError("Valori non validi nella griglia")


def copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def find_empty(grid: Grid) -> Optional[Tuple[int, int]]:
    best: Optional[Tuple[int, int]] = None
    best_len = 10
    for r in range(9):
        for c in range(9):
            if grid[r][c] != 0:
                continue
            choices = candidate_values(grid, r, c)
            if not choices:
                return (r, c)
            if len(choices) < best_len:
                best = (r, c)
                best_len = len(choices)
                if best_len == 1:
                    return best
    return best


def candidate_values(grid: Grid, row: int, col: int) -> List[int]:
    if grid[row][col] != 0:
        return []
    used = set(grid[row])
    used.update(grid[r][col] for r in range(9))
    br = (row // 3) * 3
    bc = (col // 3) * 3
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            used.add(grid[r][c])
    return [value for value in range(1, 10) if value not in used]


def solve_python(grid: Grid, rng: Optional[random.Random] = None) -> Optional[Grid]:
    work = copy_grid(grid)

    def backtrack() -> bool:
        cell = find_empty(work)
        if cell is None:
            return True
        row, col = cell
        values = candidate_values(work, row, col)
        if rng is not None:
            rng.shuffle(values)
        for value in values:
            work[row][col] = value
            if backtrack():
                return True
            work[row][col] = 0
        return False

    return work if backtrack() else None


def count_solutions_python(grid: Grid, limit: int = 2) -> Tuple[int, Optional[Grid]]:
    work = copy_grid(grid)
    found = 0
    first_solution: Optional[Grid] = None

    def backtrack() -> None:
        nonlocal found, first_solution
        if found >= limit:
            return
        cell = find_empty(work)
        if cell is None:
            found += 1
            if first_solution is None:
                first_solution = copy_grid(work)
            return
        row, col = cell
        for value in candidate_values(work, row, col):
            work[row][col] = value
            backtrack()
            work[row][col] = 0
            if found >= limit:
                return

    backtrack()
    return found, first_solution


def solve_excluding_python(grid: Grid, forbidden: Grid) -> Optional[Grid]:
    work = copy_grid(grid)

    def backtrack() -> bool:
        cell = find_empty(work)
        if cell is None:
            if any(work[r][c] != forbidden[r][c] for r in range(9) for c in range(9)):
                return True
            return False
        row, col = cell
        for value in candidate_values(work, row, col):
            work[row][col] = value
            if backtrack():
                return True
            work[row][col] = 0
        return False

    return work if backtrack() else None


def puzzle_status_python(grid: Grid, method: str = "counting") -> dict:
    start = time.time()
    if method == "counting":
        count, solution = count_solutions_python(grid, limit=2)
        elapsed = time.time() - start
        if count == 0:
            status = "unsat"
        elif count == 1:
            status = "unique"
        else:
            status = "multiple"
        return {
            "status": status,
            "solutions_found": count,
            "elapsed_seconds": elapsed,
            "solution": solution,
            "method": "counting",
        }
    if method == "solve-and-block":
        first = solve_python(grid)
        if first is None:
            return {
                "status": "unsat",
                "solutions_found": 0,
                "elapsed_seconds": time.time() - start,
                "solution": None,
                "method": "solve-and-block",
            }
        second = solve_excluding_python(grid, first)
        elapsed = time.time() - start
        if second is None:
            return {
                "status": "unique",
                "solutions_found": 1,
                "elapsed_seconds": elapsed,
                "solution": first,
                "method": "solve-and-block",
            }
        return {
            "status": "multiple",
            "solutions_found": 2,
            "elapsed_seconds": elapsed,
            "solution": first,
            "method": "solve-and-block",
        }
    raise ValueError(f"Metodo di unicità non supportato: {method}")


def board_to_dzn(name: str, grid: Grid) -> str:
    flat = ", ".join(str(value) for row in grid for value in row)
    return f"{name} = array2d(1..9, 1..9, [{flat}]);\n"


def run_minizinc(
    model: Path,
    dzn_text: str,
    timeout_seconds: Optional[int],
    extra_flags: Optional[List[str]] = None,
) -> subprocess.CompletedProcess:
    if shutil.which("minizinc") is None:
        raise RuntimeError("Il comando 'minizinc' non è disponibile nel PATH")
    project_root = model.parents[1]
    solver_config = project_root / "spec" / "gecode_local.msc"
    tmp_dir = project_root / "results"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".dzn", dir=tmp_dir, delete=False, encoding="utf-8") as handle:
        handle.write(dzn_text)
        temp_dzn = handle.name
    try:
        cmd = ["minizinc", "--solver", str(solver_config)]
        if extra_flags:
            cmd.extend(extra_flags)
        cmd.extend([str(model), temp_dzn])
        if timeout_seconds is not None:
            cmd.extend(["--time-limit", str(timeout_seconds * 1000)])
        return subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            check=False,
        )
    finally:
        try:
            os.unlink(temp_dzn)
        except FileNotFoundError:
            pass


def parse_minizinc_grid(output: str) -> Optional[Grid]:
    rows = []
    for raw_line in output.strip().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("----------") or line.startswith("=========="):
            continue
        if "UNSATISFIABLE" in line or "UNKNOWN" in line or "ERROR" in line:
            continue
        values = [int(token) for token in line.split()]
        if len(values) == 9:
            rows.append(values)
    return rows if len(rows) == 9 else None


def parse_minizinc_grids(output: str) -> List[Grid]:
    grids: List[Grid] = []
    current: List[List[int]] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("----------"):
            if len(current) == 9:
                grids.append(current)
            current = []
            continue
        if line.startswith("==========") or "UNSATISFIABLE" in line or "UNKNOWN" in line or "ERROR" in line:
            continue
        try:
            values = [int(token) for token in line.split()]
        except ValueError:
            continue
        if len(values) == 9:
            current.append(values)
    if len(current) == 9:
        grids.append(current)
    return grids


def puzzle_status_minizinc_solve_and_block(
    project_root: Path, grid: Grid, timeout_seconds: Optional[int]
) -> dict:
    start = time.time()
    solver_model = project_root / "models" / "sudoku_solver.mzn"
    proc = run_minizinc(solver_model, board_to_dzn("clues", grid), timeout_seconds)
    elapsed = time.time() - start
    if proc.returncode != 0:
        return {
            "status": "unknown",
            "solutions_found": 0,
            "elapsed_seconds": elapsed,
            "stderr": proc.stderr.strip(),
            "solution": None,
            "method": "solve-and-block",
        }
    solution = parse_minizinc_grid(proc.stdout)
    if solution is None:
        return {
            "status": "unsat",
            "solutions_found": 0,
            "elapsed_seconds": elapsed,
            "stderr": proc.stderr.strip(),
            "solution": None,
            "method": "solve-and-block",
        }
    non_unique_model = project_root / "models" / "sudoku_non_unique_check.mzn"
    dzn = board_to_dzn("clues", grid) + board_to_dzn("known_solution", solution)
    second = run_minizinc(non_unique_model, dzn, timeout_seconds)
    if second.returncode == 0 and parse_minizinc_grid(second.stdout) is not None:
        status = "multiple"
        solutions_found = 2
    else:
        status = "unique"
        solutions_found = 1
    return {
        "status": status,
        "solutions_found": solutions_found,
        "elapsed_seconds": time.time() - start,
        "solution": solution,
        "stderr": (proc.stderr + "\n" + second.stderr).strip(),
        "method": "solve-and-block",
    }


def puzzle_status_minizinc_counting(
    project_root: Path, grid: Grid, timeout_seconds: Optional[int]
) -> dict:
    start = time.time()
    solver_model = project_root / "models" / "sudoku_solver.mzn"
    proc = run_minizinc(
        solver_model,
        board_to_dzn("clues", grid),
        timeout_seconds,
        extra_flags=["-a", "-n", "2"],
    )
    elapsed = time.time() - start
    if proc.returncode != 0:
        return {
            "status": "unknown",
            "solutions_found": 0,
            "elapsed_seconds": elapsed,
            "stderr": proc.stderr.strip(),
            "solution": None,
            "method": "counting",
        }
    solutions = parse_minizinc_grids(proc.stdout)
    search_complete = "==========" in proc.stdout
    if not solutions:
        return {
            "status": "unsat",
            "solutions_found": 0,
            "elapsed_seconds": elapsed,
            "stderr": proc.stderr.strip(),
            "solution": None,
            "method": "counting",
        }
    if len(solutions) >= 2:
        return {
            "status": "multiple",
            "solutions_found": 2,
            "elapsed_seconds": elapsed,
            "stderr": proc.stderr.strip(),
            "solution": solutions[0],
            "method": "counting",
        }
    if search_complete:
        return {
            "status": "unique",
            "solutions_found": 1,
            "elapsed_seconds": elapsed,
            "stderr": proc.stderr.strip(),
            "solution": solutions[0],
            "method": "counting",
        }
    return {
        "status": "unknown",
        "solutions_found": 1,
        "elapsed_seconds": elapsed,
        "stderr": proc.stderr.strip(),
        "solution": solutions[0],
        "method": "counting",
    }


def puzzle_status_minizinc(
    project_root: Path,
    grid: Grid,
    timeout_seconds: Optional[int],
    method: str = "solve-and-block",
) -> dict:
    if method == "solve-and-block":
        return puzzle_status_minizinc_solve_and_block(project_root, grid, timeout_seconds)
    if method == "counting":
        return puzzle_status_minizinc_counting(project_root, grid, timeout_seconds)
    raise ValueError(f"Metodo di unicità non supportato: {method}")


def choose_source_grid(path: Path, rng: random.Random) -> Grid:
    payload = read_json(path)
    boards = payload.get("grids") or payload.get("solutions")
    if not isinstance(boards, list) or not boards:
        raise ValueError("Il file sorgente deve contenere una lista non vuota di griglie")
    grid = rng.choice(boards)
    validate_grid(grid, allow_zero=False)
    return copy_grid(grid)


def iter_positions(strategy: str, rng: random.Random) -> List[Tuple[int, int]]:
    positions = [(r, c) for r in range(9) for c in range(9)]
    if strategy == "random":
        rng.shuffle(positions)
        return positions
    if strategy == "symmetry":
        seen = set()
        ordered = []
        for r, c in positions:
            mirror = (8 - r, 8 - c)
            key = tuple(sorted(((r, c), mirror)))
            if key in seen:
                continue
            seen.add(key)
            ordered.append((r, c))
        rng.shuffle(ordered)
        return ordered
    if strategy == "density":
        return sorted(positions, key=lambda item: abs(item[0] - 4) + abs(item[1] - 4), reverse=True)
    raise ValueError("Strategia non supportata")


def generate_puzzle(
    source_grid: Grid,
    backend: str,
    project_root: Path,
    strategy: str,
    timeout_seconds: Optional[int],
    seed: int,
    method: str = "counting",
) -> dict:
    rng = random.Random(seed)
    puzzle = copy_grid(source_grid)
    removal_log = []
    positions = iter_positions(strategy, rng)
    index = 0
    while index < len(positions):
        row, col = positions[index]
        if puzzle[row][col] == 0:
            index += 1
            continue
        previous = puzzle[row][col]
        mirror = None
        mirror_prev = None
        if strategy == "symmetry":
            candidate = (8 - row, 8 - col)
            if candidate != (row, col):
                mirror = candidate
                mirror_prev = puzzle[mirror[0]][mirror[1]]
        puzzle[row][col] = 0
        if mirror is not None:
            puzzle[mirror[0]][mirror[1]] = 0
        status = evaluate_puzzle(project_root, puzzle, backend, timeout_seconds, method=method)
        accepted = status["status"] == "unique"
        if not accepted:
            puzzle[row][col] = previous
            if mirror is not None:
                puzzle[mirror[0]][mirror[1]] = mirror_prev
        removal_log.append(
            {
                "row": row + 1,
                "col": col + 1,
                "accepted": accepted,
                "status": status["status"],
                "elapsed_seconds": status["elapsed_seconds"],
            }
        )
        index += 1
    clues = sum(1 for row in puzzle for value in row if value != 0)
    return {
        "seed": seed,
        "strategy": strategy,
        "backend": backend,
        "method": method,
        "puzzle": puzzle,
        "solution": source_grid,
        "clues": clues,
        "uniqueness_checks": len(removal_log),
        "accepted_removals": sum(1 for item in removal_log if item["accepted"]),
        "removal_log": removal_log,
    }


def evaluate_puzzle(project_root: Path, grid: Grid, backend: str, timeout_seconds: Optional[int], method: str = "counting") -> dict:
    validate_grid(grid, allow_zero=True)
    if backend == "python":
        return puzzle_status_python(grid, method=method)
    if backend == "minizinc":
        return puzzle_status_minizinc(project_root, grid, timeout_seconds, method=method)
    raise ValueError("Backend non supportato")


def cmd_check(args: argparse.Namespace) -> int:
    payload = read_json(Path(args.input))
    grid = payload["grid"]
    result = evaluate_puzzle(Path(args.project_root), grid, args.backend, args.timeout, method=args.method)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] in {"unique", "multiple", "unsat"} else 1


def cmd_generate(args: argparse.Namespace) -> int:
    source = choose_source_grid(Path(args.source), random.Random(args.seed))
    result = generate_puzzle(
        source_grid=source,
        backend=args.backend,
        project_root=Path(args.project_root),
        strategy=args.strategy,
        timeout_seconds=args.timeout,
        seed=args.seed,
        method=args.method,
    )
    write_json(Path(args.output), result)
    print(json.dumps({"output": args.output, "clues": result["clues"], "strategy": args.strategy, "method": args.method}, indent=2))
    return 0


def cmd_solve(args: argparse.Namespace) -> int:
    payload = read_json(Path(args.input))
    grid = payload["grid"]
    validate_grid(grid, allow_zero=True)
    if args.backend == "python":
        start = time.time()
        solution = solve_python(grid)
        elapsed = time.time() - start
        result = {"solution": solution, "elapsed_seconds": elapsed}
    else:
        status = puzzle_status_minizinc(Path(args.project_root), grid, args.timeout)
        result = {"solution": status.get("solution"), "elapsed_seconds": status["elapsed_seconds"], "status": status["status"]}
    print(json.dumps(result, indent=2))
    return 0 if result.get("solution") else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pipeline per il progetto Sudoku Instance Generation")
    parser.add_argument(
        "--project-root",
        default=str(Path(__file__).resolve().parents[1]),
        help="Radice del progetto Sudoku",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    solve_cmd = sub.add_parser("solve")
    solve_cmd.add_argument("--input", required=True)
    solve_cmd.add_argument("--backend", choices=["python", "minizinc"], default="python")
    solve_cmd.add_argument("--timeout", type=int, default=None)
    solve_cmd.set_defaults(func=cmd_solve)

    check_cmd = sub.add_parser("check")
    check_cmd.add_argument("--input", required=True)
    check_cmd.add_argument("--backend", choices=["python", "minizinc"], default="python")
    check_cmd.add_argument("--method", choices=["counting", "solve-and-block"], default="counting")
    check_cmd.add_argument("--timeout", type=int, default=None)
    check_cmd.set_defaults(func=cmd_check)

    gen_cmd = sub.add_parser("generate")
    gen_cmd.add_argument("--source", required=True)
    gen_cmd.add_argument("--output", required=True)
    gen_cmd.add_argument("--backend", choices=["python", "minizinc"], default="python")
    gen_cmd.add_argument("--strategy", choices=["random", "symmetry", "density"], default="random")
    gen_cmd.add_argument("--method", choices=["counting", "solve-and-block"], default="counting")
    gen_cmd.add_argument("--timeout", type=int, default=None)
    gen_cmd.add_argument("--seed", type=int, default=0)
    gen_cmd.set_defaults(func=cmd_generate)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
