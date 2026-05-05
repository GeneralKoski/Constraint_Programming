# Note di Teoria per l'Orale

Riassunto degli argomenti teorici del corso che possono essere chiesti durante la discussione del progetto Sudoku Instance Generation. Ogni sezione contiene la "lavagna mentale" minima da poter spiegare a voce, più dettagli da approfondire se servono.

## Indice

1. [Teorema di Régin e filtering di `alldifferent`](#1-teorema-di-régin-e-filtering-di-alldifferent)
2. [NP-completezza del Sudoku generalizzato](#2-np-completezza-del-sudoku-generalizzato)
3. [#P-completezza del solution counting](#3-p-completezza-del-solution-counting)
4. [Arc Consistency vs Bounds Consistency](#4-arc-consistency-vs-bounds-consistency)
5. [Solve-and-block vs Solution counting](#5-solve-and-block-vs-solution-counting)
6. [Strategie di ricerca (variable e value selection)](#6-strategie-di-ricerca-variable-e-value-selection)
7. [Vincoli globali notevoli](#7-vincoli-globali-notevoli)
8. [Reificazione](#8-reificazione)
9. [Vincoli ridondanti](#9-vincoli-ridondanti)
10. [Symmetry breaking](#10-symmetry-breaking)
11. [Branch and bound (ottimizzazione)](#11-branch-and-bound-ottimizzazione)
12. [Modello CSP formale](#12-modello-csp-formale)
13. [Domande probabili e risposte rapide](#13-domande-probabili-e-risposte-rapide)

---

## 1. Teorema di Régin e filtering di `alldifferent`

### Setup

Il vincolo `alldifferent(x₁, …, xₙ)` impone che tutte le variabili abbiano valori distinti. Una formulazione naive è `forall(i ≠ j) (xᵢ ≠ xⱼ)`, ma propaga male: ottiene solo bounds consistency, non arc consistency.

### Costruzione del grafo bipartito

Si costruisce il **value graph** `G = (V, E)`:
- nodi a sinistra: variabili `x₁, …, xₙ`;
- nodi a destra: valori `v₁, …, vₘ` nei domini;
- archi: `(xᵢ, v) ∈ E ⟺ v ∈ D(xᵢ)`.

Una **soluzione** del vincolo è un *matching* che copre tutte le variabili (perfect matching dal lato delle variabili).

### Berge (1970) e Régin (1994)

**Teorema (Berge)**: un matching `M` è massimo ⟺ non esiste un *augmenting path* rispetto a `M`.

**Conseguenza utile**: un arco `(xᵢ, v)` appartiene a *qualche* matching massimo ⟺ appartiene a `M` o a un *alternating cycle* o *alternating path* che parte da un nodo libero.

### Algoritmo di filtering (Régin, 1994)

1. trovare un matching massimo `M` (Hopcroft-Karp, `O(E·√V)`);
2. se `|M| < n`: il vincolo è **inconsistente** → fail;
3. orientare gli archi: archi di `M` da right→left, gli altri da left→right;
4. trovare le **componenti fortemente connesse** (SCC) e i nodi raggiungibili da nodi liberi;
5. un arco `(xᵢ, v)` può essere rimosso dal dominio sse non sta in `M` e non è in una SCC con un arco di `M`, e non è raggiungibile da un nodo right libero via alternating path.

**Complessità**: `O(E + V)` per il filtering (dopo aver pre-calcolato il matching). Permette di mantenere arc consistency in modo efficiente.

### Relevance per Sudoku

Ogni riga, colonna, blocco è un `alldifferent` su 9 variabili e 9 valori. Régin garantisce che ogni propagazione elimina dai domini *tutti* i valori incoerenti, non solo i bound. Su una griglia con poche celle compilate, questo accelera molto la propagazione iniziale e il branching.

---

## 2. NP-completezza del Sudoku generalizzato

### Statement

Il problema decisionale "data una griglia parziale Sudoku `n²×n²` (con blocchi `n×n`), esiste un completamento valido?" è **NP-completo**.

### Dimostrazione (sketch)

**NP**: dato un completamento, si verifica in tempo polinomiale che ogni riga, colonna e blocco contengano valori distinti.

**NP-hardness**: si riduce **Latin Square Completion** (NP-completo, Colbourn 1984) a Sudoku. Una `n²×n²` Sudoku partial-filled può codificare una `n²×n²` Latin square, perché i vincoli di blocco si possono "soddisfare banalmente" se aggiungiamo righe ausiliarie. Più preciso: ogni Latin square `n×n` può essere completato sse esiste un Sudoku `n²×n²` di appropriata struttura.

Yato e Seta (2003) hanno mostrato anche che il problema "ha esattamente una soluzione?" (USAT su Sudoku) è in **DP**, e contare le soluzioni è **#P-completo**.

### Implicazione pratica

Per Sudoku 9×9 fissato (n=3), il problema è banale (numero di griglie limitato), ma l'analisi asintotica giustifica perché serve un solver CP serio invece di un'enumeration brute-force scalabile.

---

## 3. #P-completezza del solution counting

### Definizione

Una funzione `f` è **#P** se esiste una macchina di Turing non-deterministica polinomiale `M` tale che `f(x) = #(percorsi accettanti di M su x)`.

`#P-completa` per riduzione parsimoniosa.

### Per Sudoku

"Quante completamenti validi ha questa griglia parziale?" è #P-completo (Yato 2003). Implicazione: non si conosce un algoritmo polinomiale per contare; al peggio si enumera.

### Cosa significa per il progetto

Per il check di unicità non serve contare *tutte* le soluzioni: basta sapere se ce ne sono `≥2`. Questo è un caso facile (basta fermarsi al secondo). Quindi nella pratica si fa una "approssimazione one-sided": il counting si limita a `n=2` invece di esaustivo. Tecnicamente: `#≥2` è in NP (basta esibire due soluzioni), non #P-completo.

Solve-and-block fa la stessa cosa con un'altra struttura: solve, blocking, solve. Anche questo è in NP.

---

## 4. Arc Consistency vs Bounds Consistency

### Definizioni

Sia `c(x, y)` un vincolo binario.

**Arc-consistent (AC)**: per ogni `a ∈ D(x)`, esiste `b ∈ D(y)` con `c(a, b)`. E viceversa.

**Bounds-consistent (BC)**: per ogni `a ∈ {min(D(x)), max(D(x))}`, esiste `b ∈ D(y)` con `c(a, b)`. E simmetricamente.

AC ⟹ BC, ma non viceversa.

### Algoritmi

- **AC-1** (Mackworth 1977): rivisita ripetutamente tutti i vincoli finché niente cambia. `O(end³)` con `n` variabili, `e` vincoli, `d` dim. dominio. Inefficace.
- **AC-3** (Mackworth 1977): mantiene una coda di archi da rivedere. `O(ed³)`. Standard nei solver moderni.
- **AC-4** (Mohr e Henderson 1986): tiene supporti pre-calcolati. `O(ed²)` ma overhead alto in pratica.

### Per Sudoku

Su `alldifferent`, AC è realizzato in modo *globale* dall'algoritmo di Régin (vedi §1), non come AC-3 sui singoli `≠`. La differenza è netta:

- formulazione disgiuntiva con `xᵢ ≠ xⱼ` ottiene solo BC su singoli vincoli (quando `D(xᵢ) = {a}`, rimuove `a` da `D(xⱼ)`);
- `alldifferent` come global ottiene AC: rimuove ogni valore non sopportato da un matching massimo.

In pratica su Sudoku la differenza è enorme nei branch iniziali, perché molte celle hanno dominio pieno `{1..9}` e le sole disuguaglianze a coppie non bastano a propagare cancellazioni globali.

---

## 5. Solve-and-block vs Solution counting (sintesi)

| Aspetto | Solve-and-block | Solution counting |
|---|---|---|
| Numero di ricerche | 2 (con re-start) | 1 (continua) |
| Vincoli aggiuntivi | sì (blocking constraint) | no |
| Esprimibile in MiniZinc | con un secondo modello | con flag `-a -n 2` |
| Dimostrare unicità | UNSAT della seconda ricerca | esaurire l'albero |
| Overhead per puzzle unici | doppio start | albero completo |
| Vantaggio | propagazione dalla blocking | riuso del search state |

Nel progetto: counting ~1.8× più veloce su Python; entrambi corretti.

---

## 6. Strategie di ricerca (variable e value selection)

### Albero di ricerca

Un solver CP con `complete` esplora un **search tree**: ogni nodo è uno stato (i domini correnti delle variabili), ogni branch è una decisione "fissa una variabile a un valore". Il branching è guidato da due euristiche:

- **variable selection**: quale variabile scegliere come prossima.
- **value selection**: quale valore provare per primo.

Dopo ogni decisione il solver propaga (es. via Régin per `alldifferent`); se un dominio si svuota, fallisce e fa backtrack.

### Variable selection

| Strategia | Cosa fa | Quando si usa |
|---|---|---|
| `input_order` | nell'ordine dell'array | baseline didattica, raramente la migliore |
| `first_fail` | dominio più piccolo | euristica fail-first: massimizza il branching factor effettivo, riduce profondità del sotto-albero esplorato |
| `smallest` | valore minimo del dominio | utile per ottimizzazione con direzione nota |
| `largest` | valore massimo del dominio | duale di `smallest` |
| `most_constrained` | più vincoli incidenti | euristica statica, utile su problemi sparsi |
| `dom_w_deg` | dominio diviso per peso accumulato | weighted-degree (Boussemart 2004): la variabile cresce di peso ogni volta che un constraint causa un wipe-out. Fail-first dinamico, sensibile alla storia. |
| `impact` | impatto stimato sul prodotto dei domini | impact-based search (Refalo 2004), più costoso ma molto buono su problemi grandi |

**Sul Sudoku**: `first_fail` è il default ragionevole perché molte celle iniziali hanno domini piccoli (clue → singleton, propagazione → dominio ridotto). `dom_w_deg` aggiunge robustezza ma su 9×9 il guadagno è dentro la varianza.

**Principio fail-first** (Haralick & Elliott, 1980): se devi sbagliare, sbaglia presto. Branca prima sulle variabili "difficili" così che un failure venga scoperto vicino alla radice e tagli un sotto-albero piccolo invece di uno grande.

### Value selection

| Strategia | Cosa fa |
|---|---|
| `indomain_min` | prova prima il valore minimo |
| `indomain_max` | prova prima il valore massimo |
| `indomain_median` | prova prima il valore mediano |
| `indomain_random` | ordine casuale |
| `indomain_split` | branca su `x ≤ mid` vs `x > mid` (binary search) |
| `indomain_reverse_split` | duale, prova prima `x > mid` |

**Principio succeed-first**: se devi avere successo, prova prima i valori "facili". Su problemi di soddisfazione la differenza tra `indomain_min` e `indomain_random` è grande quando l'istanza ha forte struttura: il min può cadere in un sotto-albero senza soluzioni e ci si blocca per ore.

**Sul Sudoku-generation**: `indomain_random` è essenziale per `sudoku_generate_full_grid.mzn` perché altrimenti si ottiene sempre la stessa griglia (la prima lessicograficamente minima).

### Strategia di esplorazione

| Modalità | Cosa fa |
|---|---|
| `complete` | DFS con backtracking esaustivo, dimostra UNSAT |
| `bounded` (LDS, Limited Discrepancy Search) | esplora prima i percorsi che si discostano poco dall'euristica |
| `restart` | riparte da capo con seed diversi (utile con randomizzazione) |

**Per il check di unicità serve `complete`**: senza esaurire l'albero non puoi dimostrare UNSAT.

---

## 7. Vincoli globali notevoli

### `alldifferent(x₁, …, xₙ)`

Tutte le variabili hanno valori distinti. Filtering: Régin (vedi §1). Complessità: `O(E√V)` per il matching iniziale, `O(E+V)` per filtering incrementale. AC garantita.

### `cumulative(start, dur, res, capacity)`

Vincolo per scheduling: dato un insieme di task con start time, durata e consumo di risorsa, la somma delle risorse usate in ogni istante non supera `capacity`. Filtering: time-table, edge-finding, energetic reasoning. Tipicamente bounds consistency.

### `circuit(succ)`

`succ[i]` è il successore di `i`. L'array deve formare un singolo ciclo Hamiltoniano. Usato per TSP, scheduling con setup. Filtering: matching + connectivity check.

### `table(vars, allowed_tuples)`

Vincolo estensionale: le `vars` devono assumere uno dei valori in `allowed_tuples` (lista esplicita). Utile quando il vincolo è troppo complesso per essere espresso in forma chiusa, ma il numero di tuple è gestibile. Filtering: GAC (algoritmi `STR2`, `STR3`, `Compact-Table`).

### `element(idx, array, val)`

`val = array[idx]` con `idx` variabile. Permette indicizzazioni dipendenti da decisioni del solver. Supporta GAC.

### `lex_less` / `lex_lesseq`

Ordinamento lessicografico tra array. Usato per **rompere simmetrie** (vedi §10).

### `regular(x, dfa)`

La sequenza `x` deve appartenere al linguaggio descritto da un automa finito deterministico. Utile per pattern (es. shift di scheduling).

**Sul progetto**: usiamo solo `alldifferent`. Gli altri sono parte del programma del corso e potrebbero essere chiesti come confronto.

---

## 8. Reificazione

**Definizione**: dato un vincolo `c`, la sua reificazione è una variabile booleana `b` legata da `b ⟺ c`. Permette di trattare la soddisfazione di `c` come un valore manipolabile.

```minizinc
var bool: b;
constraint b <-> (x + y > 5);
constraint b -> (z = 10);
```

**Half-reification**: `b → c` o `c → b` invece del biimplicazione completo. Più debole ma più facile da propagare.

**Esempi d'uso**:

- contare quanti vincoli sono soddisfatti: `sum([b1, b2, ..., bn]) >= k`;
- vincoli condizionali: "se b allora x = 5";
- soft constraints: assegna un costo a `1 - b`.

**Filtering sotto reificazione**: la propagazione del solver agisce sull'implicazione. Se il sub-vincolo `c` diventa entailed, `b` viene fissato a true. Se `c` diventa unsatisfiable, `b` viene fissato a false. Idem viceversa.

**Sul progetto**: non usata direttamente, ma un'estensione naturale sarebbe contare il numero di celle vuote come `sum(grid[i,j] = 0) = clues_count` e fare branch-and-bound su `clues_count` per minimizzarlo (vedi §11).

---

## 9. Vincoli ridondanti

**Definizione**: vincoli `c'` *implicati* da quelli del modello (cioè `c ⟹ c'`), aggiunti per migliorare la propagazione, non per cambiare l'insieme delle soluzioni.

**Quando aiutano**: quando il propagator di `c'` deduce informazioni che il propagator di `c` non riesce a ottenere da solo, perché lavora su una struttura algebrica diversa.

**Esempio classico**: `alldifferent(x₁, …, xₙ)` con `xᵢ ∈ 1..n`. Il propagator di Régin garantisce AC. Aggiungere `sum(xᵢ) = n(n+1)/2` non cambia le soluzioni, ma fornisce **bound consistency** sulla somma — utile se hai informazione lineare da combinare.

**Sul Sudoku 9×9**: i vincoli `sum=45` su righe/colonne/blocchi sono implicati da `alldifferent`. In pratica il guadagno è marginale (`alldifferent` è già fortissimo), ma esistono come dimostrazione del principio. Su problemi dove i propagatori globali sono assenti, i vincoli ridondanti possono fare la differenza tra "minuti" e "ore".

**Regola pratica**: aggiungi vincoli ridondanti quando (a) sono cheap da propagare, (b) catturano una struttura che i tuoi global non vedono, (c) il benchmark dimostra il guadagno.

---

## 10. Symmetry breaking

### Definizioni

Una **simmetria** di un CSP è una bijezione delle variabili o dei valori che preserva l'insieme delle soluzioni. Tipi:

- **Variable symmetry**: scambiare `x_i` con `x_j` mappa soluzioni in soluzioni.
- **Value symmetry**: rinominare i valori (es. permutare `1, 2, 3`) preserva le soluzioni.
- **Constraint symmetry**: la struttura dei vincoli è invariante per certe operazioni (es. rotazione del piano in geometria).

### Perché rompere le simmetrie

Senza symmetry breaking, il solver esplora `k` versioni equivalenti di ogni soluzione (`k` = ordine del gruppo di simmetria), gonfiando l'albero di ricerca. Per problemi con simmetrie ricche, è la differenza tra "esponenziale" e "trattabile".

### Tecniche

**Lex-leader**: tra tutte le permutazioni equivalenti, mantieni solo quella lessicograficamente minima. Implementato con `lex_less` o `lex_lesseq`:

```minizinc
constraint lex_less(row(grid, 1), row(grid, 2));      % rompe simmetria righe-righe
```

Pro: dichiarativo, gestito dal solver. Con: a volte i vincoli aggiuntivi rallentano la propagazione.

**SBDS** (Symmetry Breaking During Search): durante la ricerca, dopo un fallimento, aggiungi dinamicamente vincoli che escludono permutazioni equivalenti. Più costoso ma più mirato.

**SBDD** (Symmetry Breaking via Dominance Detection): prima di esplorare un nodo, verifica se è dominato da uno già visitato. Costoso ma efficace su simmetrie ricche.

### Sul Sudoku

Il Sudoku ha simmetrie *del problema generale* (relabeling delle 9 cifre, swap di 3 righe nello stesso band, swap delle 3 band, trasposizione, rotazioni di 90°/180°/270°), ordine totale del gruppo: `9! × 6³ × 6 × 6³ × 2 = 6,670,903,752,021,072,936,960` simmetrie sull'insieme delle griglie complete. Ma:

- Quando si **risolve** un puzzle dato, le simmetrie sono già rotte dalle clue (le clue specifiche distinguono "1" da "9" e fissano l'orientamento). Quindi la search del modello base non soffre di simmetria.
- Quando si **generano griglie complete** (`sudoku_generate_full_grid.mzn`), tutte le simmetrie sono attive. Lex-leader sulle prime righe/colonne accelera significativamente.

**Sul progetto**: non implementiamo symmetry breaking esplicito perché il setting è "puzzle parzialmente fissato" → simmetrie già rotte. Lo ricordiamo come *limite di estensione* (report §7).

### Symmetry-aware removal (≠ symmetry breaking)

Attenzione a non confondere: la strategia `symmetry` di rimozione delle clue (`scripts/sudoku_pipeline.py`, `iter_positions`) **non rompe** le simmetrie del CSP. Rimuove coppie di celle simmetriche per ottenere puzzle visivamente simmetrici (estetica). Sono due cose diverse: una è una scelta di branching/output, l'altra è una proprietà del modello.

---

## 11. Branch and bound (ottimizzazione)

### Setup

Per problemi di ottimizzazione, il solver cerca una soluzione che minimizzi (o massimizzi) una variabile obiettivo `obj`. In MiniZinc:

```minizinc
solve minimize obj;
```

Il solver fa **branch and bound**: mantiene una **lower bound** (min teorico) e un **incumbent** (migliore soluzione trovata finora). Quando esplora un branch, calcola un bound sul valore di `obj` raggiungibile in quel sotto-albero. Se il bound è ≥ incumbent (per minimizzazione), pota.

### Strategie

- **Linear B&B**: trova una soluzione con `obj = v`, aggiunge `obj < v` come vincolo, riparte. Iterativo. Default in molti solver CP.
- **Dichotomic search**: bisezione sui valori dell'obiettivo. Utile quando la valutazione di `obj` è costosa.
- **LDS+B&B**: combinazione, esplora prima i percorsi euristicamente promettenti.

### Sul progetto

Non usiamo `minimize` nel modello CP. La minimizzazione del numero di clue è **esterna**: la pipeline Python implementa un **greedy** (rimuovi se resta unica, altrimenti rollback) senza branch and bound sulla rimozione. È l'origine del gap tra 22 (raggiunto) e 17 (limite teorico):

- Il greedy può fallire localmente: una clue non rimovibile a un certo punto potrebbe diventarlo se prima rimuovessi un'altra clue.
- Branch and bound sulla rimozione esplorerebbe l'albero di "scelte di rimozione". Costoso (81! ordinamenti) ma con potatura via pseudo-ottimo (incumbent = miglior numero di clue trovato) può tagliare molto.

### Esempio "what if" da spiegare

> "Se volessi davvero scendere a 17 clue, come faresti?"

1. Riformula come problema di ottimizzazione: variabili `mask[i,j] ∈ {0,1}` (1 = clue mantenuta), `obj = sum(mask)`. Vincolo: il puzzle definito da `mask · grid_completa` ha soluzione unica.
2. Codifica l'unicità come vincolo: difficile da esprimere in CP standard (`#solutions = 1` è un quantificatore). Si esprime come problema **iterato**: per ogni candidato `mask`, un sub-solver verifica unicità.
3. Branch and bound: ad ogni nodo, prova a rimuovere un'altra clue; se il puzzle resta unico, ricorri; altrimenti backtracking.
4. Bound euristico: numero di clue rimanenti. Pruning: se un sotto-albero non può scendere sotto l'incumbent (es. tutte le rimozioni testate sono state rifiutate), pota.

Costo: ore di calcolo. McGuire 2012 ha dimostrato il limite di 17 enumerando tutte le griglie complete (5.5×10⁹) e per ciascuna verificando se esiste un sottoinsieme di 16 clue che la determina univocamente (tramite hitting set + checker CP), su cluster.

---

## 12. Modello CSP formale

### Definizione

Un **CSP** (Constraint Satisfaction Problem) è una tripla `(X, D, C)` dove:

- `X = {x₁, …, xₙ}` insieme di variabili;
- `D = {D(x₁), …, D(xₙ)}` insieme dei domini (uno per variabile);
- `C = {c₁, …, cₘ}` insieme di vincoli, ognuno con uno scope `S(cᵢ) ⊆ X` e una relazione `R(cᵢ) ⊆ ∏_{x ∈ S(cᵢ)} D(x)`.

Una **soluzione** è un assegnamento `α : X → ⋃ D` con `α(xᵢ) ∈ D(xᵢ)` che soddisfa tutti i vincoli.

### Sudoku come CSP

- `X = {grid[i,j] : i, j ∈ 1..9}`, |X| = 81;
- `D(grid[i,j]) = {1..9}` (per le clue: `D(grid[i,j]) = {clue}`);
- `C` = 27 vincoli `alldifferent` (9 righe + 9 colonne + 9 blocchi) + le uguaglianze delle clue.

### Soddisfacibilità (CSP decisionale)

"Esiste una soluzione?" è **NP-completo** in generale. Per Sudoku generalizzato `n²×n²`, NP-completo (Yato & Seta 2003). Per 9×9 fissato, banale (numero di griglie = 6,670,903,752,021,072,936,960).

### COP (Constraint Optimization Problem)

`(X, D, C, f)` con `f : Sol → ℝ` funzione obiettivo. Cerchi `arg min/max f(α)` tra tutti gli `α` che soddisfano `C`. Risolto via branch and bound (vedi §11).

---

## 13. Domande probabili e risposte rapide

**"Perché alldifferent è meglio di tante disuguaglianze?"**
→ AC vs BC. Régin filtra valori non sopportati da nessun matching massimo, le disuguaglianze a coppie no. Vedi §1.

**"Perché due metodi di unicità invece di uno?"**
→ Per *confrontarli* come richiesto dalla specifica. Il counting riusa search state, solve-and-block riparte. Sono entrambi corretti, differiscono in efficienza. Vedi §5.

**"Come gestisci il caso UNKNOWN da timeout?"**
→ Mai trattato come unique. Si rolledback la rimozione. Si registra nei log per quantificare. Vedi report §3.3.

**"Il minimo a 17 indizi vale per le tue strategie?"**
→ No, le strategie greedy senza backtracking sulla rimozione si fermano a 22-25. Il minimo a 17 (McGuire 2012) richiede algoritmi più sofisticati e ore di calcolo. Vedi report §6.2 e §11.

**"Qual è il ruolo del backend Python?"**
→ Validazione end-to-end senza dipendere da MiniZinc, e benchmark veloce (l'overhead di startup MiniZinc è ~400ms). Non sostituisce il modello CP, lo riproduce procedurally per il controllo di unicità. Vedi report §5.1.

**"Perché generare le griglie complete invece di usare solo Kaggle?"**
→ Per autonomia e validazione: i benchmark principali usano Kaggle come sorgente sperimentale pubblica, ma il modello CP `sudoku_generate_full_grid.mzn` resta utile come fallback, verifica strutturale e dimostrazione che il progetto non dipende esclusivamente da dati esterni.

**"Cosa cambierebbe con search annotations diverse?"**
→ Con `dom_w_deg` si pesa la storia dei fallimenti, utile su istanze fortemente vincolate. Con `indomain_random` si esplora un sotto-albero diverso, utile per generare griglie diverse. Su Sudoku 9×9 il guadagno di una variable selection più sofisticata è marginale; su 16×16 sarebbe più evidente. Vedi §6.

**"Quanto sono utili i vincoli ridondanti `sum=45`?"**
→ Marginale su Sudoku 9×9 perché `alldifferent` è già forte. Servono per dimostrazione pedagogica: i vincoli ridondanti rinforzano la propagazione lineare e aiutano in problemi con propagator nativi più deboli. Vedi §9.

**"Perché `first_fail` e non `input_order`?"**
→ Fail-first principle (Haralick & Elliott 1980): se devi sbagliare, sbaglia presto. Branca prima sulle variabili col dominio più piccolo. Vedi §6.

**"Cosa è la reificazione e perché potrebbe servire qui?"**
→ Trasformare un vincolo in una bool variable. Utile per soft constraints, conteggi, vincoli condizionali. Sul Sudoku non l'uso direttamente; un'estensione del progetto userebbe reificazione per esprimere "la cella (i,j) è una clue" e poi minimizzarne la somma. Vedi §8 e §11.

**"Cosa è un CSP formalmente?"**
→ Tripla `(X, D, C)`. Sudoku ha 81 variabili in `1..9`, 27 alldifferent + le clue come uguaglianze. Vedi §12.

**"NP-completezza, è banale 9×9?"**
→ Sì, numero di griglie limitato. La NP-completezza vale per la versione generalizzata `n²×n²`. La motivazione di usare un solver CP è: *anche* per il caso fisso, la struttura del problema favorisce CP (propagation forte) rispetto a brute-force enumeration. Vedi §2.

**"Counting solutions è #P-completo?"**
→ Contare *tutte* le soluzioni sì. Contare fino a 2 (`#≥2`) è in NP, basta esibire 2 soluzioni come testimonianza. Il progetto sfrutta questo. Vedi §3.

**"Hai gestito le simmetrie del Sudoku?"**
→ Nel modello base no, perché le clue rompono già le simmetrie. Per il modello di generazione delle griglie complete potrei aggiungere `lex_less` sulle prime righe — è un'estensione documentata in §10 e nel report §7.
