# DS/CMPSC 442 – Project 2: Adversarial Search

Two game-playing agents built with **minimax search + alpha-beta pruning** (Python 3.9+).

| Part | What it is | How to run |
|---|---|---|
| Q1 – Wild Tic-Tac-Toe | Modified pygame tic-tac-toe AI that plays the "wild" rules | `cd tictactoe-ai` then `python main.py` |
| Q2 – Territory Control | 6×6 strategy game, AI plays both teams and prints every move | `python solution_q2.py` |

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate     Mac/Linux: source .venv/bin/activate
pip install pygame
```

## Q1 – Wild Tic-Tac-Toe

**Rules:** if a player makes three in a row, the opponent gets **one more move**.
If that move makes three in a row for the opponent, the opponent wins; otherwise
the first player to make a line wins. (A second reading, "making a line loses,"
is also supported: set `RULES = "MISERE"` at the top of `tictactoe/board.py`.)

What changed:

- **`tictactoe/board.py`**: the board now remembers move order (`history`), because
  the winner depends on *who* made a line first and what happened on the next move.
  `winner()`, `is_draw()` and the new `first_line()` / `pending_line()` apply the wild rules.
- **`tictactoe/engine.py`**: minimax keeps searching after a line is made (the game
  isn't over until the reply), loss scores now prefer losing later, and the AI opens
  in the **center**, which solving the full game shows is the best first move.
- **`tictactoe/gui.py`**: shows "Last chance for …!" while a player has their reply move.

Tested against every possible opponent strategy: moving first, the AI never loses under either rule set.

## Q2 – Territory Control

- Board values come from `input.txt` (36 integers, row-major).
- Columns are **A–F**, rows are **1–6** (e.g. `C3`), matching the handout figures.
- Each turn: **Strategic Deployment** (claim any empty tile) or **Tactical Assault**
  (claim an empty tile next to one you own; adjacent enemy tiles flip to you).
- Utility = Alpha score − Bravo score. Alpha is MAX, Bravo is MIN.
- Search depth defaults to 4; change it with `python solution_q2.py input.txt 5`.

Printed board format: `A:66` = Alpha owns it, `B:66` = Bravo owns it, `66` = unclaimed.
