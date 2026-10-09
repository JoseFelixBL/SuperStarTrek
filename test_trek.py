"""Sanity checks and invariants for the Super Star Trek port."""

import random
from collections import Counter

from game import Game

def check_total_avail_time_range():
    """Test the total_avail_time range of the game with all the set ups & fixes"""
    counts = dict()
    for _ in range(10_000):
        game = Game()
        game.setup_galaxy()
        game.fix_up_galaxy()
        if game.total_avail_time not in counts:
            counts[game.total_avail_time] = 0
        counts[game.total_avail_time] += 1

    print(f'total_avail_time Indices: {sorted(counts)}')
    if 35 in counts:
        print('WARNING: Index 35 appeared in total_avail_time.')
    else:
        print('total_avail_time Indices look Ok.')


def check_total_avail_time_only():
    """Test random total_avail_time generation to check boundaries"""
    number_of_days_distribution = Counter(25 + random.randint(0, 9) for _ in range(10_000))
    print(f'Check total_avail_time only (not the complete game): {number_of_days_distribution}')


def check_randomness():
    """Test Initial game randomness"""
    for _ in range(3):
        game = Game()
        game.setup_galaxy()
        print(game)
        if game.bases == 0:
            game.fix_up_galaxy()
            print(f'{" -+- " * 5}Bases Fixed!{" -+- " * 5}')
            print(game)
            print(f'{" -+- " * 5}Bases Fixed!{" -+- " * 5}')


def check_galaxy_generation():
    """Test invariants & averages"""
    game = Game()
    k = []
    b = []
    t9 = []
    for _ in range(1_000):
        game.reset()
        game.setup_galaxy()
        game.fix_up_galaxy()

        # Invariants check:
        klingons_count =  sum([game.G[i][j] // 100 for i in range(1, 9) for j in range(1, 9)] )
        assert klingons_count == game.klingons

        assert game.bases >= 1

        bases_count = sum([((game.G[i][j] // 10) % 10) for i in range(1, 9) for j in range(1, 9)] )
        assert bases_count == game.bases

        # According to MY current design choice of using `>=` 
        # comparison in fix_up_galaxy
        assert game.total_avail_time >= (game.klingons + 1)

        k.append(klingons_count)
        b.append(bases_count)
        t9.append(game.total_avail_time)

    # Average checks:
    print(f'...Galaxy Averages:   Klingons: {sum(k)/1000:.3f} - Bases: {sum(b)/1000:.3f}')
    print(f'...Quadrant Averages: Klingons: {sum(k)/1000/64:.3f} - Bases: {sum(b)/1000/64:.3f}')
    print(f'...total_avail_time Average: {sum(t9)/1000:.2f}')


def check_region_names():
    """Test the Quadrant names and numbers"""
    game = Game()
    assert game.region_name(1, 1) == "ANTARES I"
    assert game.region_name(1, 1, region_only=True) == "ANTARES"
    assert game.region_name(8, 8) == "SPICA IV" 



if __name__ == "__main__":
    print('Running all test')
    check_randomness()
    check_total_avail_time_range()
    check_total_avail_time_only()
    check_galaxy_generation()
    print('All tests passed')
