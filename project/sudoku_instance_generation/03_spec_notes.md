# Sudoku Instance Generation - Spec Notes

## Project Text Checks

Two points should be treated carefully before the implementation is finalized:

1. The project text appears to contain a likely copy-paste error:

> "Implement a MiniZinc model using linear constraints for capacity and cost."

This sentence looks unrelated to Sudoku and seems more coherent with project 18 (Transit Line Frequency). It should not drive the modeling choices unless the professor explicitly confirms that some optimization term was intended.

2. The use of an external dataset should be clarified.

If the project specification explicitly points to a dataset of complete Sudoku solutions, then it is reasonable to use it as an input source for puzzle generation. If instead the dataset is only suggested, then the report should explain why it was used and what its role is in the pipeline.

## Reference Dataset

The current project text appears to point to the public Kaggle Sudoku Dataset:

- https://www.kaggle.com/datasets/rohanrao/sudoku

It contains complete Sudoku solutions and can be used as the source of valid full grids from which puzzles can be derived. This avoids spending solver time only on generating new full grids and makes experiments more reproducible.

## Deliverables

According to the current project text, the final delivery appears to be a single zip file containing:

- one or more MiniZinc models
- the orchestration script used to drive the generation pipeline
- the dataset and the generated benchmark instances
- the experimental results
- a written report of 6 to 10 pages

The report should describe the models, the implementation choices, the uniqueness strategy, the clue-removal strategy, and the experimental results.

## Experimental Constraints

The project specification appears to require:

- uniqueness checks on generated puzzles
- minimization of the number of clues
- a comparison of different strategies
- a time limit of 5 minutes per benchmark test
- an analysis relating generation time to the number of remaining clues

Before the final write-up, these points should be checked once more against the official PDF so the report can distinguish strict requirements from implementation choices.
