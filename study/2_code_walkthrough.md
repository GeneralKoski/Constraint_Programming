# Walkthrough del Codice per l'Orale

Spiegazione completa di ogni file del progetto: cosa fa, perché è fatto così, e come difenderlo all'orale. L'ordine segue il flusso logico (modelli → backend di solving → strategie → orchestrazione → benchmark → plot).

Per ogni componente trovi:

- **Cosa**: funzione del file in una frase.
- **Walkthrough**: spiegazione riga per riga delle parti che contano.
- **Punti da saper difendere**: domande probabili e risposte.

---

## Indice

1. [Modelli MiniZinc](#1-modelli-minizinc)
   - 1.1 `sudoku_solver.mzn`
   - 1.2 `sudoku_solver_redundant.mzn`
   - 1.3 `sudoku_solver_dom_w_deg.mzn`
   - 1.4 `sudoku_generate_full_grid.mzn`
   - 1.5 `sudoku_non_unique_check.mzn`
2. [Backend Python — `sudoku_pipeline.py`](#2-backend-python--sudoku_pipelinepy)
   - 2.1 Solver e candidate values
   - 2.2 Counting con limite
   - 2.3 Solve-excluding (solve-and-block in Python)
   - 2.4 Backend MiniZinc (subprocess + parsing)
   - 2.5 Strategie di rimozione (`iter_positions`)
   - 2.6 Loop di generazione (`generate_puzzle`)
   - 2.7 CLI
3. [Script di orchestrazione](#3-script-di-orchestrazione)
   - 3.1 `run_full_benchmark.py`
   - 3.2 `compare_strategies.py`
   - 3.3 `benchmark.py`
4. [Import dataset](#4-import-dataset)
   - 4.1 `import_kaggle_solutions.py` (reservoir sampling)
5. [Plot dei risultati — `plot_results.py`](#5-plot-dei-risultati--plot_resultspy)
6. [Packaging — `package_for_delivery.sh`](#6-packaging--package_for_deliverysh)
7. [Configurazione del solver — `spec/gecode_local.msc`](#7-configurazione-del-solver--specgecode_localmsc)

---

## 1. Modelli MiniZinc

I modelli condividono la struttura di base del Sudoku. Le differenze sono in: search annotation, vincoli ridondanti, parametri aggiuntivi.

### 1.1 `sudoku_solver.mzn` (modello base)

**Cosa**: il modello CP che decide se una griglia parziale ha una soluzione.

```minizinc
include "globals.mzn";

int: n = 9;
set of int: IDX = 1..n;
array[IDX, IDX] of 0..9: clues;          % parametro: 0 = vuota, 1..9 = fissata
array[IDX, IDX] of var 1..9: grid;        % variabili decisionali

constraint
  forall(i in IDX, j in IDX where clues[i, j] > 0) (
    grid[i, j] = clues[i, j]
  );

constraint forall(i in IDX) (alldifferent([grid[i, j] | j in IDX]));   % righe
constraint forall(j in IDX) (alldifferent([grid[i, j] | i in IDX]));   % colonne
constraint forall(br, bc in 0..2) (                                     % blocchi 3x3
  alldifferent([grid[3*br+dr, 3*bc+dc] | dr in 1..3, dc in 1..3])
);

solve
  :: int_search([grid[i,j] | i in IDX, j in IDX], first_fail, indomain_min, complete)
  satisfy;
```

**Walkthrough**:

- `int: n = 9` — costante simbolica. Non serve per il 9×9 ma rende riusabile la definizione su 4×4 / 16×16 cambiando una sola riga.
- `array[IDX, IDX] of 0..9: clues` — parametro a 81 celle dove `0` è "vuota". Importante: il dominio del parametro include `0`, ma il dominio delle variabili `grid` parte da `1`. Lo `0` non è mai un valore valido di Sudoku, è solo un sentinel per "cella libera".
- `array[IDX, IDX] of var 1..9: grid` — 81 variabili intere con dominio iniziale `{1..9}`.
- Il primo `constraint forall ... where clues[i,j] > 0` è il **canale di input**: lega le clue al modello senza modificare il modello stesso. Il `where` è un filtro statico: MiniZinc espande il forall solo per le posizioni con clue > 0.
- I tre `alldifferent` sono il cuore del Sudoku: 9 righe, 9 colonne, 9 blocchi 3×3. La costruzione del blocco usa `3*br+dr` con `br ∈ 0..2` e `dr ∈ 1..3`, quindi indici 1..3, 4..6, 7..9 — i 3 blocchi orizzontali. Stesso schema su `bc, dc` per quelli verticali.
- `solve :: int_search(...) satisfy`:
  - `int_search(vars, varsel, valsel, exploration)` è l'annotazione di ricerca.
  - **`first_fail`**: scegli la variabile col dominio più piccolo. È l'euristica "fail-first": se devi sbagliare, sbaglia presto (riduci la profondità del sotto-albero).
  - **`indomain_min`**: prova prima il valore minimo del dominio. Default conservativo.
  - **`complete`**: esplorazione completa (DFS con backtracking, l'unica modalità per dimostrare unicità).
  - **`satisfy`**: cerca *una* soluzione valida (non ottimizzazione). Usata anche per il counting con `-a` esterno.

**Punti da saper difendere**:

- **"Perché `alldifferent` invece di `forall(i,j) grid[i,a] != grid[i,b]`?"**
  → AC vs BC. `alldifferent` è propagato col filtering di Régin (matching nei grafi bipartiti) → arc consistency. La formulazione disgiuntiva ottiene solo bounds consistency e fallisce a propagare in molti casi. Vedi `3_oral_theory_notes.md` §1.
- **"Perché `0..9` come dominio delle clue invece di `int`?"**
  → Documentazione e safety: il dominio del parametro vincola gli input, MiniZinc rifiuta a load-time se passi `>9` o `<0`.
- **"Perché `first_fail` su Sudoku?"**
  → Sudoku ha celle iniziali con domini molto diversi (clue → singleton, vuote → `{1..9}`). `first_fail` branca prima sulle celle più vincolate, dove la propagazione ha già ristretto il dominio: massimizza la probabilità di pruning.

---

### 1.2 `sudoku_solver_redundant.mzn` (modello con vincoli ridondanti)

**Cosa**: stesso modello con in più `sum = 45` su righe, colonne, blocchi.

```minizinc
constraint forall(i in IDX) (sum([grid[i, j] | j in IDX]) = 45);
constraint forall(j in IDX) (sum([grid[i, j] | i in IDX]) = 45);
constraint forall(br, bc in 0..2) (
  sum([grid[3*br+dr, 3*bc+dc] | dr in 1..3, dc in 1..3]) = 45
);
```

**Walkthrough**:

- `1+2+...+9 = 45`. Se tutte le 9 celle sono distinte e in `{1..9}`, la somma è necessariamente 45. Quindi il vincolo è **implicato** dall'`alldifferent`.
- "Implicato" significa: nessuna soluzione viene aggiunta o tolta. Quello che cambia è la **propagazione**.
- La somma è un vincolo lineare. Dà bound consistency immediata: se 8 celle sono fissate e una è libera, propaga il valore esatto via differenza. `alldifferent` farebbe lo stesso, ma in modo meno diretto sul lato bound.

**Punti da saper difendere**:

- **"Servono o no?"**
  → Su 9×9, marginale: `alldifferent` è già forte. Sulle istanze con poche clue, il guadagno medio è ~5% sui tempi di MiniZinc, dentro la varianza statistica. Il valore principale è didattico: dimostrano il principio "redundant constraints help propagation when their semantics are different".
- **"Quando funzionano davvero?"**
  → Quando il propagator ridondante usa una struttura algebrica diversa da quella già propagata. Sum + alldifferent = bound + arc consistency combinati. Su problemi con solo bound (cumulative, scheduling), l'aggiunta di alldifferent può fare la differenza.

---

### 1.3 `sudoku_solver_dom_w_deg.mzn` (variant di search)

**Cosa**: stesso modello, ma con `dom_w_deg` come variable selection invece di `first_fail`.

```minizinc
solve
  :: int_search([grid[i,j] | i in IDX, j in IDX], dom_w_deg, indomain_min, complete)
  satisfy;
```

**Walkthrough**:

- **`dom_w_deg`** = "domain over weighted degree". Per ogni variabile mantiene un peso accumulato: ogni volta che un constraint causa un fallimento (wipe-out di un dominio), il peso delle variabili coinvolte cresce. La variabile scelta è quella con minor `|D(x)| / weight(x)`.
- Intuizione: si combinano due idee. Domain piccolo (à la `first_fail`) e "questa variabile mi ha già dato problemi prima". Va bene su istanze adversarial dove il fail-first puro non basta.

**Punti da saper difendere**:

- **"Quando conviene `dom_w_deg`?"**
  → Su istanze fortemente vincolate o con forte simmetria, dove `first_fail` da solo pesca male all'inizio. Su Sudoku 9×9 il guadagno è marginale, su 16×16 e 25×25 diventa visibile.
- **"Perché tenerlo in repo se non vince?"**
  → È esplicitamente richiesto dalla specifica (punto 6: "confrontare un modello semplice con un modello più forte che usa annotazioni di search esplicite"). Il valore è il *confronto*, non la vittoria.

---

### 1.4 `sudoku_generate_full_grid.mzn` (generazione griglie complete)

**Cosa**: modello per generare griglie 9×9 complete e diverse a ogni run.

```minizinc
array[IDX, IDX] of 0..9: fixed_cells;       % rinominato da clues
array[IDX, IDX] of var 1..9: grid;
% ... stessi alldifferent ...
solve
  :: int_search([grid[i,j] | i in IDX, j in IDX], first_fail, indomain_random, complete)
  satisfy;
```

**Walkthrough**:

- Differenza singola dal modello base: **`indomain_random`** invece di `indomain_min`.
- Con `indomain_min` ripeti la stessa griglia (la prima soluzione lessicograficamente minima) ogni volta. Con `indomain_random`, le scelte di branching sono casuali → griglie diverse a ogni esecuzione.
- `fixed_cells` invece di `clues` è una scelta semantica: se passi tutto a 0, generi una griglia random "da zero". Se passi qualche cella fissata, generi una griglia che le rispetta.

**Punti da saper difendere**:

- **"Perché esiste se usi Kaggle?"**
  → Tre motivi: (1) fallback se il Kaggle dataset non è disponibile; (2) verifica strutturale autonoma — se questo modello produce griglie valide, il modello CP è corretto; (3) dimostrazione che il progetto non dipende da dati esterni proprietari.
- **"`indomain_random` è deterministico?"**
  → Dipende dal seed del solver. Gecode usa un seed di default; passandolo da CLI (`--rnd-seed N`) si ha riproducibilità.

---

### 1.5 `sudoku_non_unique_check.mzn` (controllo unicità via blocking)

**Cosa**: dato un puzzle e una sua soluzione `S₁`, cerca una soluzione `S₂ ≠ S₁`. Se UNSAT, il puzzle è unico.

```minizinc
array[IDX, IDX] of 0..9: clues;
array[IDX, IDX] of 1..9: known_solution;   % parametro: la prima soluzione trovata
array[IDX, IDX] of var 1..9: grid;

% ... clues + alldifferent come prima ...

constraint
  exists(i in IDX, j in IDX) (
    grid[i, j] != known_solution[i, j]
  );
```

**Walkthrough**:

- **`known_solution`** è un parametro `array of 1..9` (non `0..9`): è una soluzione completa, niente celle vuote.
- **`exists(...) (grid[i,j] != known_solution[i,j])`** è il **blocking constraint**. In logica: ∃(i,j) tale che grid[i,j] ≠ known_solution[i,j], cioè la nuova griglia deve differire dalla soluzione data in almeno una cella.
- Se questo modello restituisce UNSAT su quel puzzle e quella soluzione, allora l'unica soluzione possibile è `known_solution` stessa → unicità.
- `exists` in MiniZinc viene compilato come una grossa disgiunzione `or(grid[1,1]≠ks[1,1], grid[1,2]≠ks[1,2], ...)`. È l'opposto duale di `forall ... and`.

**Punti da saper difendere**:

- **"Perché non `grid != known_solution` direttamente?"**
  → MiniZinc supporta `array != array` come elementwise, ma esprimerlo via `exists` è più chiaro pedagogicamente e più robusto nel parsing.
- **"Cosa succede se la prima soluzione è sbagliata?"**
  → Non può esserlo: viene dal solver corretto, è già stata validata. Se per qualche ragione fosse non valida, il blocking constraint farebbe rifiutare anche la "vera" soluzione e tornerebbe UNSAT prematuramente — ma la validazione del solver garantisce che non succeda.
- **"Costo della seconda ricerca?"**
  → Nello scenario "puzzle unico" deve esaurire l'albero per dimostrare UNSAT. Su Sudoku 9×9 con propagazione `alldifferent` di Régin, costa ~ms. Su scala più grande sarebbe il collo di bottiglia.

---

## 2. Backend Python — `sudoku_pipeline.py`

Il file ha 578 righe. Contiene il modulo Python "fa-tutto": solver, counting, solve-and-block, parser MiniZinc, strategie di rimozione, loop di generazione, CLI.

### 2.1 Solver e candidate values

```python
def candidate_values(grid: Grid, row: int, col: int) -> List[int]:
    if grid[row][col] != 0:
        return []
    used = set(grid[row])                                   # riga
    used.update(grid[r][col] for r in range(9))             # colonna
    br = (row // 3) * 3
    bc = (col // 3) * 3
    for r in range(br, br + 3):                             # blocco
        for c in range(bc, bc + 3):
            used.add(grid[r][c])
    return [value for value in range(1, 10) if value not in used]
```

**Walkthrough**:

- `candidate_values(grid, r, c)` → lista dei valori legali per la cella `(r,c)` data la griglia attuale.
- Calcola l'unione dei valori già presenti nella stessa riga, colonna, blocco; restituisce il complemento in `{1..9}`.
- È la versione procedurale del propagator `alldifferent` *forward checking* sulla cella corrente.

```python
def find_empty(grid: Grid) -> Optional[Tuple[int, int]]:
    best = None
    best_len = 10
    for r in range(9):
        for c in range(9):
            if grid[r][c] != 0:
                continue
            choices = candidate_values(grid, r, c)
            if not choices:
                return (r, c)              # dead-end immediato
            if len(choices) < best_len:
                best = (r, c)
                best_len = len(choices)
                if best_len == 1:
                    return best            # singleton, branca subito
    return best
```

- `find_empty` è l'euristica di **variable selection**: trova la cella vuota col dominio più piccolo (replica di `first_fail` in Python).
- Se trova una cella vuota con 0 candidati → la restituisce subito così il backtracking fallisce immediatamente (early fail).
- Se trova una cella con 1 solo candidato → la restituisce subito così il branching è banale (dopotutto è forced).

```python
def solve_python(grid: Grid, rng=None) -> Optional[Grid]:
    work = copy_grid(grid)
    def backtrack() -> bool:
        cell = find_empty(work)
        if cell is None:
            return True                    # tutte piene → soluzione
        row, col = cell
        values = candidate_values(work, row, col)
        if rng is not None:
            rng.shuffle(values)
        for value in values:
            work[row][col] = value
            if backtrack():
                return True
            work[row][col] = 0             # undo
        return False
    return work if backtrack() else None
```

- DFS con backtracking. Modifica `work` in-place; quando torna dopo il ricorsivo, ripristina `0` (undo).
- Il parametro `rng` opzionale randomizza l'ordine dei valori: utile per evitare il bias verso soluzioni lessicograficamente minime.

**Punti da saper difendere**:

- **"È un solver CP?"**
  → No, è un backtracking + forward checking *imperativo*, non un CP solver. Ma simula il comportamento del modello MiniZinc con `first_fail + indomain_min`. È un substitute pratico per il backend, non per la teoria del corso.
- **"Perché esiste se hai MiniZinc?"**
  → Per velocità (overhead startup MiniZinc ~400ms × 80 check × 20 griglie × 3 strategie × 2 metodi = troppo) e per indipendenza dall'installazione di MiniZinc nel benchmark sperimentale. Il modello CP resta il riferimento per la *correttezza*.

### 2.2 Counting con limite

```python
def count_solutions_python(grid: Grid, limit: int = 2) -> Tuple[int, Optional[Grid]]:
    work = copy_grid(grid)
    found = 0
    first_solution = None
    def backtrack() -> None:
        nonlocal found, first_solution
        if found >= limit:
            return                                    # short-circuit
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
```

**Walkthrough**:

- Stesso solver, ma **non si ferma alla prima soluzione**: continua a esplorare l'albero, conta le soluzioni trovate.
- Il `limit=2` è il trucco chiave per l'unicità: non interessa contare tutte le soluzioni (`#P-completo`), ma solo capire se sono ≥2.
- Lo `short-circuit` `if found >= limit: return` taglia l'esplorazione non appena trovato il secondo: tempi minimali sui puzzle non-unici.
- Restituisce sia il numero (0, 1, o 2) che la prima soluzione trovata.

**Punti da saper difendere**:

- **"È #P-completo?"**
  → No, perché il limite a 2 lo rende un problema in NP: basta esibire 2 soluzioni come testimonianza. Vedi `3_oral_theory_notes.md` §3.
- **"Per puzzle unici come si comporta?"**
  → Esaustivo: deve esplorare tutto l'albero per dimostrare che la seconda soluzione non esiste. È esattamente quello che farebbe il solve-and-block.

### 2.3 Solve-excluding (solve-and-block in Python)

```python
def solve_excluding_python(grid: Grid, forbidden: Grid) -> Optional[Grid]:
    work = copy_grid(grid)
    def backtrack() -> bool:
        cell = find_empty(work)
        if cell is None:
            if any(work[r][c] != forbidden[r][c] for r in range(9) for c in range(9)):
                return True                  # diversa da forbidden → ok
            return False                     # uguale a forbidden → rifiuta
        row, col = cell
        for value in candidate_values(work, row, col):
            work[row][col] = value
            if backtrack():
                return True
            work[row][col] = 0
        return False
    return work if backtrack() else None
```

**Walkthrough**:

- Identico a `solve_python` ma con un **filtro a fine ricerca**: se la soluzione completa coincide con `forbidden`, viene rifiutata e il backtracking continua.
- È la versione Python del modello `sudoku_non_unique_check.mzn`: cerca una soluzione che differisca dalla `forbidden` in almeno una cella.
- `any(work[r][c] != forbidden[r][c] for r,c)` è l'equivalente Python di `exists(i,j) (grid[i,j] != known_solution[i,j])`.

**Punti da saper difendere**:

- **"Perché filtrare a fine ricerca invece di propagare l'inequality?"**
  → Per semplicità implementativa. In CP propagare `grid != forbidden` come blocking constraint sarebbe più efficiente (taglia l'albero prima), ma in Python procedurale aggiungere logica di propagazione per un singolo vincolo non vale la pena.

### 2.4 Backend MiniZinc (subprocess + parsing)

```python
def run_minizinc(model, dzn_text, timeout_seconds, extra_flags=None):
    if shutil.which("minizinc") is None:
        raise RuntimeError("Il comando 'minizinc' non è disponibile nel PATH")
    project_root = model.parents[1]
    solver_config = project_root / "spec" / "gecode_local.msc"
    tmp_dir = project_root / "results"
    with tempfile.NamedTemporaryFile("w", suffix=".dzn", dir=tmp_dir, delete=False, ...) as h:
        h.write(dzn_text)
        temp_dzn = h.name
    try:
        cmd = ["minizinc", "--solver", str(solver_config)]
        if extra_flags:
            cmd.extend(extra_flags)
        cmd.extend([str(model), temp_dzn])
        if timeout_seconds is not None:
            cmd.extend(["--time-limit", str(timeout_seconds * 1000)])
        return subprocess.run(cmd, text=True, capture_output=True, check=False)
    finally:
        os.unlink(temp_dzn)
```

**Walkthrough**:

- Wrapper che chiama il binario `minizinc` come subprocess.
- Scrive un file `.dzn` temporaneo con i parametri (clues + eventualmente `known_solution`), invoca minizinc puntando al solver Gecode locale, cattura `stdout`/`stderr`.
- `--time-limit` è in millisecondi (per quello `* 1000`).
- `check=False` perché un return code != 0 è informativo (es. UNSAT non è un errore di sistema).

```python
def board_to_dzn(name: str, grid: Grid) -> str:
    flat = ", ".join(str(value) for row in grid for value in row)
    return f"{name} = array2d(1..9, 1..9, [{flat}]);\n"
```

- Serializza una griglia Python in formato DZN (data file MiniZinc): `name = array2d(1..9, 1..9, [v1, v2, ..., v81]);`. Layout row-major.

```python
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
```

- Parser per **una sola** soluzione MiniZinc.
- L'output di MiniZinc su `satisfy` ha questo formato:
  ```
  1 2 3 4 5 6 7 8 9
  4 5 6 7 8 9 1 2 3
  ...
  ----------
  ==========
  ```
  - 9 righe di numeri = la griglia
  - `----------` = separatore tra soluzioni (su `-a -n N`)
  - `==========` = ricerca esaurita (UNSAT o tutte le soluzioni emesse)
- Filtra i marker e le righe di status, raccoglie le righe da 9 numeri.

```python
def parse_minizinc_grids(output: str) -> List[Grid]:
    grids = []
    current = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if line.startswith("----------"):
            if len(current) == 9:
                grids.append(current)
            current = []
            continue
        ...
        if len(values) == 9:
            current.append(values)
    if len(current) == 9:
        grids.append(current)
    return grids
```

- Parser per il counting (più soluzioni separate da `----------`).
- Mantiene una griglia "in costruzione" `current`; ogni `----------` la chiude e ne apre una nuova.

#### `puzzle_status_minizinc_solve_and_block`

```python
solver_model = project_root / "models" / "sudoku_solver.mzn"
proc = run_minizinc(solver_model, board_to_dzn("clues", grid), timeout_seconds)
# parse first solution → solution
non_unique_model = project_root / "models" / "sudoku_non_unique_check.mzn"
dzn = board_to_dzn("clues", grid) + board_to_dzn("known_solution", solution)
second = run_minizinc(non_unique_model, dzn, timeout_seconds)
if second.returncode == 0 and parse_minizinc_grid(second.stdout) is not None:
    status = "multiple"
else:
    status = "unique"
```

- Due chiamate MiniZinc separate. Prima trova `S₁`, poi cerca `S₂ ≠ S₁` col modello `sudoku_non_unique_check.mzn`.

#### `puzzle_status_minizinc_counting`

```python
proc = run_minizinc(
    solver_model,
    board_to_dzn("clues", grid),
    timeout_seconds,
    extra_flags=["-a", "-n", "2"],
)
solutions = parse_minizinc_grids(proc.stdout)
search_complete = "==========" in proc.stdout
if len(solutions) >= 2:
    status = "multiple"
elif search_complete:
    status = "unique"
else:
    status = "unknown"     # 1 soluzione ma timeout, non posso decidere
```

- Una chiamata sola con `-a -n 2` (enumera fino a 2).
- Distingue 3 casi:
  - 0 soluzioni → `unsat`
  - 2 soluzioni → `multiple`
  - 1 soluzione + `==========` (search exhausted) → `unique`
  - 1 soluzione senza `==========` → `unknown` (timeout colpito mentre stava ancora cercando la seconda)

**Punti da saper difendere**:

- **"Perché un parser custom invece di MiniZinc-Python?"**
  → Per non aggiungere dipendenze pesanti. Lo stdout di MiniZinc è semi-strutturato (formato output dichiarato nei modelli), parsing line-by-line è banale e robusto.
- **"Cosa succede se MiniZinc cambia il formato di output?"**
  → Il parsing dipende dalle convenzioni `----------` e `==========` che sono parte dello standard FlatZinc, non cambieranno.
- **"Caso UNKNOWN?"**
  → Trattato esplicitamente come *non* `unique`: la pipeline ripristina la rimozione e logga. Vedi report §3.3.

### 2.5 Strategie di rimozione (`iter_positions`)

```python
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
        return sorted(positions, key=lambda item: abs(item[0]-4) + abs(item[1]-4), reverse=True)
    raise ValueError(...)
```

**Walkthrough**:

- **`random`**: permutazione casuale di tutte le 81 celle.
- **`symmetry`**: deduplica le coppie centrali. Per `(r,c)`, il mirror centrale è `(8-r, 8-c)`. Si genera una lista di rappresentanti (uno per coppia), poi si shuffla. Nel loop di rimozione, una rimozione include sempre anche il mirror.
  - Il `key = tuple(sorted(((r,c), mirror)))` garantisce che `(r,c)` e `(mirror)` abbiano la stessa chiave canonica → si scarta uno dei due.
  - Lo shuffle finale randomizza l'ordine tra coppie ma non rompe la simmetria.
  - Il caso `(4, 4)` (centro) è autosimmetrico (`mirror = (4,4)`), quindi il key è solo `((4,4),)` e viene incluso una sola volta. Nel loop di rimozione, non viene fatta una seconda rimozione perché `mirror == (r,c)`.
- **`density`**: ordina per distanza Manhattan dal centro (4,4) decrescente. Le celle d'angolo `(0,0), (0,8), (8,0), (8,8)` hanno distanza 8. Le centrali distanza 0. Si rimuovono prima le periferiche, ipotizzando abbiano meno vincoli incidenti.

**Punti da saper difendere**:

- **"Perché simmetria centrale e non altre?"**
  → È quella usata nei Sudoku editoriali (es. The Times). Riflessioni orizzontali/verticali sono usate meno; rotazioni di 90° non si applicano al Sudoku perché l'ordine delle 9 cifre nei blocchi non è invariante per rotazione.
- **"Density risparmia davvero?"**
  → I dati dicono di no in modo significativo: 25.4 medi vs 24.6 di random. L'ipotesi di partenza era "celle d'angolo hanno meno vincoli", ma in pratica la struttura del Sudoku rende tutte le celle ugualmente vincolate. Il valore della strategia è il *confronto*, non la performance.

### 2.6 Loop di generazione (`generate_puzzle`)

```python
def generate_puzzle(source_grid, backend, project_root, strategy, timeout, seed, method):
    rng = random.Random(seed)
    puzzle = copy_grid(source_grid)
    removal_log = []
    positions = iter_positions(strategy, rng)
    for row, col in positions:
        if puzzle[row][col] == 0:
            continue                                       # già rimossa
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
        status = evaluate_puzzle(project_root, puzzle, backend, timeout, method=method)
        accepted = status["status"] == "unique"
        if not accepted:
            puzzle[row][col] = previous                    # rollback
            if mirror is not None:
                puzzle[mirror[0]][mirror[1]] = mirror_prev
        removal_log.append({...})
    clues = sum(1 for row in puzzle for value in row if value != 0)
    return {"puzzle": puzzle, "solution": source_grid, "clues": clues, ...}
```

**Walkthrough**:

- È il **cuore** della pipeline. Greedy con rollback.
- Loop sulle posizioni nell'ordine deciso dalla strategia.
- Per ciascuna: salva il valore, prova a rimuoverla (e il mirror se symmetry), chiama il check di unicità.
- Se la rimozione fa perdere l'unicità → rollback completo (incluso mirror).
- Se la rimozione resta `unique` → cella confermata vuota.
- Output: il puzzle finale con i suoi `clues` (numero di celle non-zero), il `removal_log` con tutti i tentativi.

**Punti da saper difendere**:

- **"È un greedy. Ottimo?"**
  → No. Greedy locale: ogni cella o è rimossa o non lo è, mai riconsiderata. Per arrivare al limite teorico (17) servirebbe **backtracking sulla rimozione**: dopo un rifiuto, tornare indietro e provare a rimuovere altre celle prima. Discusso come "limite" nel report §7.
- **"Perché non si testa subito senza backup?"**
  → Backup + rollback sono necessari perché la rimozione modifica `puzzle` in-place. Se la modifica non è accettata, devi ripristinare lo stato precedente prima di passare alla cella successiva.
- **"Mirror in symmetry: due rimozioni in una sola decisione?"**
  → Sì, e questo spiega perché symmetry ha più clue: ogni rifiuto blocca 2 celle invece di 1. Statisticamente paghi double tax.

### 2.7 CLI

```python
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(...)
    sub = parser.add_subparsers(dest="command", required=True)
    
    solve_cmd = sub.add_parser("solve")
    check_cmd = sub.add_parser("check")
    gen_cmd = sub.add_parser("generate")
    ...
```

Tre subcommand:

- **`solve`**: prende un input JSON con `{"grid": [[...]]}`, restituisce una soluzione.
- **`check`**: prende un input JSON con `{"grid": [...]}`, restituisce `{status, solutions_found, elapsed_seconds, ...}`.
- **`generate`**: prende un sorgente (lista di griglie complete) e produce un puzzle generato. Output JSON con `puzzle`, `solution`, `clues`, `removal_log`.

Argomenti rilevanti:
- `--backend python|minizinc`
- `--method counting|solve-and-block`
- `--strategy random|symmetry|density`
- `--timeout SECONDS` (per minizinc)
- `--seed INT` (riproducibilità)

---

## 3. Script di orchestrazione

### 3.1 `run_full_benchmark.py`

**Cosa**: esegue il benchmark principale su 20 griglie × 3 strategie × 2 metodi = 120 run, salva CSV+JSON.

```python
selected = rng.sample(grids, args.num_grids)               # 20 da 50
for grid_idx, grid in enumerate(selected):
    for strategy in args.strategies:
        for method in args.methods:
            run_seed = args.seed * 1000 + grid_idx
            result = generate_puzzle(
                source_grid=copy_grid(grid),
                backend=args.backend, project_root=project_root,
                strategy=strategy, timeout_seconds=args.timeout,
                seed=run_seed, method=method,
            )
            rows.append({"grid_id": grid_idx, "strategy": strategy, "method": method,
                         "clues": result["clues"], ...})
```

**Walkthrough**:

- Triplo loop: grid × strategy × method.
- `run_seed = args.seed * 1000 + grid_idx` → ogni griglia ha un seed proprio derivato deterministicamente dal seed master. Cambiare il master cambia l'intero esperimento, fissato è riproducibile.
- Salva in CSV (per plot) e JSON (per ispezione manuale del puzzle generato).
- Importa `generate_puzzle` direttamente dal modulo `sudoku_pipeline` (non subprocess), riducendo overhead.

**Punti da saper difendere**:

- **"Perché 20 griglie?"**
  → Compromesso tra significatività statistica e tempo wall-clock. 50 sarebbe più robusto, ma 20 × 6 condizioni × ~10s/run = 20 minuti totali, già abbastanza per dare distribuzioni leggibili.
- **"Backend di default `python`?"**
  → Sì, perché MiniZinc su 1620+ chiamate sarebbe troppo lento. Il backend MiniZinc è verificato funzionalmente con un benchmark separato (`benchmark.py`) su un sottoinsieme.

### 3.2 `compare_strategies.py`

**Cosa**: esegue le 3 strategie su una sola griglia di partenza e raccoglie i risultati.

```python
for strategy in ("random", "symmetry", "density"):
    output_path = project_root / "results" / f"generated_{strategy}.json"
    cmd = [sys.executable, str(pipeline), "--project-root", str(project_root),
           "generate", "--source", args.source, "--output", str(output_path),
           "--backend", args.backend, "--strategy", strategy,
           "--seed", str(args.seed)]
    subprocess.run(cmd, ...)
    payload = json.loads(output_path.read_text())
    results.append({"strategy": strategy, "clues": payload["clues"], ...})
```

**Walkthrough**:

- Più "leggero" di `run_full_benchmark.py`: una sola griglia, le 3 strategie, niente matrice metodi.
- Usa subprocess (chiama il pipeline come CLI), non import diretto. Più lento ma più isolato (ogni run ha il suo processo).
- Output: 3 file `results/generated_<strategy>.json` con i 3 puzzle generati, e un file riassuntivo.
- Lo stesso seed per tutte e tre le strategie è significativo: confronto a parità di griglia di partenza.

**Punti da saper difendere**:

- **"Perché subprocess vs import?"**
  → Per coerenza con la modalità "user-facing": questo script simula come uno spettatore esterno userebbe la pipeline da CLI. Dimostra che la CLI funziona end-to-end. `run_full_benchmark.py` invece è ottimizzato per throughput.

### 3.3 `benchmark.py`

**Cosa**: benchmark minimale: prende un set di istanze già preparate, esegue `check` su ciascuna.

```python
for item in instances:
    write_json(temp_path, {"grid": item["grid"]})
    cmd = [sys.executable, str(pipeline), ..., "check",
           "--input", str(temp_path), "--backend", args.backend]
    proc = subprocess.run(cmd, ...)
    result = json.loads(proc.stdout)
    result["name"] = item["name"]
    results.append(result)
```

**Walkthrough**:

- Itera su istanze pre-definite (es. `data/test/benchmark_instances.json`).
- Per ognuna, scrive un file temp, chiama `sudoku_pipeline.py check`, raccoglie il risultato.
- Lo usiamo per il benchmark MiniZinc puro (`benchmark_minizinc_timeout300.json`) — verifica funzionale del backend MiniZinc senza il costo del loop di generazione completo.

**Punti da saper difendere**:

- **"Cos'è `benchmark_instances.json`?"**
  → Un set ridotto di istanze "famose" (puzzle unici noti, puzzle non unici, edge cases) per validare che il check di unicità sia corretto, indipendentemente dalla pipeline di generazione.

---

## 4. Import dataset

### 4.1 `import_kaggle_solutions.py` (reservoir sampling)

**Cosa**: estrae 50 griglie complete uniformemente casuali dal Kaggle CSV (1M righe).

```python
reservoir: list[str] = []
seen: set[str] = set()
total_rows = 0
with input_path.open("r") as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        total_rows += 1
        solution = row["solution"].strip()
        if solution in seen:
            continue
        if len(reservoir) < args.limit:
            reservoir.append(solution)
            seen.add(solution)
            continue
        idx = rng.randint(0, total_rows - 1)
        if idx < args.limit:
            old = reservoir[idx]
            seen.discard(old)
            reservoir[idx] = solution
            seen.add(solution)
```

**Walkthrough**:

- **Algoritmo R di Vitter** — sampling streaming uniforme da una sorgente di dimensione sconosciuta (in realtà nota qui, ma il pattern è streaming-friendly).
- Per i primi `k=50` elementi: riempi il reservoir.
- Per gli elementi successivi: con probabilità `k/i` (dove `i` è la posizione corrente), sostituisci un elemento casuale del reservoir.
- Risultato: ogni elemento del CSV ha probabilità identica `k/N` di finire nel reservoir, senza dover caricare 1M righe in memoria.
- `seen` evita duplicati testuali (alcune righe del Kaggle dataset sono ripetute).

```python
def parse_grid(text: str) -> list[list[int]]:
    if len(text) != 81 or any(ch not in "123456789" for ch in text):
        raise ValueError(...)
    values = [int(ch) for ch in text]
    return [values[row*9 : (row+1)*9] for row in range(9)]
```

- Il Kaggle CSV ha la colonna `solution` come stringa di 81 caratteri.
- Reshape a 9×9 row-major.

**Punti da saper difendere**:

- **"Perché reservoir e non `random.sample(list(rows), 50)`?"**
  → Perché il CSV è 1.4 GB (1M righe × ~163 char). Caricarlo tutto in memoria è ~3 GB di Python objects. Il reservoir lavora in O(1) memoria.
- **"Perché 50 e non 1M?"**
  → 50 è abbastanza per benchmark statistici (n=20 selezionate). 1M sarebbe inutile per questo scopo e rallenterebbe ogni rerun del benchmark.

---

## 5. Plot dei risultati — `plot_results.py`

**Cosa**: legge il CSV del benchmark e produce 3 PNG.

```python
def plot_time_vs_clues(rows, out_path):
    by_strategy = defaultdict(list)
    for row in rows:
        by_strategy[row["strategy"]].append((int(row["clues"]), float(row["total_seconds"])))
    for strategy, points in by_strategy.items():
        ax.scatter([p[0] for p in points], [p[1] for p in points], label=strategy, ...)
```

**Walkthrough**:

- **`plot_time_vs_clues`**: scatter con clue sull'asse X e secondi sull'asse Y, una serie per strategia. Mostra la correlazione (debole) tra meno clue e più tempo.
- **`plot_strategy_comparison`**: bar chart con la media + min/max range per strategia. Mostra che `random` produce meno clue.
- **`plot_method_comparison`**: bar chart con il tempo medio per check confrontando counting vs solve-and-block. Mostra che counting è ~1.8× più veloce.

**Punti da saper difendere**:

- **"Perché distanza media + min/max e non boxplot?"**
  → Boxplot più ricco ma con 20 punti per strategia non è informativo (i quartili coincidono con min/max). Bar+errorbar è più chiaro.

---

## 6. Packaging — `package_for_delivery.sh`

**Cosa**: crea lo zip finale di consegna.

```bash
INCLUDE=(
  "01_project_overview.md" "02_todo.md" "03_spec_notes.md" "04_architecture_and_risks.md"
  "README.md" "models" "scripts" "spec" "report"
  "data/solved/sample_solutions.json" "data/test"
  "data/generated/final_check_generated.json"
  "results/full_benchmark.csv" "results/full_benchmark.json"
  "results/benchmark_minizinc_timeout300.json" "results/final_check_benchmark.json"
  "results/generated_random.json" "results/generated_density.json" "results/generated_symmetry.json"
)
```

**Walkthrough**:

- Renderizza il PDF del report con `render_report_pdf.py` (pandoc + weasyprint + pypdf per il merge).
- Copia gli item della whitelist in uno staging dir.
- Pulisce `__pycache__`, `*.pyc`, `.DS_Store`.
- Zippa e cleanup.
- Gli include coprono: programs (models/, scripts/), datasets (data/solved + data/test + data/generated/...), results (full_benchmark + esperimenti specifici), report (md + pdf + assets), documentazione.

**Punti da saper difendere**:

- **"Cosa NON è incluso?"**
  → Il Kaggle CSV raw (1.4 GB, troppo grosso, link nel README), il `data/raw/` interno, file dev (kaggle_smoke), guida di collaborazione interna, virtualenv, `__pycache__`.

---

## 7. Configurazione del solver — `spec/gecode_local.msc`

**Cosa**: solver configuration (`.msc` = MiniZinc Solver Configuration) che dice a MiniZinc come trovare Gecode.

Contenuto tipico:
```json
{
  "id": "org.gecode.local",
  "name": "Gecode (local)",
  "executable": "fzn-gecode",
  "mznlib": "...",
  ...
}
```

**Walkthrough**:

- File JSON con i metadati del solver: come si chiama, dove sta il binario `fzn-gecode`, dove sono le librerie MiniZinc-specific.
- Punta al binario via PATH (`"executable": "fzn-gecode"`) per portabilità — non hardcoda un path assoluto.
- Si invoca con `minizinc --solver spec/gecode_local.msc <model> <data>`.

**Punti da saper difendere**:

- **"Perché un `.msc` custom invece di `gecode` di default?"**
  → Per garantire che il progetto giri anche su sistemi dove `gecode` non è registrato come solver MiniZinc di sistema (es. installato via brew/apt ma non via il MiniZinc IDE). Il `.msc` locale è autoesplicativo e portabile.

---

## Mappa veloce per l'orale

Quando il prof punta su un punto specifico, vai a queste sezioni:

| Domanda probabile | Sezione di riferimento |
|---|---|
| "Mostrami il modello base" | §1.1 `sudoku_solver.mzn` |
| "Spiegami `alldifferent`" | §1.1 + `3_oral_theory_notes.md` §1 |
| "Come fai il check di unicità?" | §1.5 + §2.2 + §2.4 + report §3 |
| "Perché due metodi di unicità?" | §2.2 vs §2.3 + report §3 + theory §5 |
| "Come gestisci i timeout?" | §2.4 (caso UNKNOWN) + report §3.3 |
| "Strategie di rimozione?" | §2.5 + §2.6 + report §4.2 |
| "Perché Python e MiniZinc insieme?" | §2.4 + report §5 |
| "Cosa c'è di teorico?" | `3_oral_theory_notes.md` (file separato) |
| "Quanti indizi minimi?" | report §6.2 + tabella |
| "Vincoli ridondanti servono?" | §1.2 + report §2.2 + §6.5 |

---

## Esempio "live" da preparare

Tienine pronto uno da mostrare se il prof chiede una demo:

1. Apri `data/test/unique_puzzle.json` — è un puzzle 9×9 con 30 clue noto unico.
2. Mostra:
   ```
   python3 scripts/sudoku_pipeline.py check \
     --input data/test/unique_puzzle.json \
     --backend python --method counting
   ```
   → Output: `{"status": "unique", "solutions_found": 1, "elapsed_seconds": 0.001, ...}`.
3. Spiega: il counting ha enumerato fino a `n=2`, ne ha trovato solo 1 + ricerca esaurita → `unique`.
4. Cambia `--method solve-and-block`: stessa risposta, tempi simili.
5. Cambia con `data/test/non_unique_puzzle.json`: `multiple`. Spiega: counting si ferma alla seconda soluzione, solve-and-block trova `S₂ ≠ S₁` velocemente perché la prima ricerca trova `S₁` e la seconda parte da uno stato propagato.
