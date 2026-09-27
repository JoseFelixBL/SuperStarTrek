"""Super Star Trek — Game class.

Ported from the BBC BASIC listing (May 1978 / Nov 2023 port).
"""

import random
import math

def basic_range(start, end):
    """BASIC FOR I = start TO end, inclusive."""
    return range(start, end + 1)


# We will use OOP as it gives us the advantage of accessing context variables
# without the need to mark them as Globals or sending long structs or
# prameter lists between functions.


class Game:


    def __init__(self, debug_view=False):
        self.debug_view = debug_view
        self.reset()


    def reset(self):
        """BASIC 330 - 710
        Reset all state to start a new game.
        """
        self.show_uss_enterprise()

        # Space objects...
        self.ENTERPRISE = "<*>"
        self.KLINGON = "+K+"
        self.BASE = ">!<"
        self.STAR = " * "
        self.EMPTY_SPACE = "..." if self.debug_view else "   "

        # --- Strings (BASIC variables ending in $) ---
        self.Z_str = " "*25                     # Z$
        self.X_str = ""                         # X$
        self.X0_str = " IS "                    # X0$

        # --- Arrays (BASIC DIM line 330) ---
        self.G = [[0]*9 for _ in range(9)]      # G[][]: Galaxy
        self.Z = [[0]*9 for _ in range(9)]      # Z[][]: Explored/Known galaxy
        self.course = [[0]*3 for _ in range(10)]     # C[][]: Course vectors
        self.K = [[0]*4 for _ in range(4)]      # Klingons in quadrant
        self.N = [0]*4
        self.D = [0]*9                          # D[]: self.damage_on[device_number]

        # --- Scalars (BASIC lines 370-470) ---
        self.today = random.randint(20, 39) *100            # T: Today
        self.start_date = self.today                        # T0: Mission Start date
        self.total_avail_time = 25 + random.randint(0, 9)   # T9: Total available time
        self.docked = 0             # D0: docked: 1 = True, 0 = False

        # E: energy,            E0: full_energy
        self.energy = self.full_energy = 3000

        # P: photon_torpedos,   P0: full_photon_torpedos
        self.photon_torpedos = self.full_photon_torpedos = 10
        self.S9 = 200
        self.shields = 0        # S: shields

        # NOTE: The original BASIC sets Bases = 2 initially, which seems to be a
        # leftover from an older version of the game. The galaxy always starts
        # empty and bases are only added by setup_galaxy(), so Bases should count
        # actual bases. We start at 0 and let setup_galaxy() + fix_up_galaxy()
        # populate it.
        self.Bases = 0
        self.Klingons = 0

        # --- Enterprise's starting position (BASIC 490) ---
        self.enterprise_quad_row = self.fnr(1)          # Q1: enterprise_quad_row
        self.enterprise_quad_column = self.fnr(1)       # Q2: enterprise_quad_column
        self.enterprise_sect_row = self.fnr(1)          # S1: enterprise_sect_row
        self.enterprise_sect_column = self.fnr(1)       # S2: enterprise_sect_column

        # --- Course vectors (BASIC 530-600) ---
        # Row 9 duplicates row 1 (course "9" is same as "1")
        # C[][]: course[][]
        for i in basic_range(1, 9):
            self.course[i][1] = self.course[i][2] = 0
        self.course[3][1] = -1
        self.course[2][1] = -1
        self.course[4][1] = -1
        self.course[4][2] = -1
        self.course[5][2] = -1
        self.course[6][2] = -1
        self.course[1][2] = 1
        self.course[2][2] = 1
        self.course[6][1] = 1
        self.course[7][1] = 1
        self.course[8][1] = 1
        self.course[8][2] = 1
        self.course[9][2] = 1

        # --- Devices start undamaged (BASIC 670) ---
        for i in basic_range(1, 8):
            self.damage_on[i] = 0                   # D[]: self.damage_on[device_number]

        # --- Other Object state variables, and initializations
        self.K7 = 0
        self.Q_str = [[self.EMPTY_SPACE] * 9 for _ in range(9)]    # Start with all space empty
        self.ramdon_delay = 0.0               # D4: Random delay
        self.G5 = 0
        self.condition = "UNKNOWN"
        self.local_klingons = 0
        self.local_bases = 0
        self.local_stars = 0


    def show_uss_enterprise(self):
        """BASIC 220 - 227"""
        for _ in range(11):
            print()

        print("                                    ,------*------,")
        print("                    ,-------------   '---  ------'")
        print("                     '-------- --'      / /")
        print("                         ,---' '-------/ /--,")
        print("                          '----------------'")
        print()
        print("                    THE USS ENTERPRISE --- NCC-1701")
        for _ in range(5):
            print()


    def distance_to_klingon(self, i):
        """BASIC 470
        Distance from Klingon i to Enterprise.
        BASIC: DEFFND(D) = SQR((K(I,1)-S1)^2 + (K(I,2)-S2)^2)
        Note: BASIC used a global I; we pass it explicitly — a deliberate fix.
        """
        return math.sqrt((self.K[i][1] - self.enterprise_sect_row) ** 2 +
                         (self.K[i][2] - self.enterprise_sect_column) ** 2)


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
            if self.G[self.enterprise_quad_row][self.enterprise_quad_column] < 200:
                # NOTE: The original BASIC adds +120 here, which is a transcription bug:
                # it adds 1 Klingon (hundreds) and 2 bases (tens) to this quadrant.
                # Combined with the +10 below, the final quadrant has 3 bases but the
                # global counter says 1. This is how the original has always behaved.
                # I will use the "obviously intended" behaviour, so I use +100 instead.
                # self.G[self.enterprise_quad_row][self.enterprise_quad_column] += 120
                # NOTE: We are adding 1 Klingon to that quadrant and the max number 
                # of klingons in quadrant == 3 holds because the comparisson is `< 200`.
                self.G[self.enterprise_quad_row][self.enterprise_quad_column] += 100
                self.Klingons += 1
            self.Bases = 1
            self.G[self.enterprise_quad_row][self.enterprise_quad_column] += 10

            # Set another random starting Quadrant for Enterprise
            self.enterprise_quad_row = self.fnr(1)
            self.enterprise_quad_column = self.fnr(1)

        self.K7 = self.Klingons

        # Is there enough time?
        # NOTE: I have moved the `enough time` after Bases checking
        # because the number of Klingons can change (added 1) and there 
        # could not be enough time, so better do it with the final
        # Klingons count...
        # NOTE: Also, I have changed the comparison from `>` to `>=`
        # to always allow at least one more day than Klingons.
        if self.Klingons >= self.total_avail_time:
            self.total_avail_time = self.Klingons + 1


    def print_orders(self):
        """Show mission briefing. BASIC 1201, 1230-1280."""
        if self.Bases != 1:
            self.X_str = "S"
            self.X0_str = " ARE "

        print(f'YOUR ORDERS ARE AS FOLLOWS:')
        print(f'     DESTROY THE {self.Klingons} KLINGON WARSHIPS WHICH HAVE INVADED')
        print(f'  THE GALAXY BEFORE THEY CAN ATTACK FEDERATION HEADQUARTERS')
        print(f'  ON STARDATE {self.start_date + self.total_avail_time} THIS GIVES YOU {self.total_avail_time} DAYS. THERE{self.X0_str}')
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
        # Z4 = self.enterprise_quad_row
        # Z5 = self.enterprise_quad_column
        self.local_klingons = 0
        self.local_bases = 0
        self.local_stars = 0
        self.G5 = 0
        self.ramdon_delay = .5 * random.random()          # Random delay recalculated on quadrant entry
        self.update_known_galaxy()

        # 1390
        # if not (self.enterprise_quad_row < 1 or self.enterprise_quad_row > 8 or self.enterprise_quad_column < 1 or self.enterprise_quad_column > 8):
        # if 1 <= self.enterprise_quad_row <= 8 and 1 <= self.enterprise_quad_column <= 8:
        # `if` not needed as Q1 and Q2 come from fnr ::> are always in range

        self.local_klingons = self.G[self.enterprise_quad_row][self.enterprise_quad_column] // 100
        self.local_bases = self.G[self.enterprise_quad_row][self.enterprise_quad_column] // 10 % 10
        self.local_stars = self.G[self.enterprise_quad_row][self.enterprise_quad_column] % 10

        self.print_quadrant_entry()
        

    def update_known_galaxy(self):
        self.Z[self.enterprise_quad_row][self.enterprise_quad_column] = self.G[self.enterprise_quad_row][self.enterprise_quad_column]


    def print_quadrant_entry(self):
        """
        BASIC 1430 - 
        Printing Info regarding the just entered Quadrant
        """
        # 1430 - Gosub 9030 Grab region name
        g2_quadrant_name = self.region_name(self.enterprise_quad_row, self.enterprise_quad_column)
        print()
        if self.start_date != self.today:
            print(f'NOW ENTERING {g2_quadrant_name} QUADRANT . . .')
        else:
            # Instructions printed at the begining of the game
            print(f'YOUR MISSION BEGINS WITH YOUR STARSHIP LOCATED')
            print(F'IN THE GALACTIC QUADRANT {g2_quadrant_name}.')

        # 1500
        print()

        if self.local_klingons:
            print(f'COMBAT AREA      CONDITION RED')
            if self.shields <= 200:
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
        Z1 = self.enterprise_sect_row
        Z2 = self.enterprise_sect_column
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

        if self.debug_view:
            # DEBUG ONLY - print the actual Galaxy to check the number
            # of objects vs. the ones printed
            self.debug_print_galaxy()


    def insert_in_quadrant(self, space_object, row, column):
        """
        BASIC: 8670
        INSERT IN STRING ARRAY FOR QUADRANT
        space_object: What to insert
        row: == Z1 == y coordinate
        column: == Z2 == x coordinate
        """
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
        for i in basic_range(self.enterprise_sect_row - 1, self.enterprise_sect_row + 1):
            for j in basic_range(self.enterprise_sect_column - 1, self.enterprise_sect_column + 1):
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
            self.docked = 1
            self.condition = "DOCKED"
            self.energy = self.full_energy
            self.photon_torpedos = self.full_photon_torpedos
            print('SHIELDS DROPPED FOR DOCKING PURPOSES')
            self.shields = 0
        else:
            self.docked = 0
            if self.local_klingons:
                self.condition = "*RED*"
            else:
                self.condition = "GREEN"
                if self.energy < self.full_energy * .1:
                    self.condition = "YELLOW"


    def srs_display(self):
        """
        BASIC 6720 - 7260
        Short Range Sensor Scan - Draw Sector + status panel
        """
        # 6720 - Check if SRS is Damaged
        if self.damage_on[2] < 0:
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
            1: f'{int(self.today * 10) * .1:g}',
            2: f'{self.condition}',
            3: f'{self.enterprise_quad_row}, {self.enterprise_quad_column}',
            4: f'{self.enterprise_sect_row}, {self.enterprise_sect_column}',
            5: f'{int(self.photon_torpedos)}',
            6: f'{int(self.energy + self.shields)}',
            7: f'{int(self.shields)}',
            8: f'{int(self.Klingons)}',
        }

        # DEBUG ONLY - put a `|` to "see" the space.
        sector_sep = '|' if self.debug_view else ' '
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
\tToday: {self.today} - Start Date: {self.start_date} - Total Avail. Time: {self.total_avail_time}\n\
\tQuadrant: [{self.enterprise_quad_row}, {self.enterprise_quad_column}], Sector: [{self.enterprise_sect_row}, {self.enterprise_sect_column}]\n\
\tKlingons: {self.Klingons} - Bases: {self.Bases}'


    def debug_print_galaxy(self):
        """Quick print of the Klingons-Bases-Stars distribution"""
        print('\n>> DEBUG PRINT OF THE GALAXY <<\n')
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


    def command_loop(self):
        """
        BASIC 1990 - 2060
        """
        while True:
            # Line 1990: check for stranded ship
            if self.shields + self.energy <= 10 or not (self.energy > 10 or self.damage_on[7] == 0):
                self.print_fatal_error()
                return

            # Line 2060: read command
            a_str = input("COMMAND ").strip().upper()[:3]

            # Dispatch
            if a_str == "NAV":
                self.cmd_nav()
            elif a_str == "SRS":
                self.srs_scan_and_startup()
            elif a_str == "LRS":
                self.cmd_lrs()
            elif a_str == "PHA":
                self.cmd_pha()
            elif a_str == "TOR":
                self.cmd_tor()
            elif a_str == "SHE":
                self.cmd_she()
            elif a_str == "DAM":
                self.cmd_dam()
            elif a_str == "COM":
                self.cmd_com()
            elif a_str == "XXX":
                return
            else:
                self.print_commands()


    def print_fatal_error(self):
        """
        BASIC 2020 - 2050
        """
        print()
        print( "** FATAL ERROR **   YOU'VE JUST STRANDED YOUR SHIP IN ")
        print( "SPACE" )
        print("YOU HAVE INSUFFICIENT MANEUVERING ENERGY,")
        print( " AND SHIELD CONTROL" )
        print( "IS PRESENTLY INCAPABLE OF CROSS")
        print( "-CIRCUITING TO ENGINE ROOM!!")
        self.end_of_game()


    def end_of_game(self):
        """
        BASIC 6220 - 6280
        """
        print(f'IT IS STARDATE {self.today}')
        print(f'THERE WERE {self.Klingons} KLINGON BATTLE CRUISERS LEFT AT')
        print('THE END OF YOUR MISSION.')
        self.any_bases_left()


    def any_bases_left(self):
        """
        BASIC 6290 - 6360
        """
        print('\n\n')

        if not self.Bases:
            quit()

        self.want_to_play_another()


    def want_to_play_another(self):
        """
        BASIC 6310 - 6360
        """
        print("THE FEDERATION IS IN NEED OF A NEW STARSHIP COMMANDER")
        print("FOR A SIMILAR MISSION -- IF THERE IS A VOLUNTEER,")
        a_str = input("LET HIM STEP FORWARD AND ENTER 'AYE' ").strip().upper()
        if a_str == "AYE":
           self.reset()
           self.play()
        quit()


    def enterprise_destroyed(self):
        """
        BASIC 6240 - 6250
        """
        print('THE ENTERPRISE HAS BEEN DESTROYED. THEN FEDERATION ')
        print('WILL BE CONQUERED')
        self.end_of_game()


    def mission_acomplished(self):
        """
        BASIC 6370 - 6400
        """
        print("CONGRULATION, CAPTAIN! THEN LAST KLINGON BATTLE CRUISER")
        print("MENACING THE FDERATION HAS BEEN DESTROYED.")
        print()
        print(f"YOUR EFFICIENCY RATING IS {1000 * (self.K7 / (self.today - self.start_date)) ** 2}")
        self.any_bases_left()


    def print_commands(self):
        """
        BASIC 2060
        """
        print("ENTER ONE OF THE FOLLOWING:")
        print("  NAV  (TO SET COURSE)")
        print("  SRS  (FOR SHORT RANGE SENSOR SCAN)")
        print("  LRS  (FOR LONG RANGE SENSOR SCAN)")
        print("  PHA  (TO FIRE PHASERS)")
        print("  TOR  (TO FIRE PHOTON TORPEDOES)")
        print("  SHE  (TO RAISE OR LOWER SHIELDS)")
        print("  DAM  (FOR DAMAGE CONTROL REPORTS)")
        print("  COM  (TO CALL ON LIBRARY-COMPUTER)")
        print("  XXX  (TO RESIGN YOUR COMMAND)")
        print()


    def cmd_nav(self):
        """
        BASIC 2300 - 3480
        """

        course_ok, course = self.select_course()
        if not course_ok:
            return

        warp_ok, warp = self.select_warp()
        if not warp_ok:
            return

        enough_energy, energy = self.energy_needed(warp)
        if not enough_energy:
            return

        self.klingons_move()
        self.klingons_fire()

        
        # 2700
        D1 = 0
        D6 = W1
        if W1 >= 1:
            D6 = 1
        for i in basic_range(1, 8):
            if self.damage_on[i] >= 0:
                continue
            self.damage_on[i] += D6
            if self.damage_on[i] > -.1 and self.damage_on[i] < 0:
                self.damage_on[i] = -.1
                continue
            if self.damage_on[i] < 0:
                continue
            if self.damage_on[i] != 1:
                self.damage_on[i] = 1
                print(f'DAMAGE CONTROL REPORT: ')
            print(f'{" " * 8}')
            device = i
            device_name = self.device_name(device)
            print(f'{device} REPAIR COMPLETED.')
        if random.random() > .2:
            # in 2880: Goto 3070 Moving starship
            self.begin_moving_starship(course)
            self.srs_scan_and_startup()
        R1 = self.fnr(1)
        if random.random() >= .6:
            # in 2910: Gosub 3000
            # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
            pass


    def begin_moving_starship(self, course):
        """BASIC 3070 - 3450"""
        # Leaving this sector...
        self.insert_in_quadrant(self.EMPTY_SPACE, int(self.enterprise_sect_row, int(self.enterprise_sect_column)))

        self.X1 = self.course[course][1] + (self.course[course + 1][1] - self.course[course][1]) * (course - int(course))
        self.X = self.enterprise_sect_row
        self.Y = self.enterprise_sect_column
        self.X2 = self.course[course][2] + (self.course[course + 1][2] - self.course[course][2]) * (course - int(course))
        self.Q4 = self.enterprise_quad_row
        self.Q5 = self.enterprise_quad_column

        # 3170...
        for i in basic_range(1, self.N):
            self.enterprise_sect_row += self.X1
            self.enterprise_sect_column += self.X2
            if not ( 1 <= self.enterprise_sect_row < 9 and 1 <= self.enterprise_sect_column < 9 ):
                self.exceeded_quadrant_limits()
                # Check if need to end the for loop...
            # 3240 S8 comprobar si hay 2 espacios...
            self.enterprise_sect_row - X1
            self.enterprise_sect_column - X2
            print(f'WARP ENGINESSHUT DOWN AT SECTOR {self.enterprise_sect_row}, {self.enterprise_sect_column} DUE TO BAD NAVIGATION')

        self.insert_in_quadrant(self.ENTERPRISE, self.enterprise_sect_row, self.enterprise_sect_column)
        self.maneuver_energy()
        T8 = 1
        if W1 < 1:
            T8 = .1 * int(10 * W1)
        self.today += T8
        if self.today > self.start_date + self.total_avail_time:
            self.end_of_game()

        # 3480: Goto 1980 --> Gosub 6430: SRS Scan done after returning this method


    def exceeded_quadrant_limits(self):
        """BEGIN 3500"""
        # Remember the quadrant are not spaces, it is a 2D struc


    def klingons_move(self):
        """Basic 2590 - """
        for i in basic_range(1, self.local_klingons):
            if not self.K[i][3]:
                continue

            self.insert_in_quadrant(self.EMPTY_SPACE, self.K[i][1], self.K[i][2])
            row, column = self.find_empty_place_in_quadrant()
            self.insert_in_quadrant(self.KLINGON, row, column)


    def klingons_fire(self):
        """Basic 6000 - 6200"""
        if not self.local_klingons:
            return

        if self.docked:
            print('STARBASE SHIELDS PROTECT THE ENTERPRISE')
            return

        for i in basic_range(1, 3):
            if self.K[i][3] <= 0:
                continue
            # Why distance_to_klingon(1) instead of distance_to_klingon(i) ???

            hit_power = int((self.K[i][3] / self.distance_to_klingon(1)) * (2 + (former_rnd:=random.random())))
            self.shields -= hit_power
            self.K[i][3] /= (3 + former_rnd)
            print(f'{hit_power} UNIT HIT ON ENTERPRISE FROM SECTOR {self.K[i][1]}, {self.K[i][2]}')

            if self.shields <= 0:
                self.enterprise_destroyed()

            print(f'      <SHIELDS DOWN TO {self.shields} UNITS>')

            # Small hit...
            if hit_power < 20:
                continue

            # Good luck, nothing affected...
            if random.random() > .6 or self.shields <= .02:
                continue

            self.device_affected(hit_power)


    def device_affected(self, hit_power):
        """BASIC 6140 - 6170"""
        device = self.fnr(1)
        self.damage_on[device] = self.damage_on[device] - hit_power / self.shields - .5 * random.random()
        device_name = self.device_name(device)
        print(f'DAMAGE CONTROL REPORTS {device_name} DAMAGED BY THE HIT')


    def device_name(self, device_number):
        """BASIC 8790
        device_number: The device index to search
        RETURN a device name"""
        DEVICES = {
            1: "WARP ENGINES",
            2: "SHORT RANGE SENSORS",
            3: "LONG RANGE SENSORS",
            4: "PHASER CONTROL",
            5: "PHOTON TUBES",
            6: "DAMAGE CONTROL",
            7: "SHIELD CONTROL",
            8: "LIBRARY-COMPUTER"
        }
        return DEVICES.get(device_number, "")


    def select_course(self):
        """BASIC 2300 - 2330"""
        course_ok = False
        course = input("COURSE (0-9)")
        if not (course.isnumeric()):
            self.incorrect_course()
            return course_ok, course

        course = int(course)
        course = 1 if course == 9 else course
        if not (1 <= course < 9):
            self.incorrect_course()
            return course_ok, course

        course_ok = True
        return course_ok, course


    def select_warp(self):
        """BASIC 2350 - 2470"""
        warp_ok = False
        max_warp = 8
        if self.damage_on[1] < 0:
            max_warp = 0.2

        warp = input(f'WARP FACTOR (0-{max_warp})')
        # NOTE: Check the input and convert to integer...

        if self.damage_on[1] > 0 and warp > .2:
            print('WARP ENGINES ARE DAMAGED. MAXIMUM SPEED = WARP 0.2')
            return warp_ok, warp

        if not(warp > 0 and W1 <= 8):
            if warp == 0:
                warp_ok = True
                return warp_ok, warp
            print(f"   CHIEF ENGINEER SCOTT REPORTS 'THE ENGINES WON'T TAKE WARP {W1}!'")
            return warp_ok, warp


    def energy_needed(self, warp):
        """Basic 2490 - 2570"""
        enough_energy = False
        needed = int(warp * 8 + .5)
        if self.energy - needed < 0:
            print( "ENGINEERING REPORTS: 'INSUFFICIENT ENERGY' AVAILABLE")
            print(f"                      FOR MANEUVERING AT WARP {warp}!'")

            # Can not-damaged Shields lend me enough energy...?
            if self.shields < needed - self.energy or self.damage_on[7] < 0:
                enough_energy = True
                return enough_energy, needed
            print(f'DEFLECTOR CONTROL ROOM ACKNOWLEDGES {self.shields} UNITS OF ENERGY')
            print( '                      PRESENTLY DEPLOYED TO SHIELDS.')
            return enough_energy, needed
 

    def incorrect_course(self):
        print("   LT. SULU REPORTS, 'INCORRECT COURSE DATA, SIR!'")


    def maneuver_energy(self):
        """BASIC 3910 - 3980"""
        self.energy -= (self.N + 10)
        if self.energy >= 0:
            return

        print("SHIELD CONTROL SUPPLIES ENERGY TO COMPLETE THE MANEUVER.")
        self.shields += self.E
        self.energy = 0
        if self.shields <= 0:
            self.shields = 0
        return


    def cmd_lrs(self):
        print('... LRS ...')


    def cmd_pha(self):
        print('... PHA ...')


    def cmd_tor(self):
        print('... TOR ...')


    def cmd_she(self):
        print('... SHE ...')


    def cmd_dam(self):
        """BASIC 5690 - 5980"""
        if self.damage_on[6] >= 0:
            self.show_damage_status()
        else:
            # Damage control "damaged", cannot check...
            print("DAMAGE CONTROL REPORT NOT AVAILABLE")

            # If no damage, return
            if not self.docked:
                return

        # Compute the cumulative delays: D3
        self.D3 = 0
        for i in basic_range(1, 8):
            if self.damage_on[i] < 0:
                self.D3 += .1

        # Nothing to repair
        if not self.D3:
            return

        print()
        # Add random delay (D4) that chages on every quadrant entry
        self.D3 += self.ramdon_delay
        self.D3 = .9 if self.D3 >= 1 else self.D3

        print('TECHNICIANS STANDING BY TO EFFECT REPAIRS TO YOUR SHIP')
        print(f'ESTIMATED TIME TO REPAIR: {.01 * int(100 * self.D3)} STARDATES')
        y_n = input('WILL YOU AUTHORIZE THE REPAIR ORDER (Y/N) ').strip().upper()
        if y_n != "Y":
            return

        # Do the repairs
        for i in basic_range(1, 8):
            if self.damage_on[i] < 0:
                self.damage_on[i] = 0

        # Update Today's date with delays
        self.today += self.D3 + .1

        self.show_damage_status()


    def show_damage_status(self):
        """BASIC 5910 - """
        print()
        print("DEVICE             STATE OF REPAIR")
        for device in basic_range(1, 8):
            dev_name = self.device_name(device)
            print(f'{dev_name:<25}{int(self.damage_on[device] * 100) * .01}')
        print()



    def cmd_com(self):
        print('... COM ...')


    def play(self):
        """Play the game"""
        self.setup_galaxy()
        self.fix_up_galaxy()
        self.print_orders()
        self.enter_quadrant()
        self.setup_quadrant()
        self.command_loop()
        quit()
