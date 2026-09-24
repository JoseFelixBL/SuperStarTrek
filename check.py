
def check_T9_range():
    """Test the T9 range of the game with all the set ups & fixes"""
    counts = dict()
    for _ in range(10_000):
        game = Game()
        game.setup_galaxy()
        game.fix_up_galaxy()
        if game.T9 not in counts:
            counts[game.T9] = 0
        counts[game.T9] += 1

    print(f'T9 Indices: {sorted(counts)}')
    if 35 in counts:
        print('WARNING: Index 35 appeared in T9.')
    else:
        print('T9 Indices look Ok.')


def check_T9_only():
    """Test random T9 generation to check boundaries"""
    number_of_days_distribution = Counter(25 + random.randint(0, 9) for _ in range(10_000))
    print(f'Check T9 only (not the complete game): {number_of_days_distribution}')


def check_randomness():
    """Test Initial game randomness"""
    for _ in range(3):
        game = Game()
        print(game)


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
        assert klingons_count == game.Klingons

        assert game.Bases >= 1

        bases_count = sum([((game.G[i][j] // 10) % 10) for i in range(1, 9) for j in range(1, 9)] )
        assert bases_count == game.Bases

        # According to MY current design choice of using `>=` 
        # comparison in fix_up_galaxy
        assert game.T9 >= (game.Klingons + 1)

        k.append(klingons_count)
        b.append(bases_count)
        t9.append(game.T9)

    # Average checks:
    print(f'...Galaxy Averages:   Klingons: {sum(k)/1000:.3f} - Bases: {sum(b)/1000:.3f}')
    print(f'...Quadrant Averages: Klingons: {sum(k)/1000/64:.3f} - Bases: {sum(b)/1000/64:.3f}')
    print(f'...T9 Average: {sum(t9)/1000:.2f}')


def check_region_names():
    """Test the Quadrant names and numbers"""
    game = Game()
    assert game.region_name(1, 1) == "ANTARES I"
    assert game.region_name(1, 1, region_only=True) == "ANTARES"
    assert game.region_name(8, 8) == "SPICA IV" 