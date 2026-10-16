"""
DS/CMPSC 442 - Project 2, Question 2.1
Minimax (with alpha-beta pruning) agent for the 6x6 Territory Control game.

Run:   python solution_q2.py              (reads input.txt, search depth 4)
       python solution_q2.py board.txt 4  (optional: other input file / depth)

Board coordinates follow the handout figures: columns are letters A-F
(left to right) and rows are numbers 1-6 (top to bottom), e.g. C3.

Rules implemented
  * Team Alpha moves first, then the teams alternate.
  * Strategic Deployment: claim ANY empty tile. Nothing else changes.
  * Tactical Assault: from a tile you own, claim an empty tile directly
    up/down/left/right of it. Every enemy tile directly next to the new
    tile is converted to your team (conversion is automatic/mandatory).
  * The game ends when every tile is owned. Highest total value wins.

Note: an assault that would capture nothing gives the exact same board as
a deployment on that tile, so for each empty tile the agent only considers
one action: an assault if it captures something, otherwise a deployment.
"""

import os
import re
import sys

SIZE = 6
N_TILES = SIZE * SIZE
EMPTY, ALPHA, BRAVO = 0, 1, -1
TEAM_NAME = {ALPHA: "Team-Alpha", BRAVO: "Team-Bravo"}
TEAM_TAG = {ALPHA: "A", BRAVO: "B"}
DEFAULT_DEPTH = 4

# Orthogonal neighbours of every tile (no diagonals)
NEIGHBORS = []
for _i in range(N_TILES):
    _r, _c = divmod(_i, SIZE)
    _adj = []
    for _dr, _dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        _nr, _nc = _r + _dr, _c + _dc
        if 0 <= _nr < SIZE and 0 <= _nc < SIZE:
            _adj.append(_nr * SIZE + _nc)
    NEIGHBORS.append(tuple(_adj))


def tile_name(index):
    """0 -> 'A1', 7 -> 'B2' (column letter + row number)"""
    row, col = divmod(index, SIZE)
    return f"{chr(ord('A') + col)}{row + 1}"


# --------------------------------------------------------------------------
# Game state
# --------------------------------------------------------------------------
class Game:
    def __init__(self, values):
        self.values = values
        self.owner = [EMPTY] * N_TILES
        self.empty_count = N_TILES
        # score_diff = Alpha total - Bravo total (kept up to date for speed)
        self.score_diff = 0

    def is_over(self):
        return self.empty_count == 0

    def score(self, team):
        return sum(v for v, o in zip(self.values, self.owner) if o == team)

    def legal_actions(self, team):
        """Return a list of actions: (kind, source, target, captured_tiles)."""
        actions = []
        for t in range(N_TILES):
            if self.owner[t] != EMPTY:
                continue
            source = None
            captures = []
            for n in NEIGHBORS[t]:
                if self.owner[n] == team and source is None:
                    source = n
                elif self.owner[n] == -team:
                    captures.append(n)
            if source is not None and captures:
                actions.append(("assault", source, t, tuple(captures)))
            else:
                actions.append(("deploy", None, t, ()))
        return actions

    def gain(self, action):
        """How much this action changes (my score - enemy score)."""
        _, _, target, captures = action
        return self.values[target] + 2 * sum(self.values[c] for c in captures)

    def apply(self, action, team):
        _, _, target, captures = action
        self.owner[target] = team
        self.empty_count -= 1
        self.score_diff += team * self.values[target]
        for c in captures:
            self.owner[c] = team
            self.score_diff += team * 2 * self.values[c]

    def undo(self, action, team):
        _, _, target, captures = action
        self.owner[target] = EMPTY
        self.empty_count += 1
        self.score_diff -= team * self.values[target]
        for c in captures:
            self.owner[c] = -team
            self.score_diff -= team * 2 * self.values[c]


# --------------------------------------------------------------------------
# Minimax with alpha-beta pruning
# --------------------------------------------------------------------------
def evaluate(game):
    """Utility from Alpha's point of view: Alpha score - Bravo score."""
    return game.score_diff


def minimax(game, depth, team, alpha, beta):
    """Alpha is the MAX player, Bravo is the MIN player.
    Returns (value, best_action)."""
    if depth == 0 or game.is_over():
        return evaluate(game), None

    actions = game.legal_actions(team)
    # Move ordering: try the biggest immediate gains first -> more pruning
    actions.sort(key=game.gain, reverse=True)

    best_action = None
    if team == ALPHA:
        best = float("-inf")
        for action in actions:
            game.apply(action, team)
            value, _ = minimax(game, depth - 1, BRAVO, alpha, beta)
            game.undo(action, team)
            if value > best:
                best, best_action = value, action
            alpha = max(alpha, best)
            if alpha >= beta:
                break  # Bravo will never allow this branch
    else:
        best = float("inf")
        for action in actions:
            game.apply(action, team)
            value, _ = minimax(game, depth - 1, ALPHA, alpha, beta)
            game.undo(action, team)
            if value < best:
                best, best_action = value, action
            beta = min(beta, best)
            if beta <= alpha:
                break  # Alpha will never allow this branch
    return best, best_action


# --------------------------------------------------------------------------
# Input / output
# --------------------------------------------------------------------------
def read_board(path):
    with open(path) as f:
        numbers = [int(x) for x in re.findall(r"-?\d+", f.read())]
    if len(numbers) != N_TILES:
        sys.exit(f"Error: {path} must contain {N_TILES} integers, "
                 f"found {len(numbers)}.")
    return numbers


def find_input(name):
    """Look in the current folder first, then next to this script."""
    if os.path.exists(name):
        return name
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    if os.path.exists(here):
        return here
    sys.exit(f"Error: could not find {name}")


def describe(action, team, game):
    kind, source, target, captures = action
    if kind == "deploy":
        return (f"Strategic Deployment on {tile_name(target)} "
                f"(value {game.values[target]})")
    caught = ", ".join(f"{tile_name(c)} ({game.values[c]})" for c in captures)
    return (f"Tactical Assault from {tile_name(source)} to {tile_name(target)} "
            f"(value {game.values[target]}), captured {caught}")


def board_text(game):
    """Each tile prints as its value; owned tiles get A: or B: in front."""
    lines = []
    for r in range(SIZE):
        cells = []
        for c in range(SIZE):
            i = r * SIZE + c
            tag = TEAM_TAG.get(game.owner[i])
            cells.append(f"{tag}:{game.values[i]}" if tag else str(game.values[i]))
        lines.append(",".join(cells))
    return "\n".join(lines)


def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_DEPTH

    game = Game(read_board(find_input(input_file)))
    print(f"Territory Control - minimax search depth {depth}")
    print("Board legend: A:<value> = Team Alpha, B:<value> = Team Bravo, "
          "<value> = unclaimed\n")

    team = ALPHA
    move = 1
    while not game.is_over():
        _, action = minimax(game, depth, team, float("-inf"), float("inf"))
        game.apply(action, team)

        print(f"Move {move}:")
        print(f"Minimax action for team: {TEAM_NAME[team]}")
        print(f"Action: {describe(action, team, game)}")
        print(board_text(game))
        print(f"Total score - Alpha: {game.score(ALPHA)}")
        print(f"Total score - Bravo: {game.score(BRAVO)}")
        print()

        team = -team
        move += 1

    alpha_total, bravo_total = game.score(ALPHA), game.score(BRAVO)
    if alpha_total > bravo_total:
        print("The Winner is: Team-Alpha")
    elif bravo_total > alpha_total:
        print("The Winner is: Team-Bravo")
    else:
        print("The Winner is: Tie (both teams have the same score)")


if __name__ == "__main__":
    main()
