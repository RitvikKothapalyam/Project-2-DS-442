from tictactoe.board import Board
import random


# minimax with alpha beta for wild tic tac toe
# the search is basically the same as normal tic tac toe, the only thing
# thats different is who wins and when the game ends (thats all in board.py)
# we cant stop when someone makes 3 in a row cuz the other player still
# gets there last move, so we just keep going till is_gameover() says its over
class Engine:

    WIN_SCORE = 100

    def __init__(self, ai, foe, level):
        self.ai = ai
        self.foe = foe
        self.level = level

    def minimax(self, board, ai_turn, depth, alpha, beta):
        if board.is_gameover() or depth >= self.level:
            return self.evaluate_board(board, depth), None

        moves = board.empty_squares

        # if the board is empty just go middle. we checked every game and
        # middle is the best first move for both rules so no point searching
        if len(moves) == 9:
            return 0, 4

        # mix up the moves so the ai doesnt play the same game every time
        random.shuffle(moves)

        if ai_turn:
            # ai wants the biggest score
            best = -1000
            best_move = None
            for move in moves:
                board.push(move, self.ai)
                score = self.minimax(board, False, depth + 1, alpha, beta)[0]
                board.undo(move)
                if score > best:
                    best = score
                    best_move = move
                alpha = max(alpha, best)
                if alpha >= beta:
                    break  # other player wont let this happen so stop
            return best, best_move
        else:
            # other player wants the smallest score
            best = 1000
            best_move = None
            for move in moves:
                board.push(move, self.foe)
                score = self.minimax(board, True, depth + 1, alpha, beta)[0]
                board.undo(move)
                if score < best:
                    best = score
                    best_move = move
                beta = min(beta, best)
                if beta <= alpha:
                    break  # same thing here
            return best, best_move

    def evaluate_board(self, board, depth):
        # win = big number, lose = negative, tie or not done = 0
        # depth makes it win faster and lose slower if it has to lose
        winner = board.winner()
        if winner == self.ai:
            return self.WIN_SCORE - depth
        elif winner == self.foe:
            return -self.WIN_SCORE + depth
        return 0

    def evaluate_best_move(self, board):
        # start the search and give back the move it picked
        return self.minimax(board, True, 0, -1000, 1000)[1]
