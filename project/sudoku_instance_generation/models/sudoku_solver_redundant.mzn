include "globals.mzn";

int: n = 9;
set of int: IDX = 1..n;
array[IDX, IDX] of 0..9: clues;
array[IDX, IDX] of var 1..9: grid;

constraint
  forall(i in IDX, j in IDX where clues[i, j] > 0) (
    grid[i, j] = clues[i, j]
  );

constraint forall(i in IDX) (
  alldifferent([grid[i, j] | j in IDX])
);

constraint forall(j in IDX) (
  alldifferent([grid[i, j] | i in IDX])
);

constraint forall(br, bc in 0..2) (
  alldifferent([
    grid[3 * br + dr, 3 * bc + dc]
    | dr in 1..3, dc in 1..3
  ])
);

constraint forall(i in IDX) (
  sum([grid[i, j] | j in IDX]) = 45
);

constraint forall(j in IDX) (
  sum([grid[i, j] | i in IDX]) = 45
);

constraint forall(br, bc in 0..2) (
  sum([grid[3 * br + dr, 3 * bc + dc] | dr in 1..3, dc in 1..3]) = 45
);

solve
  :: int_search([grid[i, j] | i in IDX, j in IDX], first_fail, indomain_min, complete)
  satisfy;

output [
  if j = 1 then "\n" else " " endif ++ show(grid[i, j])
  | i in IDX, j in IDX
];
