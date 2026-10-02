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
        self.G = [[0]*9 for _ in range(9)]              # G[][]: Galaxy
        self.known_galaxy = [[0]*9 for _ in range(9)]   # Z[][]: self.know_galaxy : Explored/Known galaxy
        self.course = [[0]*3 for _ in range(10)]        # C[][]: Course vectors
        self.K = [[0]*4 for _ in range(4)]              # Klingons in quadrant
        self.N = [0]*4
        self.damage_on = [0]*9                          # D[]: self.damage_on[device_number]

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
        self.bases = 0
        self.klingons = 0

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
        self.random_delay = 0.0               # D4: Random delay
        self.G5 = 0
        self.condition = "UNKNOWN"
        self.local_klingons = 0
        self.local_bases = 0
        self.local_stars = 0

        # New vars to control game ending or repeating
        # game_over is to signal the end of this game, no more cmd_loop
        self.game_over = False
        self.play_another = True


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
        """BASIC 470 (FND)
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
                self.known_galaxy[i][j] = 0             # Not Known quadrant
                ods = random.random()
                self.local_klingons = 0
                if ods > .98:
                    self.local_klingons = 3
                elif ods > .95:
                    self.local_klingons = 2
                elif ods > .8:
                    self.local_klingons = 1
                self.klingons += self.local_klingons

                self.local_bases = 1 if random.random() > .96 else 0
                self.bases += self.local_bases

                # the self.fnr(1) are the Stars on each Quadrant.
                self.G[i][j] = self.local_klingons * 100 + self.local_bases * 10 + self.fnr(1)


    def fix_up_galaxy(self):
        """BASIC 1100-1160
        Ensure at least one starbase and enough time.
        """
        # At least 1 Base should exist...
        if not self.bases:
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
                self.klingons += 1
            self.bases = 1
            self.G[self.enterprise_quad_row][self.enterprise_quad_column] += 10

            # Set another random starting Quadrant for Enterprise
            self.enterprise_quad_row = self.fnr(1)
            self.enterprise_quad_column = self.fnr(1)

        self.K7 = self.klingons

        # Is there enough time?
        # NOTE: I have moved the `enough time` after Bases checking
        # because the number of Klingons can change (added 1) and there 
        # could not be enough time, so better do it with the final
        # Klingons count...
        # NOTE: Also, I have changed the comparison from `>` to `>=`
        # to always allow at least one more day than Klingons.
        if self.klingons >= self.total_avail_time:
            self.total_avail_time = self.klingons + 1


    def print_orders(self):
        """Show mission briefing. BASIC 1201, 1230-1280."""
        if self.bases != 1:
            self.X_str = "S"
            self.X0_str = " ARE "

        print(f'YOUR ORDERS ARE AS FOLLOWS:')
        print(f'     DESTROY THE {self.klingons} KLINGON WARSHIPS WHICH HAVE INVADED')
        print(f'  THE GALAXY BEFORE THEY CAN ATTACK FEDERATION HEADQUARTERS')
        print(f'  ON STARDATE {self.start_date + self.total_avail_time} THIS GIVES YOU {self.total_avail_time} DAYS. THERE{self.X0_str}')
        print(f'  {self.bases} STARBASE{self.X_str} IN THE GALAXY FOR RESUPPLYING YOUR SHIP')
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
        self.random_delay = .5 * random.random()          # Random delay recalculated on quadrant entry
        self.update_known_galaxy()

        # 1390
        # if not (self.enterprise_quad_row < 1 or self.enterprise_quad_row > 8 or self.enterprise_quad_column < 1 or self.enterprise_quad_column > 8):
        # if 1 <= self.enterprise_quad_row <= 8 and 1 <= self.enterprise_quad_column <= 8:
        # `if` not needed as Q1 and Q2 come from fnr ::> are always in range

        self.local_klingons = self.G[self.enterprise_quad_row][self.enterprise_quad_column] // 100
        self.local_bases = self.G[self.enterprise_quad_row][self.enterprise_quad_column] // 10 % 10
        self.local_stars = self.G[self.enterprise_quad_row][self.enterprise_quad_column] % 10

        self.print_quadrant_entry()

        self.setup_quadrant()
        

    def update_known_galaxy(self):
        self.known_galaxy[self.enterprise_quad_row][self.enterprise_quad_column] = self.G[self.enterprise_quad_row][self.enterprise_quad_column]


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
            # self.debug_print_galaxy()
            pass


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
            8: f'{int(self.klingons)}',
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
\tKlingons: {self.klingons} - Bases: {self.bases}'


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
        while not self.game_over and self.play_another:
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
                self.play_another = False
                return
            else:
                self.print_commands()


    def print_fatal_error(self):
        """
        BASIC 2020 - 2050
        """
        self.game_over = True
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
        print(f'IT IS STARDATE {self.today:.1f}')
        print(f'THERE WERE {self.klingons} KLINGON BATTLE CRUISERS LEFT AT')
        print('THE END OF YOUR MISSION.')
        print()
        print()
        self.any_bases_left()


    def any_bases_left(self):
        """
        BASIC 6290 - 6360
        """
        if self.bases <= 0:
            self.play_another = False
            return

        self.want_to_play_another()


    def want_to_play_another(self):
        """
        BASIC 6310 - 6360
        """
        print("THE FEDERATION IS IN NEED OF A NEW STARSHIP COMMANDER")
        print("FOR A SIMILAR MISSION -- IF THERE IS A VOLUNTEER,")
        a_str = input("LET HIM STEP FORWARD AND ENTER 'AYE' ").strip().upper()

        self.play_another = False
        if a_str == "AYE":
           self.play_another = True
           # self.reset()
           # self.play()
        # quit()


    def enterprise_destroyed(self):
        """
        BASIC 6240 - 6250
        """
        self.game_over = True
        print()
        print('THE ENTERPRISE HAS BEEN DESTROYED. THEN FEDERATION WILL BE CONQUERED')
        self.end_of_game()


    def mission_accomplished(self):
        """
        BASIC 6370 - 6400
        """
        self.game_over = True
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

        # 2300
        course_ok, course = self.select_course()
        if not course_ok:
            return

        # 2350
        warp_ok, warp = self.select_warp()
        if not warp_ok:
            return

        # 2490
        enough_energy, energy = self.energy_needed(warp)
        if not enough_energy:
            return

        self.klingons_move()
        self.klingons_fire()
        if self.game_over:
            return

        # 2700
        D1 = 0
        D6 = warp if warp < 1 else 1

        # 2770
        for i in basic_range(1, 8):
            if self.damage_on[i] >= 0:
                continue

            # 2790
            self.damage_on[i] += D6
            if -.1 < self.damage_on[i] < 0:
                self.damage_on[i] = -.1
                continue

            # 2800
            if self.damage_on[i] < 0:
                continue

             # 2810 - Print report header only once
            if D1 != 1:
                D1 = 1
                print(f'DAMAGE CONTROL REPORT: ', end='')

            # 2840
            device = i
            device_name = self.device_name(device)
            print(f'{" " * 8}{device_name} REPAIR COMPLETED.')

        if random.random() > .2:
            # 80% of times we move with no change on devices
            # in 2880: Goto 3070 Moving starship
            self.begin_moving_starship(course, warp, energy)
            return
        
        # 2910
        # The other 20% of times there might be changes on devices
        R1 = self.fnr(1)
        device_name = self.device_name(R1)
        if random.random() >= .6:
            # 40% of times: improvements
            # in 2910: Goto 3000
            # It could be done even in the not damaged devices
            self.damage_on[R1] += random.random() * 3 + 1
            print(f'DAMAGE CONTROL REPORT: {device_name} STATE OF REPAIR IMPROVED\n')
        else:
            # 60% of times: damage
            # 2930
            self.damage_on[R1] -= (random.random() * 5 + 1)
            print(f'DAMAGE CONTROL REPORT: {device_name} DAMAGED\n')

        self.begin_moving_starship(course, warp, energy)


    def begin_moving_starship(self, course, warp, energy):
        """BASIC 3070 - 3450"""
        # Leaving this sector...
        self.insert_in_quadrant(self.EMPTY_SPACE, int(self.enterprise_sect_row), int(self.enterprise_sect_column))

        row_dir = self.course[int(course)][1] + (self.course[int(course) + 1][1] - self.course[int(course)][1]) * (course - int(course))
        s_row = self.enterprise_sect_row
        s_col = self.enterprise_sect_column
        col_dir = self.course[int(course)][2] + (self.course[int(course) + 1][2] - self.course[int(course)][2]) * (course - int(course))
        from_quad_row = self.enterprise_quad_row
        from_quad_col = self.enterprise_quad_column

        # 3170... Check that the path is workable: full of EMPTY_SPACE to go through
        # for all the energy steps to take in that direction...
        crossed = False
        for i in basic_range(1, energy):
            s_row += row_dir                # S1
            s_col += col_dir                # S2
            # self.enterprise_sect_row += row_dir
            # self.enterprise_sect_column += col_dir
            self.enterprise_sect_row = int(s_row + .5)
            self.enterprise_sect_column = int(s_col + .5)

            if not ( 1 <= self.enterprise_sect_row < 9 and 1 <= self.enterprise_sect_column < 9 ):
                # going out of my quadrant (out of sector bounds)
                self.exceeded_quadrant_limits(row_dir, col_dir, s_row, s_col, energy)

                if self.game_over:
                    return

                if from_quad_row != self.enterprise_quad_row or from_quad_col != self.enterprise_quad_column:
                    # enter_quadrant only if in a new quadrant
                    crossed = True
                    self.today += 1
                    self.enter_quadrant()
                if self.no_time_left():
                    return

                break

            # 3240 S8, check is new coords are empty
            if self.is_object_in_coordinates(self.EMPTY_SPACE, self.enterprise_sect_row, self.enterprise_sect_column):
                continue

            # Not empty, energy not consumed, no more step checks
            self.enterprise_sect_row = int(self.enterprise_sect_row - row_dir)
            self.enterprise_sect_column = int(self.enterprise_sect_column - col_dir)
            print(f'WARP ENGINES SHUT DOWN AT SECTOR {self.enterprise_sect_row}, {self.enterprise_sect_column} DUE TO BAD NAVIGATION')
            break
        else:
            self.enterprise_sect_row = int(self.enterprise_sect_row)
            self.enterprise_sect_column = int(self.enterprise_sect_column)

        if not crossed:
            self.insert_in_quadrant(self.ENTERPRISE, self.enterprise_sect_row, self.enterprise_sect_column)

        self.maneuver_energy(energy)

        if not crossed:
            T8 = 1
            if warp < 1:
                T8 = .1 * int(10 * warp)
            self.today += T8

        if self.no_time_left():
            self.end_of_game()
            return


    def no_time_left(self):
        if self.today > self.start_date + self.total_avail_time:
            self.game_over = True
            return True
        return False


    def time_left(self):
        return self.total_avail_time - ( self.today - self.start_date)
    

    def exceeded_quadrant_limits(self, row_dir, col_dir, s_row, s_col, energy):
        """BEGIN 3500 - 3870"""
        X = 8 * self.enterprise_quad_row + s_row + energy * row_dir
        Y = 8 * self.enterprise_quad_column + s_col + energy * col_dir
        self.enterprise_quad_row = X // 8
        self.enterprise_quad_column = Y // 8
        self.enterprise_sect_row = int(X - self.enterprise_quad_row * 8)
        self.enterprise_sect_column = int(Y -self.enterprise_quad_column * 8)

        if self.enterprise_sect_row == 0:
            self.enterprise_quad_row -= 1
            self.enterprise_sect_row = 8

        if self.enterprise_sect_column == 0:
            self.enterprise_quad_column -= 1
            self.enterprise_sect_column = 8

        # Am I going into the unknown? (out of 8x8 quadrants of the game)
        out_of_galaxy = False
        if self.enterprise_quad_row < 1:
            out_of_galaxy = True
            self.enterprise_quad_row = 1
            self.enterprise_sect_row = 1

        if self.enterprise_quad_row > 8:
            out_of_galaxy = True
            self.enterprise_quad_row = 8
            self.enterprise_sect_row = 8

        if self.enterprise_quad_column < 1:
            out_of_galaxy = True
            self.enterprise_quad_column = 1
            self.enterprise_sect_column = 1

        if self.enterprise_quad_column > 8:
            out_of_galaxy = True
            self.enterprise_quad_column = 8
            self.enterprise_sect_column = 8

        if out_of_galaxy:
            print("LT. UHURA REPORTS MESSAGE FROM STARFLEET COMMAND:")
            print(" 'PERMISSION TO ATTEMPT CROSSING OF GALACTIC PERIMETER")
            print("IS HEREBY *DENIED*. SHUT DOWN YOUR ENGINES.'")
            print("CHIEF ENGINEER SCOTT REPORTS 'WARP ENGINES SHUT DOWN")
            print(f"AT SECTOR {self.enterprise_sect_row}, {self.enterprise_sect_column} OF QUADRANT {self.enterprise_quad_row}, {self.enterprise_quad_column}.'")

            if self.no_time_left():
                return


    def klingons_move(self):
        """Basic 2590 - """
        for i in basic_range(1, self.local_klingons):
            if self.K[i][3] == 0:
                continue

            self.insert_in_quadrant(self.EMPTY_SPACE, self.K[i][1], self.K[i][2])
            row, column = self.find_empty_place_in_quadrant()
            self.K[i][1] = row
            self.K[i][2] = column
            self.insert_in_quadrant(self.KLINGON, row, column)


    def klingons_fire(self):
        """Basic 6000 - 6200"""
        if not self.local_klingons:
            return

        if self.docked:
            print('STARBASE SHIELDS PROTECT THE ENTERPRISE')
            return

        # 6040
        for i in basic_range(1, 3):
            if self.K[i][3] <= 0:
                continue

            hit_power = int((self.K[i][3] / self.distance_to_klingon(i)) * (2 + (former_rnd:=random.random())))
            self.shields -= hit_power
            self.K[i][3] /= (3 + former_rnd)
            print(f'{hit_power} UNIT HIT ON ENTERPRISE FROM SECTOR {self.K[i][1]}, {self.K[i][2]}')

            # 6090
            if self.shields <= 0:
                self.enterprise_destroyed()
                return

            print(f'      <SHIELDS DOWN TO {self.shields} UNITS>')

            # Small hit...
            if hit_power < 20:
                continue

            # Good luck, nothing affected...
            if random.random() > .6 or hit_power / self.shields <= .02:
                continue

            self.device_affected(hit_power)


    def device_affected(self, hit_power):
        """BASIC 6140 - 6170"""
        device = self.fnr(1)
        self.damage_on[device] = self.damage_on[device] - hit_power / self.shields - .5 * random.random()
        device_name = self.device_name(device)
        print(f"DAMAGE CONTROL REPORTS {device_name} DAMAGED BY THE HIT'")


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
        try:
            # I will use courses as int; if using float, indexes are wrong, also 
            # We will need to define how does the float-course increments coordinates moves
            # instead of being -1, 0 or 1, and what to do when the final calculation 
            # returns a fraction of a sector, which sector shall we choose.
            # 
            # course = int(input("COURSE (0-9)"))
            #
            course = float(input("COURSE (0-9)"))
        except:
            self.incorrect_nav_course()
            return course_ok, 0

        course = 1 if course == 9 else course
        if not (1 <= course < 9):
            self.incorrect_nav_course()
            return course_ok, 0

        course_ok = True
        return course_ok, course


    def select_warp(self):
        """BASIC 2350 - 2470"""
        warp_ok = False
        max_warp = 8 if self.damage_on[1] >= 0 else 0.2
        if self.damage_on[1] < 0:
            max_warp = 0.2

        # 2360
        try:
            warp = float(input(f'WARP FACTOR (0-{max_warp})'))
        except:
            print("   CHIEF ENGINEER SCOTT REPORTS 'INCORRECT WARP FIGURE, SIR!'")
            return warp_ok, 0

        if self.damage_on[1] < 0 and warp > .2:
            # 2470
            print('WARP ENGINES ARE DAMAGED. MAXIMUM SPEED = WARP 0.2')
            return warp_ok, 0

        # 2380
        if 0 < warp <= 8:
            warp_ok = True
            return warp_ok, warp
        
        # 2390
        if warp == 0:
            return warp_ok, 0

        #2420
        print(f"   CHIEF ENGINEER SCOTT REPORTS 'THE ENGINES WON'T TAKE WARP {warp}!")
        return warp_ok, 0


    def energy_needed(self, warp):
        """Basic 2490 - 2570"""
        enough_energy = False
        # One warp gives you energy to move 8 sectors, so, to the next quadrant, same sector.
        needed = int(warp * 8 + .5)

        if self.energy - needed < 0:
            print( "ENGINEERING REPORTS: 'INSUFFICIENT ENERGY' AVAILABLE")
            print(f"                      FOR MANEUVERING AT WARP {warp}!'")

            # 2530
            if self.shields < needed - self.energy or self.damage_on[7] < 0:
                return enough_energy, needed

            print(f'DEFLECTOR CONTROL ROOM ACKNOWLEDGES {self.shields} UNITS OF ENERGY')
            print( '                      PRESENTLY DEPLOYED TO SHIELDS.')
            return enough_energy, needed

        enough_energy = True
        return enough_energy, needed
 

    def incorrect_nav_course(self):
        print("   LT. SULU REPORTS, 'INCORRECT COURSE DATA, SIR!'")


    def maneuver_energy(self, energy):
        """BASIC 3910 - 3980"""
        self.energy -= (energy + 10)
        if self.energy >= 0:
            return

        print("SHIELD CONTROL SUPPLIES ENERGY TO COMPLETE THE MANEUVER.")
        self.shields += self.energy
        self.energy = 0
        if self.shields <= 0:
            self.shields = 0
        return


    def cmd_lrs(self):
        """BASIC 4000 - 4230"""
        # Is LRS damaged?
        if self.damage_on[3] < 0:
            print("LONG RANGE SENSORS ARE INOPERABLE")
            return

        print(f'LONG RANGE SCAN FOR QUADRANT {self.enterprise_quad_row}, {self.enterprise_quad_column}')
        separator = f'{"-" * 19}'
        print(separator)
        for i in basic_range(self.enterprise_quad_row - 1, self.enterprise_quad_row + 1):
            self.N[1] = -1
            self.N[2] = -2
            self.N[3] = -3
            for j in basic_range(self.enterprise_quad_column - 1, self.enterprise_quad_column + 1):
                if 0 < i < 9 and 0 < j < 9:
                    self.N[j - self.enterprise_quad_column + 2] = self.G[i][j]
                    self.known_galaxy[i][j] = self.G[i][j]
            for l in basic_range(1, 3):
                print(': ', end='')
                if self.N[l] < 0:
                    print("*** ", end='')
                else:
                    print(f'{self.N[l]:03} ', end='')
            print(":")
            print(separator)


    def cmd_pha(self):
        """BASIC 4260 - 4670"""
        # Are Phasers damaged?
        if self.damage_on[4] < 0:
            print('PHASERS INOPERATIVE')
            return

        if self.local_klingons <= 0:
            print("SCIENCE OFFICER SPOCK REPORTS 'SENSORS SHOW NO ENEMY SHIPS")
            print("                               IN THIS QUADRANT'")
            return

        if self.damage_on[8] < 0:
            print("COMPUTER FAILURE HAMPERS ACCURACY")
        print("PHASERS LOCKED ON TARGET; ", end="")
        while True:
            print(f"ENERGY AVAILABLE = {self.energy} UNITS")
            fire_units = input("NUMBER OF UNITS TO FIRE ")
            try:
                fire_units = int(float(fire_units))
            except:
                return

            if fire_units <= 0:
                return

            if self.energy - fire_units >= 0:
                break

        # fire_units = int(float(fire_units))
        self.energy -= fire_units
        if self.damage_on[7] < 0:
            fire_units *= random.random()

        H1 = int(fire_units/self.local_klingons)
        for i in basic_range(1, 3):
            if self.K[i][3] <= 0:
                continue
            H = int((H1 / self.distance_to_klingon(i)) * (random.random() + 2))
            if H <= .15 * self.K[i][3]:
                print(f'SENSORS SHOW NO DAMAGE TO ENEMY AT {self.K[i][1]}, {self.K[i][2]}')
                continue

            self.K[i][3] -= H
            print(f'{H} UNIT HIT ON KLINGON AT SECTOR {self.K[i][1]}, {self.K[i][2]}')
            if self.K[i][3] > 0:
                print(f'(SENSORS SHOW {self.K[i][3]:.1f} UNITS REMAINING)')
                continue

            print('*** KLINGON DESTROYED ***')
            self.local_klingons -=1
            self.klingons -= 1
            self.insert_in_quadrant(self.EMPTY_SPACE, self.K[i][1], self.K[i][2])

            self.K[i][3] = 0
            self.G[self.enterprise_quad_row][self.enterprise_quad_column] -= 100
            self.known_galaxy[self.enterprise_quad_row][self.enterprise_quad_column] = self.G[self.enterprise_quad_row][self.enterprise_quad_column]
            if self.klingons <= 0:
                self.mission_accomplished()
                return

        self.klingons_fire()


    def cmd_tor(self):
        """BASIC 4700 - 5490"""
        if self.photon_torpedos <= 0:
            print("ALL PHOTON TORPEDOS EXPENDED")
            return

        if self.damage_on[5] < 0:
            print("PHOTON TUBES ARE NOT OPERATIONAL")
            return

        course = input("PHOTON TORPEDO COURSE (1-9) ")
        try:
            # 
            # course = int(float(course))
            #
            course = float(course)
        except:
            self.incorrect_tor_course()
            return

        if course == 9:
            course = 1

        if not 1 <= course < 9:
            self.incorrect_tor_course()
            return

        # 4850

        # X1 = row_dir
        row_dir = self.course[int(course)][1] + (self.course[int(course) + 1][1] - self.course[int(course)][1]) * (course - int(course))
        self.energy -= 2
        self.photon_torpedos -= 1
        # Y1 = col_dir
        col_dir = self.course[int(course)][2] + (self.course[int(course) + 1][2] - self.course[int(course)][2]) * (course - int(course))
        s_row = self.enterprise_sect_row
        s_col = self.enterprise_sect_column

        print("TORPEDO TRACK:")
        while True:
            s_row += row_dir                # X
            s_col += col_dir                # Y
            tor_row = int(s_row + .5)       # X3
            tor_col = int(s_col + .5)       # Y3

            # Out of quadrant: Torpedo missed...
            if not (1 <= tor_row <= 8 and 1 <= tor_col <= 8):
                print("TORPEDO MISSED")
                self.klingons_fire()
                return

            # print actual trajectory
            print(f'{" " * 15}{tor_row}, {tor_col}')
            if self.is_object_in_coordinates(self.EMPTY_SPACE, tor_row, tor_col):
                continue

            if self.is_object_in_coordinates(self.KLINGON, tor_row, tor_col):
                self.klingon_destroyed(tor_row, tor_col)
                if self.game_over:
                    return
                self.klingons_fire()
                return
                
            if self.is_object_in_coordinates(self.STAR, tor_row, tor_col):
                print(f"STAR AT {tor_row}, {tor_col} ABSORBED TORPEDO ENERGY.")
                self.klingons_fire()
                return

            if self.is_object_in_coordinates(self.BASE, tor_row, tor_col):
                self.base_destroyed(tor_row, tor_col)
                if self.game_over:
                    return
                self.klingons_fire()
                return


    def base_destroyed(self, row, col):
        """BASIC 5330 - """
        print("*** STARBASE DESTROYED ***")
        self.local_bases -= 1
        self.bases -= 1
        # Checking for the possible end of the game, I think there is an error:
        # in BASIC it reads IF Bases > 0 OR Klingons > T... (if there are bases or ther is not enogh time left; how come having bases is a game ending?)
        # Shouldn't it be IF Bases > 0 or Klingons <= T... 
        #
        # Original BASIC line 5360:
        # if self.bases > 0 or self.klingons > self.today - self.start_date - self.total_avail_time: 
        #
        # The following is my modified version: if no bases OR no time: game_over.
        # Re-reading the ORDERS the mission is to destroy all the Klingons before certain date - nothing about having bases left...
        # ...
        if self.bases <= 0 or self.klingons > self.time_left():
            print("THAT DOES IT, CAPTAIN!! YOU ARE HEREBY RELIEVED OF COMMAND")
            print("AND SENTENCED TO 99 STARDATES AT HARD LABOR ON CYGNUS 12!!")
            # Here I include an extra print (It is stardate T)
            self.game_over = True
            self.end_of_game()
            return
        print("STARFLEET COMMAND REVIEWING YOUR RECORD TO CONSIDER")
        print("COURT MARTIAL!")
        self.insert_in_quadrant(self.EMPTY_SPACE, row, col)
        self.G[self.enterprise_quad_row][self.enterprise_quad_column] = self.local_klingons * 100 + self.local_bases * 10 + self.local_stars
        self.known_galaxy[self.enterprise_quad_row][self.enterprise_quad_column] = self.G[self.enterprise_quad_row][self.enterprise_quad_column]


    def klingon_destroyed(self, row, col):
        """BASIC 5110 - 5470"""
        print("*** KLINGON DESTROYED ***")
        self.local_klingons-= 1
        self.klingons -= 1
        if self.klingons <= 0:
            self.mission_accomplished()
            return

        for i in basic_range(1, 3):
            if row == self.K[i][1] and col == self.K[i][2]:
                self.K[i][3] = 0
                self.insert_in_quadrant(self.EMPTY_SPACE, row, col)
                self.G[self.enterprise_quad_row][self.enterprise_quad_column] = self.local_klingons * 100 + self.local_bases * 10 + self.local_stars
                self.known_galaxy[self.enterprise_quad_row][self.enterprise_quad_column] = self.G[self.enterprise_quad_row][self.enterprise_quad_column]


    def incorrect_tor_course(self):
        print("ENSIGN CHEKOV REPORTS, 'INCORRECT COURSE DATA, SIR!'")


    def cmd_she(self):
        """BASIC 5530 - 5660"""
        # Are shields damaged?
        if self.damage_on[7] < 0:
            print('SHIELDS INOPERABLE')
            return

        units = input(f'ENERGY AVAILABLE = {self.energy + self.shields}, NUMBER OF UNITS TO SHIELDS ')
        try:
            units = int(float(units))
        except:
            print('<SHIELDS UNCHANGED>')
            return

        if units < 0 or units == self.shields:
            print('<SHIELDS UNCHANGED>')
            return

        if units > self.energy + self.shields:
            print("SHIELD CONTROL REPORTS 'THIS IS NOT THE FEDERATION TREASURY.'")
            print('<SHIELDS UNCHANGED>')
            return

        self.energy += self.shields - units
        self.shields = units
        print('DEFLECTOR CONTROL ROOM REPORT:')
        print(f" 'SHIELDS NOW AT {int(self.shields)} UNITS PER YOUR COMMAND.'")
        return


    def cmd_dam(self):
        """BASIC 5690 - 5980"""
        if self.damage_on[6] >= 0:
            # Damage control works: show status
            self.show_damage_status()
        else:
            # Damage control "damaged", cannot check...
            print("DAMAGE CONTROL REPORT NOT AVAILABLE")

            if not self.docked:
                return

        # Compute the cumulative delays: D3
        self.D3 = 0
        for i in basic_range(1, 8):
            if self.damage_on[i] < 0:
                self.D3 += .1

        # Nothing to repair
        if self.D3 == 0:
            return

        print()
        # Add random delay (D4) that chages on every quadrant entry
        self.D3 += self.random_delay
        
        # Delay is less than one day
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
        """BASIC 7290 -"""
        if self.damage_on[8] < 0:
            print("COMPUTER DISABLED")
            return

        while True:
            command = input("COMPUTER ACTIVE AND AWAITING COMMAND: ")
            try:
                command = int(command)
            except:
                self.print_computer_options()
                continue

            bool_val = True
            if command == 0:
                self.com_cumulative_gal_record()
                return
            if command == 1:
                self.com_status_report()
                return
            if command == 2:
                self.com_tor_data()
                return
            if command == 3:
                self.com_starbase_nav_data()
                return
            if command == 4:
                self.com_d_d_calculator()
                return
            if command == 5:
                self.com_galaxy_region_map()
                return
            if command < 0:
                return
            self.print_computer_options()


    def print_computer_options(self):
        """BASIC 7350"""

        print("FUNCTIONS AVAILABLE FROM LIBRARY-COMPUTER:")
        print("   0 = CUMULATIVE GALACTIC RECORD")
        print("   1 = STATUS REPORT")
        print("   2 = PHOTON TORPEDO DATA")
        print("   3 = STARBASE NAV DATA")
        print("   4 = DIRECTION/DISTANCE CALCULATOR")
        print("   5 = GALAXY 'REGION NAME' MAP")
        print()


    def com_status_report(self):
        """BASIC 7890 - 8020"""
        print("   STATUS REPORT")
        self.X_str = "" if self.klingons == 1 else "S"
        print(f"KLINGON{self.X_str} LEFT: {self.klingons}")
        print(f"MISSION MUST BE COMPLETED IN {.1 * int((self.start_date + self.total_avail_time - self.today) * 10)} STARDATES")
        self.X_str = "" if self.bases < 2 else "S"
        if self.bases >= 1:
            print(f"THE FEDERATION IS MAINTSINING {self.bases} STARBASE{self.X_str} IN THE GALAXY")
        else:
            print("YOUR STUPIDITY HAS LEFT YOU ON YOUR ON IN")
            print(" THE GALAXY -- YOU HAVE NO STARBASES LEFT!")
        self.cmd_dam()


    def com_tor_data(self):
        print("PHOTON TORPEDO DATA - *** NOT YET IMPLEMENTED ***")
        

    def com_starbase_nav_data(self):
        print("STARBASE NAV DATA - *** NOT YET IMPLEMENTED ***")
        

    def com_d_d_calculator(self):
        """BASIC 8150 - 8480"""
        print("DIRECTION/DISTANCE CALCULATOR - *** NOT YET COMPLETELY IMPLEMENTED ***")
        print("DIRECTION/DISTANCE CALCULATOR:")
        print(f"YOU ARE AT QUADRANT {self.enterprise_quad_row}, {self.enterprise_quad_column} SECTOR {self.enterprise_sect_row}, {self.enterprise_sect_column}")
        print("PLEASE ENTER")
        coord_ok, from_x = self.ask_coordinate("  INITIAL COORDINATE (X) ")
        if not coord_ok:
            return
        coord_ok, from_y = self.ask_coordinate("  INITIAL COORDINATE (Y) ")
        if not coord_ok:
            return
        coord_ok, to_x = self.ask_coordinate("  FINAL COORDINATE (X) ")
        if not coord_ok:
            return
        coord_ok, to_y = self.ask_coordinate("  FINAL COORDINATE (Y) ")
        if not coord_ok:
            return


    def ask_coordinate(self, msg):
        coord = input(msg)
        try:
            from_x = int(from_x)
        except:
            print("*** BAD COORDINATE ***")
            return False, coord
        if not (1 <= from_x <= 8):
            print("*** BAD COORDINATE ***")
            return False, coord
        return True, coord



    def com_galaxy_region_map(self):
        """BASIC 7400"""
        print("                        THE GALAXY")
        self.print_galaxy_headers()
        self.print_galaxy_sep()
        self.print_galaxy_region_names()
        self.print_galaxy_sep()


    def print_galaxy_headers(self):
        """BASIC 7550 - 7570"""
        print("       1     2     3     4     5     6     7     8")


    def print_galaxy_sep(self):
        """BASIC 7560"""
        galaxy_sep = "     ----- ----- ----- ----- ----- ----- ----- -----"
        print(galaxy_sep)


    def com_cumulative_gal_record(self):
        """BASIC 7530 -"""
        self.print_cumulative_headers()
        self.print_galaxy_headers()
        self.print_galaxy_sep()
        self.print_known_galaxy()


    def print_known_galaxy(self):
        """BASIC 7570 - 7850"""
        for i in basic_range(1, 8):
            print(f"{i}   ", end="")
            for j in basic_range(1, 8):
                known_data = str(f'{self.known_galaxy[i][j]:03d}') if self.known_galaxy[i][j] != 0 else "***"
                print(f' {known_data:^5}', end='')
            print()
            self.print_galaxy_sep()
        print()


    def print_cumulative_headers(self):
        """BASIC 7543 - 7546"""
        print()
        print("        ", end="")
        print(f"COMPUTER RECORD OF GALAXY FOR QUADRANT {self.enterprise_quad_row}, {self.enterprise_quad_column}")
        print()


    def print_galaxy_region_names(self):
        """BASIC """
        for i in basic_range(1, 8):
            print(f"{i}   ", end="")
            north_region = self.region_name(i, 1, region_only=True)
            south_region = self.region_name(i, 5, region_only=True)
            print(f' {north_region:^24}{south_region:^24}')


    def play(self):
        """Play the game"""
        while self.play_another:
            if self.game_over:
                self.reset()
            self.setup_galaxy()
            self.fix_up_galaxy()
            self.print_orders()
            self.enter_quadrant()
            self.command_loop()
