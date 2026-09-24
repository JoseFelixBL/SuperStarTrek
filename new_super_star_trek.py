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

class Game:


    def __init__(self):
        self.DEBUG = True
        self.ENTERPRISE = "<*>"
        self.KLINGON = "+K+"
        self.BASE = ">!<"
        self.STAR = " * "
        # DEBUG ONLY - empty space depicted as 3 dots for easier viewing
        self.EMPTY_SPACE = "..." if self.DEBUG else "   "
        self.reset()


    def reset(self):
        """BASIC 330 - 710
        Reset all state to start a new game.
        """
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
        # empty and bases are only added by setup_galaxy(), so Bases should count
        # actual bases. We start at 0 and let setup_galaxy() + fix_up_galaxy()
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
        for i in basic_range(1, 9):
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
        for i in basic_range(1, 8):
            self.D[i] = 0

        # --- Other Object state variables, and initializations
        self.K7 = 0
        self.Q_str = [[self.EMPTY_SPACE] * 9 for _ in range(9)]    # Quadrant I am in now
        self.D4 = 0.0
        self.G5 = 0
        self.condition = "UNKNOWN"
        self.local_klingons = 0
        self.local_bases = 0
        self.local_stars = 0


    def fnd(self, i):
        """BASIC 470
        Distance from Klingon i to Enterprise.
        BASIC: DEFFND(D) = SQR((K(I,1)-S1)^2 + (K(I,2)-S2)^2)
        Note: BASIC used a global I; we pass it explicitly — a deliberate fix.
        """
        return math.sqrt((self.K[i][1] - self.S1) ** 2 +
                         (self.K[i][2] - self.S2) ** 2)


    def fnr(self, _=1):
        """BASIC 475
        Random integer 1..8. BASIC: FNR(R) = INT(RND(R)*7.98 + 1.01).
        The BASIC argument is essentially ignored; we keep the param for fidelity.
        """
        return random.randint(1, 8)


    def setup_galaxy(self):
        """BASIC 810 - 1040
        Populate G (Galaxy) and Z (Known Galaxy) with Klingons, Bases, Stars.
        """
        # SETUP WHAT EXISTS IN GALAXY…
        for i in basic_range(1, 8):
            for j in basic_range(1, 8):
                self.Z[i][j] = 0             # Not Known quadrant
                ods = random.random()
                self.local_klingons = 0
                if ods > .98:
                    self.local_klingons = 3
                elif ods > .95:
                    self.local_klingons = 2
                elif ods > .8:
                    self.local_klingons = 1
                self.Klingons += self.local_klingons

                self.local_bases = 1 if random.random() > .96 else 0
                self.Bases += self.local_bases

                # the self.fnr(1) are the Stars on each Quadrant.
                self.G[i][j] = self.local_klingons * 100 + self.local_bases * 10 + self.fnr(1)


    def fix_up_galaxy(self):
        """BASIC 1100-1160
        Ensure at least one starbase and enough time.
        """
        # At least 1 Base should exist...
        if not self.Bases:
            if self.G[self.Q1][self.Q2] < 200:
                # NOTE: The original BASIC adds +120 here, which is a transcription bug:
                # it adds 1 Klingon (hundreds) and 2 bases (tens) to this quadrant.
                # Combined with the +10 below, the final quadrant has 3 bases but the
                # global counter says 1. This is how the original has always behaved.
                # I will use the "obviously intended" behaviour, so I use +100 instead.
                # self.G[self.Q1][self.Q2] += 120
                # NOTE: We are adding 1 Klingon to that quadrant and the max number 
                # of klingons in quadrant == 3 holds because the comparisson is `< 200`.
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


    def enter_quadrant(self):
        """
        BASIC 1300 - 1600
        Now entering X Quadrant...
        """
        # 1300 - Not used... commented until found the utility of I = random.random()
        # I = random.random()
        # Also not sure if Z4 & Z5 are needed in the Python port...
        # Z4 = self.Q1
        # Z5 = self.Q2
        self.local_klingons = 0
        self.local_bases = 0
        self.local_stars = 0
        self.G5 = 0
        self.D4 = .5 * random.random()
        self.update_known_galaxy()

        # 1390
        # if not (self.Q1 < 1 or self.Q1 > 8 or self.Q2 < 1 or self.Q2 > 8):
        # if 1 <= self.Q1 <= 8 and 1 <= self.Q2 <= 8:
        # `if` not needed as Q1 and Q2 come from fnr ::> are always in range

        self.local_klingons = self.G[self.Q1][self.Q2] // 100
        self.local_bases = self.G[self.Q1][self.Q2] // 10 % 10
        self.local_stars = self.G[self.Q1][self.Q2] % 10

        self.print_quadrant_entry()
        

    def update_known_galaxy(self):
        self.Z[self.Q1][self.Q2] = self.G[self.Q1][self.Q2]


    def print_quadrant_entry(self):
        """
        BASIC 1430 - 
        Printing Info regarding the just entered Quadrant
        """
        # 1430 - Gosub 9030 Grab region name
        g2_quadrant_name = self.region_name(self.Q1, self.Q2)
        print()
        if self.T0 != self.T:
            print(f'NOW ENTERING {g2_quadrant_name} QUADRANT . . .')
        else:
            # Instructions printed at the begining of the game
            print(f'YOUR MISSION BEGINS WITH YOUR STARSHIP LOCATED')
            print(F'IN THE GALACTIC QUADRANT {g2_quadrant_name}.')

        # 1500
        print()

        if self.local_klingons:
            print(f'COMBAT AREA      CONDITION RED')
            if self.S <= 200:
                print('   SHIELDS DANGEROUSLY LOW')
        for i in basic_range(1,3):
            self.K[i][1] = 0
            self.K[i][2] = 0

        # 1600
        for i in basic_range(1,3):
            self.K[i][3] = 0

        # Python's 2D list to represent the Quadrant instead of big string...
        # Q$ = Z$+Z$+Z$+Z$+Z$+Z$+Z$+LEFT$(Z$,17)  
        # self.Q_str = self.Z_str * 7 + self.Z_str[:17]
        self.Q_str = [[self.EMPTY_SPACE] * 9 for _ in range(9)]


    def setup_quadrant(self):
        """"BASIC 1660 - 1980
        Place objects: self.local_klingons, self.local_bases, self.local_stars,
        in sector grid
        """
        # Position Enterprise in Quadrant, then place all the Klingons, 
        # the Bases, and the Stars elsewhere.
        
        # Enterprise:
        Z1 = self.S1
        Z2 = self.S2
        # Gosub 8670
        self.insert_in_quadrant(self.ENTERPRISE, Z1, Z2)

        # Klingons:
        if self.local_klingons:
            for i in basic_range(1, self.local_klingons):

                # Gosub 8590 - find_empty_place_in_quadrant():
                R1, R2 = self.find_empty_place_in_quadrant()
                Z1 = R1
                Z2 = R2

                # Gosub 8670
                self.insert_in_quadrant(self.KLINGON, Z1, Z2)

                self.K[i][1] = R1
                self.K[i][2] = R2
                self.K[i][3] = self.S9 * (0.5 + random.random())

        # Bases:
        if self.local_bases:
            for i in basic_range(1, self.local_bases):

                # Gosub 8590 - find_empty_place_in_quadrant():
                R1, R2 = self.find_empty_place_in_quadrant()
                Z1 = R1
                B4 = R1
                Z2 = R2
                B5 = R2

                # Gosub 8670
                self.insert_in_quadrant(self.BASE, Z1, Z2)

        # Stars:
        if self.local_stars:
            for i in basic_range(1, self.local_stars):

                # Gosub 8590 - find_empty_place_in_quadrant():
                R1, R2 = self.find_empty_place_in_quadrant()
                Z1 = R1
                Z2 = R2

                # Gosub 8670
                self.insert_in_quadrant(self.STAR, Z1, Z2)

        # Gosub 6430 - srs_scan_and_startup(self.local_klingons)
        self.srs_scan_and_startup()

        if self.DEBUG:
            # DEBUG ONLY - print the actual Galaxy to check the number
            # of objects vs. the ones printed
            self.debug_print_galaxy()


    def insert_in_quadrant(self, space_object, row, column):
        """
        BASIC: 8670
        INSERT IN STRING ARRAY FOR QUADRANT
        space_object: What to insert
        row: == z1 == y coordinate
        column: == z2 == x coordinate
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
        self.Q_str[row][column] = space_object


    def find_empty_place_in_quadrant(self):
        """8590
        FIND EMPTY PLACE IN QUADRANT (FOR THINGS)
        RETURN tuple(r1, r2) = sector's empty space coordinates
        """
        # NOTE: Robustness issue: this loop "might" loop forever...
        # added a max_attempts and bound the coordinates exaustively.
        r1 = r2 = 0
        max_attempts = 100
        found = False
        while max_attempts and not found:
            r1 = self.fnr(1)
            r2 = self.fnr(1)
            Z1 = r1
            Z2 = r2

            # Gosub 8830 - is_object_in_coordinates()
            found = self.is_object_in_coordinates(self.EMPTY_SPACE, Z1, Z2)
            max_attempts -= 1
        if not found:
            for r1 in basic_range(1, 8):
                for r2 in basic_range(1, 8):
                    found = self.is_object_in_coordinates(self.EMPTY_SPACE, r1, r2)
                    if found:
                        Z1 = r1
                        Z2 = r2
                        break
                if found:
                    break
            else:
                print('ERROR: No empty space in Quadrant.')
                quit()
        return (r1, r2)


    def is_object_in_coordinates(self, looking_for, row, column):
        """
        BASIC 8830
        looking_for: space objects: <*>, >!<, +K+, " * ", "   "
        RETURN True if z1, z2 coordinates content is the same as looking_for
        else return False
        """
        
        # Check if coordinates are out of bound
        if not (1 <= row <= 8 and 1 <= column <= 8):
            return False

        return self.Q_str[row][column] == looking_for


    def srs_scan_and_startup(self):
        """
        BASIC 6430 - 7260
        SHORT RANGE SENSOR SCAN & STARTUP SUBROUTINE
        """
        self.docked_check()
        self.srs_display()


    def docked_check(self):
        """6430 - 6660
        Docking check"""
        docked = False
        for i in basic_range(self.S1 - 1, self.S1 + 1):
            for j in basic_range(self.S2 - 1, self.S2 + 1):
                if not (1 <= i <= 8 and 1 <= j <= 8):
                    continue
                # Gosub 8830
                if self.is_object_in_coordinates(self.BASE, i, j):
                    docked = True
                    break
            if docked:
                break

        if docked:
            # 6580 Docked to Base
            self.D0 = 1
            self.condition = "DOCKED"
            self.E = self.E0
            self.P = self.P0
            print('SHIELDS DROPPED FOR DOCKING PURPOSES')
            self.S = 0
        else:
            self.D0 = 0
            if self.local_klingons:
                self.condition = "*RED*"
            else:
                self.condition = "GREEN"
                if self.E < self.E0 * .1:
                    self.condition = "YELLOW"


    def srs_display(self):
        """
        BASIC 6720 - 7260
        Short Range Sensor Scan - Draw Sector + status panel
        """
        # 6720 - Check if SRS is Damaged
        if self.D[2] < 0:
            # SRS Damaged! Cannot shhow Anything...
            print()
            print('*** SHORT RANGE SENSORS ARE OUT ***')
            print()
            return

        # 6770 - Print SRS info
        O1_str = '-' * 33

        # enterprise_headers & enterprise_info for easier printing in TTY
        enterprise_headers = {
            1: "        STARDATE           ",
            2: "        CONDITION          ",
            3: "        QUADRANT           ",
            4: "        SECTOR             ",
            5: "        PHOTON TORPEDOES   ",
            6: "        TOTAL ENERGY       ",
            7: "        SHIELDS            ",
            8: "        KLINGONS REMAINING "
        }

        enterprise_info = {
            1: f'{int(self.T * 10) * .1:g}',
            2: f'{self.condition}',
            3: f'{self.Q1}, {self.Q2}',
            4: f'{self.S1}, {self.S2}',
            5: f'{int(self.P)}',
            6: f'{int(self.E + self.S)}',
            7: f'{int(self.S)}',
            8: f'{int(self.Klingons)}',
        }

        # DEBUG ONLY - put a `|` to "see" the space.
        sector_sep = '|' if self.DEBUG else ' '
        print(O1_str)
        for row in basic_range(1, 8):
            for column in basic_range(1, 8):
                print(f'{sector_sep}{self.Q_str[row][column]}', end="")
            print(f'{sector_sep}{enterprise_headers[row]}{enterprise_info[row]}')
        print(O1_str)
        return


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
        NORTH = {
            1: "ANTARES", 2: "RIGEL", 3: "PROCYON", 4: "VEGA",
            5: "CANOPUS", 6: "ALTAIR", 7: "SAGITTARIUS", 8: "POLLUX"
        }
        SOUTH = {
            1: "SIRIUS", 2: "DENEB", 3: "CAPELLA", 4: "BETELGEUSE",
            5: "ALDEBARAN", 6: "REGULUS", 7: "ARCTURUS", 8: "SPICA"
        }

        name = (NORTH if z5 <= 4 else SOUTH).get(z4, "")

        if region_only:
            return name

        # REGION_NUMBER starts on index '0' because if z5  in [4, 8] z5 % 4 == 0 
        REGION_NUMBER = {0: " IV", 1: " I", 2: " II", 3: " III"}
        name += REGION_NUMBER.get(z5 % 4, "")
        return name


    def __repr__(self):
        return f'Game:\n\
\tToday: {self.T} - Start Date: {self.T0} - Total Avail. Time: {self.T9}\n\
\tQuadrant: [{self.Q1}, {self.Q2}], Sector: [{self.S1}, {self.S2}]\n\
\tKlingons: {self.Klingons} - Bases: {self.Bases}'


    def debug_print_galaxy(self):
        """Quick print of the Klingons-Bases-Stars distribution"""
        print('\n>>>>> DEBUG PRINT OF THE GALAXY <<<<<\n')
        for i in basic_range(1, 8):
            for j in basic_range(1, 8):
                print(f'{self.G[i][j]:03d} ', end="")
            print()


    def debug_print_quadrant(self):
        """Quick print of actual quadrant to check"""
        for i in basic_range(1, 8):
            for j in basic_range(1, 8):
                print(f'{self.Q_str[i][j]}', end="")
            print()


    def play(self):
        """Play the game"""
        self.setup_galaxy()
        self.fix_up_galaxy()
        self.print_orders()
        self.enter_quadrant()
        self.setup_quadrant()

        # self._print_quadrant()


def basic_range(start, end):
    return range(start, end + 1)


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