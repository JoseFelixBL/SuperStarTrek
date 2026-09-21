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
        self.Bases = 2
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

    def __repr__(self):
        return f'Game:\n\
\tToday: {self.T} - Start Date: {self.T0} - Total Avail. Time: {self.T9}\n\
\tQuadrant: [{self.Q1}, {self.Q2}], Sector: [{self.S1}, {self.S2}]'

def check_T9_range():
    counts = dict()
    for _ in range(10_000):
        game = Game()
        if game.T9 not in counts:
            counts[game.T9] = 0
        counts[game.T9] += 1
        del game
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

if __name__ == "__main__":
    check_ramdomness()
    check_T9_range()
    check_T9_only()