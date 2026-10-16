from tictactoe.board import Board
import random

Square = int
Score = int


class Engine:
    """Minimax + alpha-beta player for WILD tic-tac-toe.

    The search itself is the same as classic tic-tac-toe; what changes is
    *when the game ends and who wins*, which comes from Board.winner()
    (wild rules live in board.py). Because of the last-chance rule the
    search must keep going after someone makes a line, so the game is only
    over when Board.is_gameover() says so.
    """

    WIN_SCORE = 100

    def __init__(self, ai, foe, level: int):
        self.ai = ai
        self.foe = foe
        self.level = level

    def minimax(self, board: Board, ai_turn: bool, depth: int, alpha: float,
                beta: float) -> tuple:
        if board.is_gameover() or depth >= self.level:
            return self.evaluate_board(board, depth), None

        available_moves = board.empty_squares
        if len(available_moves) == board.size**2 and board.size == 3:
            # Empty board: in wild tic-tac-toe the opening matters. Solving
            # the full game shows the CENTER is the best first move under
            # both rule sets (it forces a win with LAST_CHANCE, and it is
            # the only opening that doesn't lose with MISERE), so play it
            # instead of spending time searching the whole tree.
            return 0, 4

        # Try moves in random order so the AI doesn't always play the same
        # game when several moves are equally good
        random.shuffle(available_moves)

        if ai_turn:
            max_eval = float('-inf')
            best_move = None
            for move in available_moves:
                board.push(move, self.ai)
                eval_ = self.minimax(board, False, depth + 1, alpha, beta)[0]
                board.undo(move)
                if eval_ > max_eval:
                    max_eval, best_move = eval_, move
                alpha = max(alpha, max_eval)
                if alpha >= beta:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for move in available_moves:
                board.push(move, self.foe)
                eval_ = self.minimax(board, True, depth + 1, alpha, beta)[0]
                board.undo(move)
                if eval_ < min_eval:
                    min_eval, best_move = eval_, move
                beta = min(beta, min_eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def evaluate_board(self, board: Board, depth: int) -> Score:
        """Win = big positive, loss = big negative, draw/unknown = 0.
        Depth is used so the AI prefers FASTER wins and SLOWER losses."""
        winner = board.winner()
        if winner == self.ai:
            return self.WIN_SCORE - depth
        elif winner == self.foe:
            return -self.WIN_SCORE + depth
        return 0

    def evaluate_best_move(self, board: Board) -> Square:
        best_move = self.minimax(board, True, 0, float('-inf'),
                                 float('inf'))[1]
        return best_move
