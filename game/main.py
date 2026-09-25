"""Module entry redirect — delegates to the main Game class."""
from game.core.game import Game

def run():
    game = Game()
    game.run()

if __name__ == "__main__":
    run()