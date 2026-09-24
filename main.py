#
# Nuevo intento de porte de Super Star Trek de BBC BASIC a Python.
# Intentaré mantener en lo posible la estructura y las variables del 
# original, MENOS en los casos en los que Python ofrezca una alternativa
# más sencilla de usar y comprender.
#
import random
import math
from collections import Counter

# We will use OOP as it gives us the advantage of accessing context variables
# without the need to mark them as Globals or sending long structs or
# prameter lists between functions.

def basic_range(start, end):
    """Helper function to aid with BASIC ranges"""
    return range(start, end + 1)


if __name__ == "__main__":
    # DEBUG_MODE = {"play", 
    #               "check_random", 
    #               "check_T9", 
    #               "check_galaxy_generation", 
    #               "print_galaxy", 
    #               "check_region_names"}
    DEBUG_MODE = {"play"}

    if "check_random" in DEBUG_MODE:
        check_randomness()

    if "check_T9" in DEBUG_MODE:
        check_T9_range()
        check_T9_only()

    if "check_galaxy_generation" in DEBUG_MODE:
        check_galaxy_generation()

    if "play" in DEBUG_MODE:
        game = Game()
        game.play()

    if "print_galaxy" in DEBUG_MODE:
        game = Game()
        game.reset()
        game.setup_galaxy()
        game.fix_up_galaxy()
        game.debug_print_galaxy()

    if "check_region_names" in DEBUG_MODE:
        check_region_names()