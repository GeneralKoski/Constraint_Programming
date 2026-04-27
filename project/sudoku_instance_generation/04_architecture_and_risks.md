# Sudoku Instance Generation - Architecture And Risks

## Suggested Architecture

A clean implementation can be split into the following parts:

- one MiniZinc solver model for solving and validating Sudoku instances
- one MiniZinc model or configuration for uniqueness tests
- one orchestration script that removes clues and repeatedly invokes MiniZinc
- one data folder containing complete solved grids and generated puzzles
- one results folder containing timings, statistics, and plots

This separation is important because clue removal is procedural, while Sudoku feasibility and uniqueness are delegated to the CP solver.

## Full Grid Sources

Once the solver is correct, valid complete Sudoku boards can be obtained in two ways:

- generated directly by the solver
- loaded from an external dataset of solved grids

Both approaches are reasonable. The second is usually better for experiments because it decouples puzzle generation from full-grid construction.

## Uniqueness Strategies

The main approaches worth comparing are:

- solve-and-block: find one solution, add a constraint that forbids it, search again
- solution counting: enumerate solutions and stop as soon as a second one is found
- implicit reasoning: mainly useful as a theoretical limitation, not as the main implementation strategy

In practice, the first two should drive the implementation.

## Main Risks

The main technical risks are:

- spending too much time on full-grid generation when a dataset would be enough
- mixing puzzle generation logic with the MiniZinc model instead of keeping a clear orchestration layer
- making uniqueness checks too expensive by rerunning an inefficient base model
- trying to optimize clue minimization too early, before the validation pipeline is stable

## Uniqueness Check Outcomes

Each uniqueness check can produce three outcomes that the orchestration layer must handle explicitly:

- the second search returns UNSAT within the timeout: the puzzle is unique
- a second solution is found: the puzzle is not unique and the last clue removal must be reverted
- the timeout fires before a verdict: the result is unknown

The third case must not be silently treated as "unique", otherwise the pipeline can produce non-unique puzzles. A safe default is to revert the last removal when the result is unknown, and to record the event in the logs so the report can quantify how often it happened.

## Recommended Development Order

1. Get a correct solver.
2. Get a correct uniqueness check.
3. Build the clue-removal pipeline.
4. Only then optimize clue count and benchmark performance.

## Working Principle

The project should treat Sudoku generation as a hybrid workflow:

- MiniZinc handles feasibility and uniqueness checks
- an external script controls clue removal
- experiments measure the effect of modeling and search choices

That separation makes the project easier to debug, explain, and benchmark.
