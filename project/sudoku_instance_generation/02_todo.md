# Sudoku Instance Generation - To Do

## Preliminary Clarifications

- [ ] Email the professor to confirm the actual scope of point 1, since the official text contains a copy-paste error mentioning "linear constraints for capacity and cost"
- [ ] Confirm whether the Kaggle dataset is required as the source of complete grids or can be replaced by self-generated full grids

## Core Setup

- [ ] Decide the naming convention for MiniZinc models, data files, and report material
- [ ] Collect any course examples that can be reused as a starting point
- [ ] Copy the Sudoku project text from `Elly/00_introduction/projects.pdf` (project 19) into `spec/` so all assumptions remain traceable
- [ ] Download the Kaggle Sudoku Dataset and store it under `data/raw/`
- [ ] Write a small loader that reads complete solutions from the Kaggle dataset
- [ ] Add a project-level `README.md` that documents how to reproduce the full pipeline

## Folder Structure

- [ ] Create `models/` for MiniZinc files
- [ ] Create `spec/` for the official project text and related notes
- [ ] Create `data/raw/` for the original Kaggle dataset
- [ ] Create `data/solved/` for complete Sudoku grids extracted from the dataset
- [ ] Create `data/generated/` for generated puzzles
- [ ] Create `data/test/` for known Sudoku instances used to validate the solver
- [ ] Create `scripts/` for orchestration code
- [ ] Create `results/` for benchmarks, logs and figures
- [ ] Create `report/` for the final 6-10 pages document

## Solver

- [ ] Write a base MiniZinc Sudoku solver
- [ ] Model rows with `alldifferent`
- [ ] Model columns with `alldifferent`
- [ ] Model 3x3 blocks with `alldifferent`
- [ ] Test the solver on known Sudoku instances
- [ ] Add a clear output format for grids

## Full Grid Generation

- [ ] Adapt the model so it can generate complete valid Sudoku solution grids
- [ ] Produce a small set of sample full grids
- [ ] Check that generated full grids are structurally correct
- [ ] Decide whether generated full grids are only a fallback or part of the main pipeline

## Puzzle Generation

- [ ] Define how clues are removed from a full grid
- [ ] Implement a first simple clue-removal strategy
- [ ] Produce sample incomplete puzzles
- [ ] Verify that generated puzzles remain valid inputs for the solver

## Uniqueness

- [ ] Define how to test whether a generated puzzle has a unique solution
- [ ] Implement a first uniqueness-check workflow based on solve-and-block
- [ ] Implement an alternative uniqueness check based on solution counting (find first 2 solutions)
- [ ] Document the limits of any implicit-reasoning approach for uniqueness, only as a discussion point
- [ ] Separate clearly the solving step from the uniqueness-check step
- [ ] Test the uniqueness check on multiple generated puzzles
- [ ] Compare the uniqueness strategies in terms of runtime and reliability

## Pipeline Orchestration

- [ ] Write a Python script that drives the full generation pipeline
- [ ] The script should: load a complete grid, remove clues, call MiniZinc for uniqueness, accept or revert each removal
- [ ] Make the removal order pluggable so that different strategies can be tested
- [ ] Make the MiniZinc solver and timeout configurable from the script
- [ ] Log every accepted and rejected clue removal for debugging and later analysis
- [ ] Save generated puzzles in a stable textual format

## Clue Minimization

- [ ] Implement a random clue-removal strategy as baseline
- [ ] Implement a symmetry-aware clue-removal strategy
- [ ] Implement a density-aware clue-removal strategy
- [ ] Record the final number of remaining clues per generated instance
- [ ] Produce a plot of time vs remaining clues, as required by the specification
- [ ] Record how many uniqueness calls were needed per final instance

## Improvements

- [ ] Try different search strategies
- [ ] Test whether redundant constraints help performance
- [ ] Compare different generation strategies
- [ ] Evaluate how many clues can be removed while keeping uniqueness
- [ ] Compare a plain model against a stronger model with explicit search annotations

## Experiments

- [ ] Prepare a benchmark set of generated puzzles starting from the Kaggle dataset
- [ ] Run all experiments with a 5 minutes timeout per test, if that requirement is confirmed in the official text
- [ ] Record runtimes and solver behavior
- [ ] Compare at least two variants of the model or workflow
- [ ] Summarize the main empirical findings
- [ ] Separate clearly correctness experiments from performance experiments

## Report And Exam Preparation

- [ ] Write a project report structure
- [ ] Make sure the final report is between 6 and 10 pages, if that requirement is confirmed in the official text
- [ ] Document the modeling choices
- [ ] Document the uniqueness strategy and the comparison among the alternatives
- [ ] Document the clue-removal strategies and the time vs clues analysis
- [ ] Prepare a few representative examples to show at the oral exam
- [ ] Prepare a short explanation of why this is more than a plain Sudoku solver
- [ ] Review Régin's theorem and the filtering algorithm behind `alldifferent`
- [ ] Review NP-completeness of generalized Sudoku and the `#P`-complete nature of solution counting
- [ ] Review propagator strength: AC vs bounds consistency on Sudoku, as discussed in lectures 7, 10 and 11

## Final Packaging

- [ ] Collect models, scripts, dataset, generated instances, results and report into a single zip file
- [ ] Verify that the zip is self-contained and that the pipeline can be reproduced from it

## Milestones

- [ ] Milestone 1: working Sudoku solver
- [ ] Milestone 2: working uniqueness checker
- [ ] Milestone 3: working clue-removal pipeline
- [ ] Milestone 4: benchmarkable generator
- [ ] Milestone 5: complete report and oral preparation
