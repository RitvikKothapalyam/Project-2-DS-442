import pygame
import time

from tictactoe.board import Board, Symbol
from tictactoe.gui import Gui
from tictactoe.engine import Engine

MODE = "TERMINATOR"
# MODE = "2 Player"


def main():
    board = Board()

    human = Symbol.CIRCLE
    computer = Symbol.CROSS

    ai = Engine(computer, human, 9)
    gui = Gui(board, "Wild Tic Tac Toe", MODE)
    clock = pygame.time.Clock()

    running = True

    while running:
        gui.update_display()
        clock.tick(30)

        # Let the AI move on its turn.
        if MODE == "TERMINATOR":
            if board.turn == computer and not board.is_gameover():
                move = ai.evaluate_best_move(board)
                board.move(move)
                time.sleep(1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONUP:
                # Clicking after a finished game starts another game.
                if board.is_gameover():
                    board.reset()
                    continue

                # In AI mode, only accept clicks on the human's turn.
                if MODE == "TERMINATOR" and board.turn != human:
                    continue

                square = gui.get_clicked_tile(event.pos)

                if square is not None:
                    board.move(square)

    pygame.quit()


if __name__ == "__main__":
    main()