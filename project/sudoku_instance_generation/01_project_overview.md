# Sudoku Instance Generation

## Goal

The project focuses on modeling and generating Sudoku instances with Constraint Programming, using MiniZinc as the main language.

According to the project description currently available, the generated 9x9 instances must:

- have at least one valid solution
- have exactly one admissible solution (uniqueness)
- contain as few clues (pre-filled cells) as possible while preserving uniqueness

The core idea is not only to solve a Sudoku grid, but to study how to:

- generate a valid complete Sudoku solution
- remove clues to obtain a puzzle
- verify that the generated puzzle is still valid
- enforce or test uniqueness of the solution
- minimize the number of clues kept in the final instance
- compare different modeling and search choices

## Why This Project Is Interesting

This project is a good fit for the course because it combines:

- classic CSP modeling
- global constraints such as `alldifferent`
- search strategy choices
- propagation quality
- generation instead of simple solving
- an extra layer of difficulty given by uniqueness checking

It is therefore stronger than a basic Sudoku solver and gives enough material for both the implementation and the oral discussion.

## Main Technical Direction

The project can be developed in stages.

### 1. Sudoku Solver

First, build a clean MiniZinc model for solving Sudoku:

- 9x9 grid of decision variables
- domains `1..9`
- `alldifferent` on rows
- `alldifferent` on columns
- `alldifferent` on each 3x3 block

This part serves as the foundation for all later work.

### 2. Complete Grid Generation

Once the solver is correct, valid complete Sudoku boards can be obtained in two ways:

- generated directly by the solver
- loaded from an external dataset of solved grids

Both approaches are reasonable. The second is usually better for experiments because it decouples puzzle generation from full-grid construction.

### 3. Puzzle Generation

Starting from a valid complete grid, remove some values and keep the rest as clues.

The goal is to obtain a playable Sudoku instance, not only a solved board.

### 4. Uniqueness Check

The most important advanced step is verifying that the generated puzzle has a unique solution.

This is what makes the project significantly more interesting than standard Sudoku solving. It also gives a strong theoretical and practical point to discuss during the exam.

Based on the current project text, a relevant goal is to evaluate different strategies for testing the uniqueness of the solution. The main approaches to compare are:

- Solve-and-block: find one solution, add a constraint that forbids it, search again. If the second search returns UNSAT, the puzzle is unique.
- Solution counting: enumerate solutions with the solver flag for finding all solutions, stopping as soon as a second one is found.
- Implicit reasoning: rely on propagation to argue uniqueness without full enumeration. This is sound only in restricted cases and is mainly worth discussing as a limitation.

In practice, the project should rely on the first two approaches. The third one is mainly a theoretical discussion point.

### 5. Clue Minimization

Once uniqueness can be checked, the workflow should aim at producing puzzles with as few clues as possible while keeping the solution unique. This part connects directly to the current reading of the project requirement:

- iteratively remove clues from a complete grid
- after each removal, run the uniqueness check
- accept the removal only if the puzzle is still uniquely solvable
- compare different removal strategies (random order, symmetry-aware, density-aware)

The final report should clearly relate the number of remaining clues to the time required to verify uniqueness.

### 6. Experimental Comparison

After the base version works, compare:

- different search annotations
- different clue-removal strategies
- different levels of redundancy in the model
- runtime and solver behavior on multiple generated instances
- time vs number of remaining clues, as required by the project specification

If the project text is confirmed as read, the benchmark should be run with a 5 minutes timeout per test.

## Expected Deliverables

The final delivery is a single zip file containing models, scripts, dataset, generated instances, results and a written report of 6 to 10 pages.

See [03_spec_notes.md](03_spec_notes.md) for the full deliverables list and the open points still to be confirmed against the official project text.

## Oral Exam Value

This project is good for the oral exam because it allows discussion of:

- CSP modeling choices
- role of global constraints, in particular `alldifferent`
- Régin's theorem and the filtering algorithm behind `alldifferent`
- propagation and solver efficiency, including AC vs bounds consistency on Sudoku
- search heuristics
- difference between solving and generation
- how uniqueness changes the problem structure
- complexity remarks: NP-completeness of generalized Sudoku and the `#P`-complete nature of solution counting

In short, the project should be presented as a Constraint Programming project on Sudoku generation, not just on Sudoku solving.

## Related Notes

More detailed material is split into separate files:

- [02_todo.md](02_todo.md): implementation checklist and milestones
- [03_spec_notes.md](03_spec_notes.md): notes about the official project text, dataset, deliverables, experimental constraints and assumptions
- [04_architecture_and_risks.md](04_architecture_and_risks.md): architecture, workflow separation, uniqueness strategies and main technical risks
