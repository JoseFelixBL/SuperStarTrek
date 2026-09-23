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
        # NOTE: The original BASIC sets Bases = 2 initially, which seems to be a
        # leftover from an older version of the game. The galaxy always starts
        # empty and bases are only added by setup_galaxy, so Bases should count
        # actual bases. We start at 0 and let setup_galaxy + fix_up_galaxy
        # populate it.
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
        self.Q_str = ""         # Quadrant I am in now

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
        """Populate G and Z from BASIC 810-1040."""
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

            # Set another random starting Quadrant for Enterprise
            self.Q1 = self.fnr(1)
            self.Q2 = self.fnr(1)

        self.K7 = self.Klingons

        # Is there enough time?
        # NOTE: I have moved the `enough time` after Bases checking
        # because the number of Klingons can change (added 1) and there 
        # could not be enough time, so better do it with the final
        # Klingons count...
        # NOTE: Also, I have changed the comparison from `>` to `>=`
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

    def __print_galaxy__(self):
        """Quick print of the Klingons-Bases-Stars distribution"""
        for i in range(1,9):
            for j in range(1,9):
                print(f'{self.G[i][j]:03d} ', end="")
            print()

    def __print_quadrant__(self):
        """Quick print of actual quadrant to check"""
        for i in range(1,9):
            for j in range(1,9):
                print(f'{self.Q_str[i][j]}', end="")
            print()

    def enter_quadrant(self):
        """1300 - 1600
        Now entering X Quadrant
        Return local_klingons, local_bases, local_stars
        """

        # 1300
        I = random.random()
        local_klingons = 0
        local_bases = 0
        local_stars = 0
        G5 = 0
        D4 = .5 * random.random()
        self.Z[self.Q1][self.Q2] = self.G[self.Q1][self.Q2]

        # 1390
        # When can this condition happen? Out of range indices? What does it mean?
        if not (self.Q1 < 1 or self.Q1 > 8 or self.Q2 < 1 or self.Q2 > 8):

            # 1430
            g2_quadrant_name = self.region_name(self.Q1, self.Q2)
            print()
            if self.T0 != self.T:
                print(f'NOW ENTERING {g2_quadrant_name} QUADRANT . . .')
            else:
                print(f'YOUR MISSION BEGINS WITH YOUR STARSHIP LOCATED')
                print(F'IN THE GALACTIC QUADRANT {g2_quadrant_name}.')

            # 1500
            print()
            local_klingons = self.G[self.Q1][self.Q2] // 100
            local_bases = self.G[self.Q1][self.Q2] // 10 % 10
            local_stars = self.G[self.Q1][self.Q2] % 10

            if local_klingons:
                print(f'COMBAT AREA      CONDITION RED')
                if self.S <= 200:
                    print('   SHIELDS DANGEROUSLY LOW')
                for i in range(1,3):
                    self.K[i][1] = 0
                    self.K[i][2] = 0

            # 1600
            if self.Q1 < 1 or self.Q1 > 8 or self.Q2 < 1 or self.Q2 > 8:
                for i in range(1,3):
                    self.K[i][3] = 0

        for i in range(1,3):
            self.K[i][3] = 0

        # Q$ = Z$+Z$+Z$+Z$+Z$+Z$+Z$+LEFT$(Z$,17)  
        # self.Q_str = self.Z_str * 7 + self.Z_str[:17]
        self.Q_str = [["   "] * 9 for _ in range(9)]
        
        return local_klingons, local_bases, local_stars

    def setup_quadrant(self, local_klingons, local_bases, local_stars):
        """1660 - 1910
        Place objects, local_klingons, local_bases, local_stars,
        in sector grid"""
        # Position Enterprise in Quadrant, then place all the Klingons, 
        # the Bases, and the Stars elsewhere.
        
        # Enterprise:
        A_str = "<*>"
        Z1 = self.S1
        Z2 = self.S2

        # Gosub 8670
        self.insert_in_quadrant_string(A_str, Z1, Z2)

        # Klingons:
        if local_klingons:
            for i in range(1, local_klingons + 1):

                # Gosub 8590 - find_empty_place_in_quadrant():
                R1, R2 = self.find_empty_place_in_quadrant()

                A_str = "+K+"
                Z1 = R1
                Z2 = R2

                # Gosub 8670
                self.insert_in_quadrant_string(A_str, Z1, Z2)

                self.K[i][1] = R1
                self.K[i][2] = R2
                self.K[i][3] = self.S9 * (0.5 + random.random())

        # Bases:
        if local_bases:
            for i in range(1, local_bases + 1):

                # Gosub 8590 - find_empty_place_in_quadrant():
                R1, R2 = self.find_empty_place_in_quadrant()

                A_str = ">!<"
                Z1 = R1
                B4 = R1
                Z2 = R2
                B5 = R2

                # Gosub 8670
                self.insert_in_quadrant_string(A_str, Z1, Z2)

        # Stars:
        if local_stars:
            for i in range(1, local_stars):

                # Gosub 8590 - find_empty_place_in_quadrant():
                R1, R2 = self.find_empty_place_in_quadrant()

                A_str = " * "
                Z1 = R1
                Z2 = R2

                # Gosub 8670
                self.insert_in_quadrant_string(A_str, Z1, Z2)

        # Gosub 6430 - srs_scan_and_startup()

    def insert_in_quadrant_string(self, a_str, z1, z2):
        """
        BASIC: 8670
        INSERT IN STRING ARRAY FOR QUADRANT
        """
        # s8 = int(z2 - .5) * 3 + int(z1 - .5) * 24 + 1
        # if len(a_str) != 3:
            # print('ERROR')
            # quit()

        # if s8 == 1:
            # return a_str + self.Q_str[-189:]

        # if s8 == 190:
            # return self.Q_str[:189] + a_str

        # self.Q_str[:s8 - 1] + a_str + self.Q_str[-(190 - s8):]
        self.Q_str[z1][z2] = a_str

    def find_empty_place_in_quadrant(self):
        """8590
        FIND EMPTY PLACE IN QUADRANT (FOR THINGS)
        Return tuple(r1, r2) = sector's empty space coordinates
        """
        r1 = r2 = 0
        found = False
        A_str = "   "
        while not found:
            r1 = self.fnr(1)
            r2 = self.fnr(1)
            Z1 = r1
            Z2 = r2

            # Gosub 8830 - string_comparison_in_quadrant_array()
            found = self.string_comparison_in_quadrant_array(A_str, Z1, Z2)
        return (r1, r2)


    def string_comparison_in_quadrant_array(self, a_str, z1, z2):
        """8830
        Return True if z1, z2 coordinates are the same as a_str
        else return False
        """
        # z1 = int(z1 + .5)
        # z2 = int(z2 + .5)
        # s8 = (z2 - 1) *3 + (z1 - 1) * 24 + 1
        
        # return self.Q_str[s8-1:s8 + 3] == a_str
        return self.Q_str[z1][z2] == a_str


    def srs_scan_and_startup(self):
        """6430
        SHORT RANGE SENSOR SCAN & STARTUP SUBROUTINE"""
        for i in range(self.S1 - 2, self.S1 + 1):
            for j in range(self.S2 - 2, self.S2 + 1):
                if int(i + .5) < 1 or int(i + .5) > 8 or int(j + .5) < 1 or int(j + .5) > 8:
                    continue
                a_str = ">!<"
                Z1 = i
                Z2 = j
                # Gosub 8830
                if string_comparison_in_quadrant_array(a_str, Z1, Z2):
                    self.D0 = 1
                    C_str = "DOCKED"
                    E = self.E0
                    P = self.P0
                    print('SHIELDS DROPPED FOR DOCKING PURPOSES')
                    S = 0
                    self.D0 = 0
                    if self.D[2] < 0:
                        print()
                        print('*** SHORT RANGE SENSORS ARE OUT ***')
                        print()
                        return
                    O1_str = '-' * 33
                    print(O1_str)

                    break
        else:
            self.D0 = 0
            if local_klingons:
                C_str = "RED"
                # Repensar cómo dividir esto en subrutinas !!!!!!!!!!!!!!!!!!!
                # Hacerlo escribiendo
            


    def srs_display(self):
        """6430 - 7260
        Short Range Sensor Scan - Draw Sector + status panel"""
        pass

    def docked_check(self):
        """6430 - 6620
        Docking check"""
        pass

    def region_name(self, z4, z5, region_only=False):
        """Return the region name for quadrant (z4, z5)
        BASIC: 9010 - 9300
        z4: Q1
        z5: Q2
        region_only: Bool, formerly g5: == 1, return region name only!
        RETURN a region name, plus region number, optionally no region number
        EXAMPLES:
        region_name(1, 1) -> "ANTARES I"
        region_name(1, 1, True) -> "ANTARES"
        region_name(1, 5) -> "ANTARES I"    (because 5 % 4 == 1)
        region_name(8, 8) -> "SPICA IV"
        """

        g2 = ""
        if z5 <= 4:
            match z4:
                case 1:
                    g2 = "ANTARES"
                case 2:
                    g2 = "RIGEL"
                case 3:
                    g2 = "PROCYON"
                case 4:
                    g2 = "VEGA"
                case 5:
                    g2 = "CANOPUS"
                case 6:
                    g2 = "ALTAIR"
                case 7:
                    g2 = "SAGITTARIUS"
                case 8:
                    g2 = "POLLUX"
        else:
            match z4:
                case 1:
                    g2 = "SIRIUS"
                case 2:
                    g2 = "DENEB"
                case 3:
                    g2 = "CAPELLA"
                case 4:
                    g2 = "BETELGEUSE"
                case 5:
                    g2 = "ALDEBARAN"
                case 6:
                    g2 = "REGULUS"
                case 7:
                    g2 = "ARCTURUS"
                case 8:
                    g2 = "SPICA"

        if region_only:
            return g2

        match z5:
            case 1|5:
                g2 += " I"
            case 2|6:
                g2 += " II"
            case 3|7:
                g2 += " III"
            case 4|8:
                g2 += " IV"
        return g2


    def __repr__(self):
        return f'Game:\n\
\tToday: {self.T} - Start Date: {self.T0} - Total Avail. Time: {self.T9}\n\
\tQuadrant: [{self.Q1}, {self.Q2}], Sector: [{self.S1}, {self.S2}]\n\
\tKlingons: {self.Klingons} - Bases: {self.Bases}'

    def play(self):
        """Play the game"""
        self.setup_galaxy()
        self.fix_up_galaxy()
        self.print_orders()
        klingons, bases, stars = self.enter_quadrant()
        self.setup_quadrant(klingons, bases, stars )
        self.__print_quadrant__()



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
    c = Counter(25 + random.randint(0, 9) for _ in range(10_000))
    print(f'Check T9 only (not the complete game): {c}')

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
    for i in range(1,9):
        for j in range(1,9):
            print(f'{i},{j}: {game.region_name(i, j)}')

if __name__ == "__main__":
    # DEBUG_MODE = {"play", 
    #               "check_random", 
    #               "check_T9", 
    #               "check_galaxy_generation", 
    #               "print_galaxy", 
    #               "check_region_names"}
    DEBUG_MODE = {"check_galaxy_generation", "print_galaxy"}
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
        game.print_galaxy()

    if "check_region_names" in DEBUG_MODE:
        check_region_names()