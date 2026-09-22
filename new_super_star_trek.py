# Nuevo intento de porte de Super Star Trek de BBC BASIC a Python
import random
import math
from collections import Counter

# Usaremos OOP para la programación del juego
class Game:
    def __init__(self):
        """Reset all state to start a new game. BASIC lines 330-710."""
        self.reset()

    def reset(self):
        # --- Strings (BASIC variables ending in $) ---
        self.Z_str = " "*25                     # Z$
        self.X_str = ""                         # X$
        self.X0_str = " IS "                    # X0$

        # --- Arrays (BASIC DIM line 330) ---
        self.G = [[0]*9 for _ in range(9)]      # Galaxy
        self.Z = [[0]*9 for _ in range(9)]      # Explored/Known galaxy
        self.C = [[0]*3 for _ in range(10)]     # Course vectors
        self.K = [[0]*4 for _ in range(4)]      # Klingons in quadrant
        self.N = [0]*4
        self.D = [0]*9                          # Device damage

        # --- Scalars (BASIC lines 370-470) ---
        self.T = random.randint(20, 39) *100
        self.T0 = self.T
        self.T9 = 25 + random.randint(0, 9)
        self.D0 = 0
        self.E = self.E0 = 3000
        self.P = self.P0 = 10
        self.S9 = 200
        self.S = 0
        # NOTE: The original game strted with Bases = 2, I think it was a typo
        # I have started with 0 and let the latter self.setup_galaxy & self.fix_up_galaxy
        # set the randomized number of Bases in the galaxy.
        self.Bases = 0
        self.Klingons = 0

        # --- Enterprise's starting position (BASIC 490) ---
        self.Q1 = self.fnr(1)
        self.Q2 = self.fnr(1)
        self.S1 = self.fnr(1)
        self.S2 = self.fnr(1)

        # --- Course vectors (BASIC 530-600) ---
        # Row 9 duplicates row 1 (course "9" is same as "1")
        for i in range(1, 10):
            self.C[i][1] = self.C[i][2] = 0
        self.C[3][1] = -1
        self.C[2][1] = -1
        self.C[4][1] = -1
        self.C[4][2] = -1
        self.C[5][2] = -1
        self.C[6][2] = -1
        self.C[1][2] = 1
        self.C[2][2] = 1
        self.C[6][1] = 1
        self.C[7][1] = 1
        self.C[8][1] = 1
        self.C[8][2] = 1
        self.C[9][2] = 1

        # --- Devices start undamaged (BASIC 670) ---
        for i in range(1,9):
            self.D[i] = 0

        # --- Other Object state variables, and initializations
        self.K7 = 0

    def fnd(self, i):
        """Distance from Klingon i to Enterprise.
        BASIC: DEFFND(D) = SQR((K(I,1)-S1)^2 + (K(I,2)-S2)^2)
        Note: BASIC used a global I; we pass it explicitly — a deliberate fix.
        """
        return math.sqrt((self.K[i][1] - self.S1) ** 2 +
                         (self.K[i][2] - self.S2) ** 2)

    def fnr(self, _=1):
        """Random integer 1..8. BASIC: FNR(R) = INT(RND(R)*7.98 + 1.01).
        The BASIC argument is essentially ignored; we keep the param for fidelity.
        """
        return random.randint(1, 8)

    def setup_galaxy(self):
        """Populate G and Z from BASIC 810-1160."""
        # SETUP WHAT EXISTS IN GALAXY…
        for i in range(1,9):
            for j in range(1,9):
                self.Z[i][j] = 0             # Not Known quadrant
                ods = random.random()
                local_klingons = 0
                if ods > .98:
                    local_klingons = 3
                elif ods > .95:
                    local_klingons = 2
                elif ods > .8:
                    local_klingons = 1
                self.Klingons += local_klingons

                local_bases = 1 if random.random() > .96 else 0
                self.Bases += local_bases

                self.G[i][j] = local_klingons * 100 + local_bases * 10 + self.fnr(1)

    def fix_up_galaxy(self):
        """Ensure at least one starbase and enough time. BASIC 1100-1160."""

        # At least 1 Base should exist...
        if not self.Bases:
            if self.G[self.Q1][self.Q2] < 200:
    # NOTE: The original BASIC adds +120 here, which is a transcription bug:
    # it adds 1 Klingon (hundreds) and 2 bases (tens) to this quadrant.
    # Combined with the +10 below, the final quadrant has 3 bases but the
    # global counter says 1. This is how the original has always behaved.
    # I will use the "obviously intended" behaviour, so I use +100 instead.
                # self.G[self.Q1][self.Q2] += 120
                self.G[self.Q1][self.Q2] += 100
                self.Klingons += 1
            self.Bases = 1
            self.G[self.Q1][self.Q2] += 10
            # Set another random starting Quadrant for Entreprise
            self.Q1 = self.fnr(1)
            self.Q2 = self.fnr(1)

        self.K7 = self.Klingons

        # Is there enought time?
        # NOTE: I have moved the `enought time` after Bases checking
        # because the number of Klingons can change (added 1) and there 
        # could not be enought time, so better do it with the final
        # Klingons count...
        # NOTE: Also, I have changed the comparison fron `>` to `>=`
        # to always allow at least one more day than Klingons.
        if self.Klingons >= self.T9:
            self.T9 = self.Klingons + 1

    def print_orders(self):
        """Show mission briefing. BASIC 1201, 1230-1280."""
        if self.Bases != 1:
            self.X_str = "S"
            self.X0_str = " ARE "

        print(f'YOUR ORDERS ARE AS FOLLOWS:')
        print(f'     DESTROY THE {self.Klingons} KLINGON WARSHIPS WHICH HAVE INVADED')
        print(f'  THE GALAXY BEFORE THEY CAN ATTACK FEDERATION HEADQUARTERS')
        print(f'  ON STARDATE {self.T0 + self.T9} THIS GIVES YOU {self.T9} DAYS. THERE{self.X0_str}')
        print(f'  {self.Bases} STARBASE{self.X_str} IN THE GALAXY FOR RESUPPLYING YOUR SHIP')
        print()

    def print_galaxy(self):
        for i in range(1,9):
            for j in range(1,9):
                print(f'{self.G[i][j]:03d} ', end="")
            print()

    def __repr__(self):
        return f'Game:\n\
\tToday: {self.T} - Start Date: {self.T0} - Total Avail. Time: {self.T9}\n\
\tQuadrant: [{self.Q1}, {self.Q2}], Sector: [{self.S1}, {self.S2}]\n\
\tKlingons: {self.Klingons} - Bases: {self.Bases}'

def check_T9_range():
    counts = dict()
    for _ in range(10_000):
        game = Game()
        if game.T9 not in counts:
            counts[game.T9] = 0
        counts[game.T9] += 1

    print(f'T9 Indices: {sorted(counts)}')
    if 35 in counts:
        print('WARNING: Index 35 appeared in T9.')
    else:
        print('T9 Indices look Ok.')

def check_T9_only():
    c = Counter(25 + random.randint(0, 9) for _ in range(10_000))
    print(f'Check T9 only (not the complete game): {c}')

def check_ramdomness():
    for _ in range(3):
        game = Game()
        print(game)

def check_galaxy_generation():
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

        assert game.T9 >= (game.Klingons + 1)

        k.append(klingons_count)
        b.append(bases_count)
        t9.append(game.T9)

    # Average checks:
    print(f'...Galaxy Averages:   Klingons: {sum(k)/1000:.3f} - Bases: {sum(b)/1000:.3f}')
    print(f'...Quadrant Averages: Klingons: {sum(k)/1000/64:.3f} - Bases: {sum(b)/1000/64:.3f}')
    print(f'...T9 Average: {sum(t9)/1000:.2f}')

if __name__ == "__main__":
    # DEBUG_MODE = {"play", "check_random", "check_T9", "check_galaxy_generation", "print_galaxy"}
    DEBUG_MODE = ["check_galaxy_generation", "print_galaxy"]

    if "check_random" in DEBUG_MODE:
        check_ramdomness()

    if "check_T9" in DEBUG_MODE:
        check_T9_range()
        check_T9_only()

    if "check_galaxy_generation" in DEBUG_MODE:
        check_galaxy_generation()

    if "play" in DEBUG_MODE:
        game = Game()
        game.reset()
        game.setup_galaxy()
        game.fix_up_galaxy()
        game.print_orders()
        print(game)

    if "print_galaxy" in DEBUG_MODE:
        game = Game()
        game.reset()
        game.setup_galaxy()
        game.fix_up_galaxy()
        game.print_galaxy()