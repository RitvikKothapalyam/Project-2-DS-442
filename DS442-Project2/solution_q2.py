# solution_q2.py
# ds 442 question 2 - computer that plays the territory game

import os
import re
import sys


# board is 6x6 and each team gets a number
SIZE = 6
N_TILES = SIZE * SIZE
EMPTY, ALPHA, BRAVO = 0, 1, -1

TEAM_NAME = {ALPHA: "Team-Alpha", BRAVO: "Team-Bravo"}
TEAM_TAG = {ALPHA: "A", BRAVO: "B"}

DEFAULT_DEPTH = 4


# for each tile get the tiles next to it (up down left right no diagonals)
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
    # turns tile number into a name like C3
    row, col = divmod(index, SIZE)
    return f"{chr(ord('A') + col)}{row + 1}"


class Game:
    # 0 = nobody has it, 1 = alpha has it, -1 = bravo has it

    def __init__(self, values):
        self.values = values
        self.owner = [EMPTY] * N_TILES
        self.empty_count = N_TILES

        # how much alpha is winning by
        self.score_diff = 0

    def is_over(self):
        # games over when theres no empty tiles
        return self.empty_count == 0

    def score(self, team):
        # add up all the points for this team
        return sum(
            v for v, o in zip(self.values, self.owner)
            if o == team
        )

    def legal_actions(self, team):
        # get every move the team can do rn
        actions = []

        for t in range(N_TILES):
            if self.owner[t] != EMPTY:
                continue

            source = None
            captures = []

            # check the tiles next to it to see whos there
            for n in NEIGHBORS[t]:
                if self.owner[n] == team and source is None:
                    source = n
                elif self.owner[n] == -team:
                    captures.append(n)

            # if we can attack and take there tiles we gotta do it, if not just place it
            if source is not None and captures:
                actions.append(("assault", source, t, tuple(captures)))
            else:
                actions.append(("deploy", None, t, ()))

        return actions

    def gain(self, action):
        # kinda guess how good a move is (taking a tile counts double cuz they lose it to)
        _, _, target, captures = action

        return self.values[target] + 2 * sum(
            self.values[c] for c in captures
        )

    def apply(self, action, team):
        _, _, target, captures = action

        # put our team on the tile
        self.owner[target] = team
        self.empty_count -= 1
        self.score_diff += team * self.values[target]

        # take the enemy tiles next to it and update score
        for c in captures:
            self.owner[c] = team
            self.score_diff += team * 2 * self.values[c]

    def undo(self, action, team):
        _, _, target, captures = action

        # make the tile empty again
        self.owner[target] = EMPTY
        self.empty_count += 1
        self.score_diff -= team * self.values[target]

        # give the tiles back to the other team
        for c in captures:
            self.owner[c] = -team
            self.score_diff -= team * 2 * self.values[c]


def evaluate(game):
    # big number good for alpha, small number good for bravo
    return game.score_diff


def minimax(game, depth, team, alpha, beta):
    # stop if we looked far enough or board is full
    if depth == 0 or game.is_over():
        return evaluate(game), None

    actions = game.legal_actions(team)

    # try the moves that get the most points first
    actions.sort(key=game.gain, reverse=True)

    best_action = None

    if team == ALPHA:
        # alpha wants the number to be big as possible
        best = float("-inf")

        for action in actions:
            # try the move, see what the other team does, then undo it
            game.apply(action, team)
            value, _ = minimax(game, depth - 1, BRAVO, alpha, beta)
            game.undo(action, team)

            if value > best:
                best, best_action = value, action

            alpha = max(alpha, best)

            # stop early cuz the other team wouldnt let this happen anyways
            if alpha >= beta:
                break

    else:
        # bravo wants the number to be small as possible
        best = float("inf")

        for action in actions:
            # try the move, see what the other team does, then undo it
            game.apply(action, team)
            value, _ = minimax(game, depth - 1, ALPHA, alpha, beta)
            game.undo(action, team)

            if value < best:
                best, best_action = value, action

            beta = min(beta, best)

            # stop early cuz the other team wouldnt let this happen anyways
            if beta <= alpha:
                break

    return best, best_action


def read_board(path):
    # read the numbers from the file
    with open(path) as f:
        numbers = [int(x) for x in re.findall(r"-?\d+", f.read())]

    # make sure theres 36 numbers
    if len(numbers) != N_TILES:
        sys.exit(
            f"Error: {path} must contain {N_TILES} integers, "
            f"found {len(numbers)}."
        )

    return numbers


def find_input(name):
    # look for the file in the folder were in
    if os.path.exists(name):
        return name

    # if its not there look where this code is
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)

    if os.path.exists(here):
        return here

    sys.exit(f"Error: could not find {name}")


def describe(action, team, game):
    kind, source, target, captures = action

    # say what tile got picked
    if kind == "deploy":
        return (
            f"Strategic Deployment on {tile_name(target)} "
            f"(value {game.values[target]})"
        )

    # say where the attack came from and went to and what got took
    caught = ", ".join(
        f"{tile_name(c)} ({game.values[c]})"
        for c in captures
    )

    return (
        f"Tactical Assault from {tile_name(source)} to {tile_name(target)} "
        f"(value {game.values[target]}), captured {caught}"
    )


def board_text(game):
    # put A: or B: in front if a team owns the tile
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
    # use input.txt and look 4 moves ahead unless u say different
    input_file = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_DEPTH

    game = Game(read_board(find_input(input_file)))

    print(f"Territory Control - minimax search depth {depth}")
    print(
        "Board legend: A:<value> = Team Alpha, B:<value> = Team Bravo, "
        "<value> = unclaimed\n"
    )

    # alpha goes first
    team = ALPHA
    move = 1

    while not game.is_over():
        # computer picks the best move and does it
        _, action = minimax(game, depth, team, float("-inf"), float("inf"))
        game.apply(action, team)

        # print the move and board and scores
        print(f"Move {move}:")
        print(f"Minimax action for team: {TEAM_NAME[team]}")
        print(f"Action: {describe(action, team, game)}")
        print(board_text(game))
        print(f"Total score - Alpha: {game.score(ALPHA)}")
        print(f"Total score - Bravo: {game.score(BRAVO)}")
        print()

        # other teams turn now
        team = -team
        move += 1

    # see who got more points
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
