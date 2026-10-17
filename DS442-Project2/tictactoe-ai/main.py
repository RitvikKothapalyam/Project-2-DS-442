# main.py
# ds 442 question 1 - wild tic tac toe

import pygame
import time

from tictactoe.board import Board, Symbol
from tictactoe.gui import Gui
from tictactoe.engine import Engine

MODE = "TERMINATOR"
# MODE = "2 Player"


def main():
    board = Board()

    # u are O and the computer is X
    human = Symbol.CIRCLE
    computer = Symbol.CROSS

    ai = Engine(computer, human, 9)
    gui = Gui(board, "Wild Tic Tac Toe", MODE)
    clock = pygame.time.Clock()

    running = True

    while running:
        gui.update_display()
        clock.tick(30)

        # if its the computers turn let it pick a move
        if MODE == "TERMINATOR":
            if board.turn == computer and not board.is_gameover():
                move = ai.evaluate_best_move(board)
                board.move(move)
                time.sleep(1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONUP:
                # click after the game ends to start a new one
                if board.is_gameover():
                    board.reset()
                    continue

                # dont let u click when its the computers turn
                if MODE == "TERMINATOR" and board.turn != human:
                    continue

                square = gui.get_clicked_tile(event.pos)

                if square is not None:
                    board.move(square)

    pygame.quit()


if __name__ == "__main__":
    main()
