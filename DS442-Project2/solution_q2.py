# solution_q2.py
# DS 442 - Question 2: Minimax for the Territory Control Game

import os
import re
import sys


# Board size and team values
SIZE = 6
N_TILES = SIZE * SIZE
EMPTY, ALPHA, BRAVO = 0, 1, -1

TEAM_NAME = {ALPHA: "Team-Alpha", BRAVO: "Team-Bravo"}
TEAM_TAG = {ALPHA: "A", BRAVO: "B"}

DEFAULT_DEPTH = 4


# Find the neighboring tiles in each direction
NEIGHBORS = []

for _i in range(N_TILES):
    _r, _c = divmod(_i, SIZE)
    _adj = []

    for _dr, _dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        _nr = _r + _dr
        _nc = _c + _dc

        if 0 <= _nr < SIZE and 0 <= _nc < SIZE:
            _adj.append(_nr * SIZE + _nc)

    NEIGHBORS.append(tuple(_adj))


def tile_name(index):
    # Convert the position to a column letter and row number
    row, col = divmod(index, SIZE)
    return f"{chr(ord('A') + col)}{row + 1}"


class Game:
    # Owner values: 0 = empty, 1 = Alpha, -1 = Bravo

    def __init__(self, values):
        self.values = values
        self.owner = [EMPTY] * N_TILES
        self.empty_count = N_TILES

        # Store Alpha's score minus Bravo's score
        self.score_diff = 0

    def is_over(self):
        # The game ends when every tile is owned
        return self.empty_count == 0

    def score(self, team):
        # Add the values of the team's tiles
        return sum(
            v for v, o in zip(self.values, self.owner)
            if o == team
        )

    def legal_actions(self, team):
        # Action = (kind, source, target, captured tiles)
        actions = []

        for t in range(N_TILES):
            if self.owner[t] != EMPTY:
                continue

            source = None
            captures = []

            # Check for neighboring friendly and enemy tiles
            for n in NEIGHBORS[t]:
                if self.owner[n] == team and source is None:
                    source = n
                elif self.owner[n] == -team:
                    captures.append(n)

            # Choose an assault when a capture is available at this tile
            if source is not None and captures:
                actions.append(("assault", source, t, tuple(captures)))
            else:
                actions.append(("deploy", None, t, ()))

        return actions

    def gain(self, action):
        # Capturing a tile adds its value and removes it from the other team
        _, _, target, captures = action

        return self.values[target] + 2 * sum(
            self.values[c] for c in captures
        )

    def apply(self, action, team):
        _, _, target, captures = action

        # Claim the target tile
        self.owner[target] = team
        self.empty_count -= 1
        self.score_diff += team * self.values[target]

        # Convert captured tiles and update the score difference
        for c in captures:
            self.owner[c] = team
            self.score_diff += team * 2 * self.values[c]

    def undo(self, action, team):
        _, _, target, captures = action

        # Restore the target tile
        self.owner[target] = EMPTY
        self.empty_count += 1
        self.score_diff -= team * self.values[target]

        # Return captured tiles to the other team
        for c in captures:
            self.owner[c] = -team
            self.score_diff -= team * 2 * self.values[c]


def evaluate(game):
    # Positive values favor Alpha and negative values favor Bravo
    return game.score_diff


def minimax(game, depth, team, alpha, beta):
    # Stop at the depth limit or when the board is full
    if depth == 0 or game.is_over():
        return evaluate(game), None

    actions = game.legal_actions(team)

    # Check moves with larger gains first
    actions.sort(key=game.gain, reverse=True)

    best_action = None

    if team == ALPHA:
        # Alpha maximizes the score difference
        best = float("-inf")

        for action in actions:
            # Try the move and search the opponent's turn
            game.apply(action, team)
            value, _ = minimax(game, depth - 1, BRAVO, alpha, beta)
            game.undo(action, team)

            if value > best:
                best, best_action = value, action

            alpha = max(alpha, best)

            # Skip the remaining moves when this branch cannot help
            if alpha >= beta:
                break

    else:
        # Bravo minimizes the score difference
        best = float("inf")

        for action in actions:
            # Try the move and search the opponent's turn
            game.apply(action, team)
            value, _ = minimax(game, depth - 1, ALPHA, alpha, beta)
            game.undo(action, team)

            if value < best:
                best, best_action = value, action

            beta = min(beta, best)

            # Skip the remaining moves when this branch cannot help
            if beta <= alpha:
                break

    return best, best_action


def read_board(path):
    # Read the tile values from the input file
    with open(path) as f:
        numbers = [int(x) for x in re.findall(r"-?\d+", f.read())]

    # Check that all 36 values were provided
    if len(numbers) != N_TILES:
        sys.exit(
            f"Error: {path} must contain {N_TILES} integers, "
            f"found {len(numbers)}."
        )

    return numbers


def find_input(name):
    # Check the current folder for the input file
    if os.path.exists(name):
        return name

    # Otherwise check the folder containing this script
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)

    if os.path.exists(here):
        return here

    sys.exit(f"Error: could not find {name}")


def describe(action, team, game):
    kind, source, target, captures = action

    # Show the tile claimed by a deployment
    if kind == "deploy":
        return (
            f"Strategic Deployment on {tile_name(target)} "
            f"(value {game.values[target]})"
        )

    # Show the source, target, and captured tiles for an assault
    caught = ", ".join(
        f"{tile_name(c)} ({game.values[c]})"
        for c in captures
    )

    return (
        f"Tactical Assault from {tile_name(source)} to {tile_name(target)} "
        f"(value {game.values[target]}), captured {caught}"
    )


def board_text(game):
    # Show A or B before the values of owned tiles
    lines = []

    for r in range(SIZE):
        cells = []

        for c in range(SIZE):
            i = r * SIZE + c
            tag = TEAM_TAG.get(game.owner[i])

            cells.append(
                f"{tag}:{game.values[i]}" if tag
                else str(game.values[i])
            )

        lines.append(",".join(cells))

    return "\n".join(lines)


def main():
    # Use input.txt and depth 4 unless other arguments are provided
    input_file = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_DEPTH

    game = Game(read_board(find_input(input_file)))

    print(f"Territory Control - minimax search depth {depth}")
    print(
        "Board legend: A:<value> = Team Alpha, B:<value> = Team Bravo, "
        "<value> = unclaimed\n"
    )

    # Alpha moves first
    team = ALPHA
    move = 1

    while not game.is_over():
        # Run minimax and apply the selected move
        _, action = minimax(game, depth, team, float("-inf"), float("inf"))
        game.apply(action, team)

        # Print the action, board, and current scores
        print(f"Move {move}:")
        print(f"Minimax action for team: {TEAM_NAME[team]}")
        print(f"Action: {describe(action, team, game)}")
        print(board_text(game))
        print(f"Total score - Alpha: {game.score(ALPHA)}")
        print(f"Total score - Bravo: {game.score(BRAVO)}")
        print()

        # Switch teams for the next move
        team = -team
        move += 1

    # Compare the final scores
    alpha_total = game.score(ALPHA)
    bravo_total = game.score(BRAVO)

    if alpha_total > bravo_total:
        print("The Winner is: Team-Alpha")
    elif bravo_total > alpha_total:
        print("The Winner is: Team-Bravo")
    else:
        print("The Winner is: Tie (both teams have the same score)")


if __name__ == "__main__":
    main()
