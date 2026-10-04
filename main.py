"""Entry point for Super Star Trek."""
from game import Game

if __name__ == "__main__":
    game = Game(debug_view=False)
    game.play()
