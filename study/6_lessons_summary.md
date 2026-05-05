# Lessons Summary - Constraint Programming

Detailed log of topics covered in each lesson, based on the `Elly` repository contents.

## Introduction & Fundamentals
- **Lesson 00 (Intro):** Course presentation, rules, and references.
- **Lessons 01-03:**
  - **Peg Solitaire:** Modeling movement and plan symmetry.
  - **Traffic Light Problem:** Implementation using reification and table constraints.
- **Lesson 04:**
  - **Intelligent Search:** Strategies to fail early for better performance.
  - **N-Queens:** Comparing different models and their impact on search space.
  - **Complexity:** NP-completeness of CSPs and experimenting with SAT encodings.

## Search and Consistency
- **Lesson 05:**
  - Introduction to Local Search and Integer Linear Programming (ILP).
  - Proof rules and basic propagation concepts.
- **Lesson 06:**
  - Formalizing consistency: **AC1** and **AC3** (Arc Consistency).
  - Example application on the 4-Queens problem.
- **Lesson 07:**
  - **Bounds Consistency** and **Path Consistency**.
  - Practical example: Consistency in Sudoku (extreme levels).
  - SAT solving vs. Constraint Solving (Propagate + Branch).
- **Lesson 08:**
  - **Branch and Bound** tree examples.
  - MiniZinc syntax introduction.
  - Search tree analysis: impact of variable and domain selection strategies.

## Modeling Techniques
- **Lesson 09:**
  - Classic problems: **Send More Money**, **Latin Square**.
  - Comparison of strategies, redundant constraints, and propagator costs.
- **Lesson 10:**
  - **Magic Square** and **Sudoku**.
  - **Symmetry Breaking:** Symmetries on variable renaming, cell permutations, and local symmetries. Impact on search time/space.
- **Lesson 11:**
  - Sudoku: Effect of propagator precision (e.g., `alldifferent`).
  - **Timetabling:** Modeling alternatives (variables for class/period vs. classroom/period). Handling preferences in COPs (Constraint Optimization Problems).
- **Lesson 12:**
  - Balancing multiple goals in Timetabling.
  - **Knapsack Problem:** Tuning search strategies.
  - **Hamming Codes:** Symmetry breaking using lexicographic order.

## Advanced Problems & Global Constraints
- **Lesson 13 (Haplotyping):** Modeling equivalence classes and representative selection. Importance of reification.
- **Lesson 14 (Protein Structure):** Space and energy modeling, constraints over space, and space symmetries.
- **Lesson 15 (Global Constraints):** TSP (Traveling Salesperson Problem) - comparing `circuit` vs. `alldifferent`.
- **Lesson 16 (Scheduling):** `cumulative` global constraint. **Social Golfers Problem** (discussion of alternative versions).
- **Lesson 17:** Social Golfer modeling comparison. **Best Host Problem** (maximization of preferences).

## Filtering & Final Topics
- **Lesson 18:** Project presentation and discussion.
- **Lesson 19:** Formalization of the **all-different global propagator**. Bipartite graph modeling, Berge theorem, and Regin's theorem for filtering implementation.
- **Lesson 20:**
  - **Stable Marriage Problem**.
  - **Tower of Hanoi:** Planning as CP, modeling fluents, inertia, and search strategies.
- **Lesson 21:** Hanoi Tower (actions symmetry), Nurse Scheduling problem (paper discussion).
- **Lesson 24:** Final projects discussion.

---
*Note: Lessons 22 and 23 focus on COLA 3.0 and practical implementations of Peg Solitaire/Traffic Lights.*
