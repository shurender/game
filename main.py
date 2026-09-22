"""Risu — A Creature Collecting Adventure.

Launch the game by running this file:

    python main.py
"""
from game.core.game import Game


def main() -> None:
    """Create and run the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()