import argparse

from player import HumanPlayer, RandomPlayer
from ui_game import UIGame
from ai_player import AIPlayer

# *********** LOGGER ***********
import config
logger = config.LOGGER 

if __name__ == '__main__':

    logger.info("")
    logger.info("")
    logger.info("")
    logger.info("NOUVELLE PARTIE")

    parser = argparse.ArgumentParser()
    parser.add_argument('--p1', default='player 1')
    parser.add_argument('--p2', default='player 2')
    args = parser.parse_args()

    player1 = HumanPlayer()
    player1.name = args.p1
    player2 = AIPlayer()
    player2.name = args.p2

    game = UIGame(player1, player2)
