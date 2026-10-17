from typing import Optional
from enum import Enum

Square = int

# wild tic tac toe rules (ds 442 project 2 q1)
# LAST_CHANCE = if u make 3 in a row the other player gets 1 more move,
#   if they make 3 in a row on that move they win, if not u win
# MISERE = making 3 in a row just loses right away
# the handout kinda says both so u can switch it here
RULES = "LAST_CHANCE"


class Symbol(Enum):
    CIRCLE = "O"
    CROSS = "X"
    EMPTY = "#"


def opponent(symbol):
    # gives back the other players symbol
    if symbol == Symbol.CIRCLE:
        return Symbol.CROSS
    return Symbol.CIRCLE


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
        # list of the moves in order. we need this cuz for the wild rules
        # it matters who made 3 in a row first and what the next move was
        self.history = []

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
        self.history = []  # clear the moves for the new game
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

    def makes_line(self, square, symbol, table):
        # checks if putting symbol on this square made 3 in a row
        for line in self.win_conditions:
            if square not in line:
                continue
            count = 0
            for sq in line:
                if table[sq] == symbol:
                    count += 1
            if count == self.size:
                return True
        return False

    def first_line(self):
        # go thru the moves in order on a blank board and find the first
        # move that made 3 in a row. gives back (which move, who did it)
        # or None if nobody has 3 in a row yet
        replay = self.get_table()
        for i in range(len(self.history)):
            square = self.history[i]
            symbol = self.table[square]
            replay[square] = symbol
            if self.makes_line(square, symbol, replay):
                return i, symbol
        return None

    def pending_line(self):
        # if someone just made 3 in a row and the other player still gets
        # there last move, give back who made the line. otherwise None
        # (the gui uses this to show the last chance message)
        if RULES != "LAST_CHANCE":
            return None
        first = self.first_line()
        if first is None:
            return None
        index, maker = first
        if index == len(self.history) - 1 and len(self.empty_squares) > 0:
            return maker
        return None

    def winner(self):
        # figure out who won with the wild rules, None if nobody yet
        first = self.first_line()
        if first is None:
            return None
        index, maker = first

        if RULES == "MISERE":
            # making 3 in a row = u lose
            return opponent(maker)

        # LAST_CHANCE rules
        if index == len(self.history) - 1:
            # the line was the last move so far
            if len(self.empty_squares) > 0:
                return None  # other player still gets there last move
            return maker  # board full so they cant answer, maker wins
        # check if the other players next move made 3 in a row for them
        reply = self.history[index + 1]
        if self.makes_line(reply, opponent(maker), self.table):
            return opponent(maker)
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
        self.history.append(square)  # remember the move order

    def undo(self, square: Square):
        """Change the square's value to empty

        Args:
            square (Square): square name
        """
        self.table[square] = Symbol.EMPTY
        # take it out of the move list too
        if square in self.history:
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
