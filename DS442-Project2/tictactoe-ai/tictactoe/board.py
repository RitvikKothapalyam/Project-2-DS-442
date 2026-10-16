from typing import Optional
from enum import Enum

Square = int

# ---------------------------------------------------------------------------
# WILD TIC-TAC-TOE RULES (DS/CMPSC 442 Project 2, Q1.1)
#
# "LAST_CHANCE" (default): when a player makes three in a row, the opponent
#     gets ONE more move. If that move makes three in a row for the opponent,
#     the opponent wins. Otherwise the player who made the first line wins.
# "MISERE": making three in a row loses immediately (the "doing so results
#     in a loss" reading of the handout).
# ---------------------------------------------------------------------------
RULES = "LAST_CHANCE"


class Symbol(Enum):
    CIRCLE = "O"
    CROSS = "X"
    EMPTY = "#"


def opponent(symbol: "Symbol") -> "Symbol":
    return Symbol.CROSS if symbol == Symbol.CIRCLE else Symbol.CIRCLE


class Board:
    """Responsible for storing current state, making and validating moves, and updating the game

    Attributes:
        first_move (Symbol): Symbol to make the first move, alternate after every match
        p1_score (int): First player's score
        p2_score (int): Second player's score
        size (int): Board dimension     
        squares (dict[[int,int],Square]): Container to convert row,col into Square
        table (list[Symbol]): Container to store the current board state, use Square as index 
        turn (Symbol): Current turn to make a move
        win_conditions (list[list[Square]]): All possible connections to win the game
    """

    def __init__(self, size: int = 3):
        """Creating a board with given size

        Args:
            size (int, optional): Board dimension
        """
        self.size: int = size
        self.p1_score: int = 0
        self.p2_score: int = 0

        self.squares: dict[[int, int], Square] = self.get_squares()
        self.table: list[Symbol] = self.get_table()
        self.win_conditions: list[list[Square]] = self.get_win_conditions()
        # Lines that pass through each square (used to check only the lines
        # a new move could have completed)
        self.lines_through: dict[Square, list[list[Square]]] = {
            sq: [line for line in self.win_conditions if sq in line]
            for sq in range(self.size**2)
        }
        # Order the squares were filled in. Wild rules depend on WHO made a
        # line first and what happened on the very next move, so the board
        # has to remember move order, not just the final picture.
        self.history: list[Square] = []

        self.first_move: Symbol = Symbol.CIRCLE
        self.turn: Symbol = self.first_move

    def get_win_conditions(self) -> list[list[Square]]:
        """Get all winning connections, for all board sizes

        Returns:
            list[list[Square]]: list of rows, cols, diagonals 
        """
        rows, cols = self.get_rows_cols()
        diagonals = self.get_diagonals()
        return rows + cols + diagonals

    def get_squares(self) -> dict[[int, int], Square]:
        """Create a dictionary containing all squares

        Returns:
            dict[[int, int], Square]: (row,col) as key, square name as value
        """
        return {(r, c): r * self.size + c
                for r in range(self.size) for c in range(self.size)}

    def get_table(self) -> list[Symbol]:
        """Table to store the current board state

        Returns:
            list[Symbol]: List of tiles filled with empty Symbol
        """
        return [Symbol.EMPTY for _ in range(self.size**2)]

    def get_rows_cols(self) -> tuple[list[Square], list[Square]]:
        """Group squares into corresponding rows and columns

        Returns:
            tuple[list[Square], list[Square]]: lists of rows and cols
        """
        rows: list[list[Square]] = [[] for _ in range(self.size)]
        columns: list[list[Square]] = [[] for _ in range(self.size)]
        for index, square in self.squares.items():
            r, c = index
            rows[r].append(square)
            columns[c].append(square)
        return rows, columns

    def get_diagonals(self) -> list[list[Square]]:
        """Calculate diagonal squares for all board sizes

        Returns:
            list[list[Square]]: list of diagonals
        """
        diagonals: list[list] = [[], []]
        i = 0
        j = self.size - 1
        for _ in range(self.size):
            diagonals[0].append(i)
            diagonals[1].append(j)
            i += self.size + 1
            j += self.size - 1
        return diagonals

    @property
    def empty_squares(self) -> list[Square]:
        """Get all empty squares

        Returns:
            list[Square]: list of empty squres
        """
        return [
            square for square in self.squares.values() if self.is_empty(square)
        ]

    def reset(self):
        """Reset the board and change the turn
        """
        self.table = self.get_table()
        self.history = []
        self.first_move =Symbol.CROSS if self.first_move == Symbol.CIRCLE else Symbol.CIRCLE
        self.turn = self.first_move

    def square_pos(self, square: Square) -> Optional[tuple[int, int]]:
        """Get row, col of the square

        Args:
            square (Square): Square number

        Returns:
            Optional[tuple[int, int]]: (row, col) if square exists
        """
        for pos, sq in self.squares.items():
            if sq == square:
                return pos
        return None

    def square_name(self, row: int, col: int) -> Square:
        """Convert row, col into square

        Returns:
            Square: corresponding number
        """
        return self.squares[(row, col)]

    def square_value(self, square: Square) -> Symbol:
        """Get the symbol of the square

        Args:
            square (Square): Square name

        Returns:
            Symbol: Symbol of the square
        """
        return self.table[square]

    def is_empty(self, square: Square) -> bool:
        """Check if square is empty

        Args:
            square (Square): square name

        Returns:
            bool: True if empty symbol
        """
        return self.table[square] == Symbol.EMPTY

    def get_connection(self) -> list[Square]:
        """Check for connected tiles

        Returns:
            list[Square]: List of connected squares
        """
        for row in self.win_conditions:
            checklist = []
            for square in row:
                if self.is_empty(square):
                    continue
                checklist.append(self.square_value(square))
            if len(checklist) == self.size and len(set(checklist)) == 1:
                return row
        return []

    def is_draw(self) -> bool:
        """Check for draw

        Returns:
            bool: True if board is filled and nobody won
        """
        return len(self.empty_squares) == 0 and self.winner() is None

    def _makes_line(self, square: Square, symbol: Symbol,
                    table: list[Symbol]) -> bool:
        """True if `symbol` has three in a row through `square` on `table`"""
        return any(
            all(table[sq] == symbol for sq in line)
            for line in self.lines_through[square])

    def first_line(self) -> Optional[tuple[int, Symbol]]:
        """Replay the moves in order and find the first one that made a line

        Returns:
            Optional[tuple[int, Symbol]]: (index in history, symbol of the
            player who made the line), or None if nobody has a line yet
        """
        replay = self.get_table()
        for i, square in enumerate(self.history):
            symbol = self.table[square]
            replay[square] = symbol
            if self._makes_line(square, symbol, replay):
                return i, symbol
        return None

    def pending_line(self) -> Optional[Symbol]:
        """LAST_CHANCE rule: symbol of the player who just made a line while
        the opponent still has their one reply move left (else None)"""
        if RULES != "LAST_CHANCE":
            return None
        first = self.first_line()
        if first is None:
            return None
        index, maker = first
        if index == len(self.history) - 1 and self.empty_squares:
            return maker
        return None

    def winner(self) -> Optional[Symbol]:
        """Get the winner of the match under wild tic-tac-toe rules

        Returns:
            Optional[Symbol]: Winner's symbol, or None if no winner (yet)
        """
        first = self.first_line()
        if first is None:
            return None
        index, maker = first

        if RULES == "MISERE":
            # Making three in a row loses right away
            return opponent(maker)

        # LAST_CHANCE: the opponent gets exactly one reply move
        if index == len(self.history) - 1:
            if self.empty_squares:
                return None  # waiting for the opponent's last-chance move
            return maker  # board is full, opponent has no reply
        reply = self.history[index + 1]
        if self._makes_line(reply, opponent(maker), self.table):
            return opponent(maker)  # opponent answered with their own line
        return maker

    def is_gameover(self) -> bool:
        """Check for gameover

        Returns:
            bool: True if there's winner or draw
        """
        return self.winner() is not None or self.is_draw()

    def _update(self):
        """Update the turn and score if there's winner
        """
        self.turn = Symbol.CROSS if self.turn == Symbol.CIRCLE else Symbol.CIRCLE
        if self.winner() == Symbol.CIRCLE:
            self.p1_score += 1
        elif self.winner() == Symbol.CROSS:
            self.p2_score += 1

    def push(self, square: Square, value: Symbol):
        """Store the symbol into the square

        Args:
            square (Square): square name
            value (Symbol): symbol
        """
        self.table[square] = value
        self.history.append(square)

    def undo(self, square: Square):
        """Change the square's value to empty

        Args:
            square (Square): square name
        """
        self.table[square] = Symbol.EMPTY
        if self.history and self.history[-1] == square:
            self.history.pop()
        elif square in self.history:
            self.history.remove(square)

    def move(self, square: Square):
        """Mark the square with symbol of current turn if valid and update the board

        Args:
            square (Square): square name
        """
        if self.is_gameover():
            return
        if square >= self.size**2 or square < 0 or not self.is_empty(square):
            print("Invalid move!")
            return
        self.push(square, self.turn)
        self._update()

    def print(self):
        """Represent the board in string
        """
        turn = "Player 1" if self.turn == Symbol.CIRCLE else "Player 2"
        if self.winner():
            print("Match Over!")
            print("*" * 13)
        else:
            print("*" * 15)
            print("Turn->> ", turn)
            print('-' * (self.size * 5))
        for index, square in self.squares.items():
            r, c = index
            sign = square if self.is_empty(
                square) else "O" if self.square_value(
                    square) == Symbol.CIRCLE else "X"
            print(' |', end=' ')
            print(sign, end='')
            if c == self.size - 1:
                print(' |')
                print('-' * (self.size * 5))
        print('-' * (self.size * 5))
        print()


if __name__ == "__main__":
    # CLI game for two player mode
    board = Board()
    print("Tic Tac Toe - Duel")
    print("##################")
    board.print()
    running = True
    while running:
        turn = "Player 1" if board.turn == Symbol.CIRCLE else "Player 2"
        move = int(input(f"Enter {turn} 's move: "))
        board.move(move)
        board.print()
        if board.is_gameover():
            running = False
    if board.is_draw():
        print("Draw! What a great match!")
    else:
        print("Player 1" if board.winner() == Symbol.CIRCLE else "Player 2",
              " Wins....!")
