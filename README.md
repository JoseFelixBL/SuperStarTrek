# Super Startrek

Port from BBC Basic Super Startrek - November 12, 2023, by Lee Morgan - to Python.  

# Requirements

  - Python 3.9 or newer.
  - A terminal with ANSI colour support.

# Files

  - `main.py` — entry point. Creates a `Game` and runs it.
  - `game.py` — the `Game` class: all game state and logic.
  - `ansi_text_color.py` — small helper for ANSI colour codes.
  - `trek_test.py` — sanity checks and invariants (run with `python trek_test.py`).
  - `INSTRUCTIONS.md` — player's manual.
  - `SST_saved_{1,2,3}.json` — save files (created on demand).  

# License  

The original Super Star Trek program is in the public domain
(published in DEC's "101 BASIC Games", 1971). This port follows
the same licence — use it, modify it, share it. 

# How to install - run

The actual version is meant to be run in a computer with Python 3.12+ :
  - Load all components to a suitable directory
  - In a terminal window, navigate to the installation directory
  - run `python main.py`  

Save files are written to the current directory as `SST_saved_1.json`,  
`SST_saved_2.json`, or `SST_saved_3.json`.  

# Testing

Run the test suite:

    python trek_test.py

The tests verify:
  - Galaxy generation invariants (encoded counts match counters).
  - Region name function.
  - T9 range and average.

## To exit the game while playing

In the Command menu type `XXX`

# Game commands and behaviour

You are the Commander of the USS Enterprise and your mission is to kill all Klingon battle cruisers in the Galaxy within a time limit.

Navigate the galaxy in search for Klingon battle cruisers to destroy  
and starbases to refuel, repair, re-arm.

The Starship has 9 commands:
  - **NAV**: Navigate, Move within this quadrant or to another quadrant in the galaxy.  
  - **SRS**: short range sensor scan, to see what's in this quadrant you are now.  
  - **LRS**: long range sensor scan, to show what is in the nearby quadrants around: Nr. of Klingons, starbases, stars.  
  - **PHA**: phaser control, to destroy Klingon's battle cruisers.  
  - **TOR**: photon torpedo control, to send a torpedo to a Klingon vessel.  
  - **SHE**: shield control to protect from Klingon's attacks.  
  - **DAM**: damage control report, to see what's broken and how long will it take to repair.  
  - **COM**: library-computer, with various options to show.  
  - **XXX**: to save, restore or exit the game.

See `INSTRUCTIONS.md` for detaled information.

# Deviations from the original

The goal of this port has been to preserve the original 1978 game's
behaviour, but a few deliberate changes have been made — either to
fix bugs that have existed for decades, to remove ambiguities, or to
take advantage of Python's features. Each deviation is listed below
with a rationale.

## Deliberate bug fixes

### `Bases = 2` initial value

The original sets `Bases = 2` at the start of the game, before any
galaxy is generated. Since the galaxy always starts with zero bases
and only gains them during `setup_galaxy`, this initial value would
make the counter claim two bases exist when the galaxy might have
none. We start with `Bases = 0` and let `setup_galaxy` and
`fix_up_galaxy` maintain an accurate count.

### `+120` vs `+100` in `fix_up_galaxy`

The original (line 1150) adds `+120` to a quadrant's encoded value
when forcing a fallback starbase, which unpacks as "+1 Klingon and
+2 starbases" — inconsistent with the global `Bases` counter, which
is set to 1 immediately afterwards. We use `+100` (+1 Klingon only)
so the encoded value and the counter stay consistent.

### `Klingons > T9` vs `Klingons >= T9`

The original ensures enough days with `IF Klingons > T9 THEN
T9 = Klingons + 1`. This allows exactly as many days as Klingons.
We use `>=` to guarantee at least one extra day, matching the
"before they attack" framing of the mission orders.

### Base-destroyed end-of-game condition

The original (line 5360) uses a condition that compares the Klingon
count to a *time delta*, which is a units mismatch and almost never
fires in the intended way. We use a semantically meaningful check:
the game ends when there are no bases left *or* the remaining
Klingons outnumber the remaining days.

## Deliberate behaviour changes

### Float courses supported

The original allows fractional courses (e.g. `1.5`) which move the
ship partway between two adjacent directions. Both NAV courses and
torpedo courses accept floats. For Enterprise movement, the final
sector coordinates are rounded to integers when the ship stops, so
the ship always ends on a valid sector.  

### Course and distance format

Distances reported by the computer (`COM 2`, `COM 3`, `COM 4`) are
shown to one decimal place, and directions to two, to aid reading.
The original prints full-precision floats in BASIC's default format.

### Quadrant crossing "teleport"

In the original, when the Enterprise's *total displacement* for a
move crosses more than one quadrant boundary, the crossing routine
recomputes the final position from the *full* energy budget rather
than the steps actually taken before leaving the sector grid. Near
the galaxy edge with high warp, this can "teleport" the ship to a
corner. This behaviour is preserved (it's part of the original's
character), but the code includes comments marking where this
happens.

### Starbase pluralisation in status report

BASIC uses a fixed `X$` variable that is set once and not updated.
If the number of bases drops to 1 after the initial message, the
report can still say "STARBASES". This port recalculates the
pluralisation on each call.

## Cosmetic changes

### ANSI colour

The game uses ANSI colour codes for the sector grid and status
panel. Symbols are colour-coded:
  - `<*>` Enterprise — cyan
  - `+K+` Klingon — red
  - `>!<` Starbase — magenta
  - ` * ` Star — yellow
  - Condition `*RED*` / `GREEN` / `YELLOW` / `DOCKED` — matching colour

This requires a terminal that supports ANSI escape sequences (most
modern terminals do). No effect on gameplay.

### Typo fixes

The original contains several long-standing typos that have been
corrected here:
  - `CRUSER` → `CRUISER`
  - `THEN FEDERATION` → `THE FEDERATION`
  - `CONGRULATION` → `CONGRATULATION`
  - `FDERATION` → `FEDERATION`
  - `MAINTSINING` → `MAINTAINING`
  - `NAVAGATION` → `NAVIGATION`
  - `desrtoy` → `destroy` (in help text)

### Debug mode

A `debug_view` flag (default off) enables:
  - `DBG` command for direction/distance testing.
  - Empty sectors shown as `...` instead of `   `.
  - `|` separators between sector cells.

Not used in normal play.

## Structural changes

### Data model

The original stores the sector grid as a 192-character string (`Q$`)
with fixed-width cells. This port uses a 9×9 2D list of 3-character
strings, which is easier to read, index, and display. The sector
addressing logic (`S8 = ...` in BASIC) is replaced by direct
list indexing.

### Direction calculation

The original's direction routine (`8220-8460`) is written as a
tangle of `GOTO`s with reversed coordinate deltas. The port uses a
clean, documented `my_coord_direction` function that produces the
same results. The original routine is not retained.  

### Single-step routines split

BASIC routines that combined several concerns (e.g. `cmd_nav`
including damage repair, Klingon fire, and ship movement) are split
into separate methods (`cmd_nav`, `begin_moving_starship`,
`exceeded_quadrant_limits`, `klingons_fire`). The dispatch
structure is preserved but the code is no longer a single
fall-through block.  

# Credits

****        **** STAR TREK ****        ****  
SIMULATION OF A MISSION OF THE STARSHIP ENTERPRISE,
AS SEEN ON THE STAR TREK TV SHOW.
ORIGIONAL PROGRAM BY MIKE MAYFIELD, MODIFIED VERSION
PUBLISHED IN DEC'S "101 BASIC GAMES", BY DAVE AHL.
MODIFICATIONS TO THE LATTER (PLUS DEBUGGING) BY BOB
LEEDOM - APRIL & DECEMBER 1974,
WITH A LITTLE HELP FROM HIS FRIENDS . . .  
COMMENTS, EPITHETS, AND SUGGESTIONS SOLICITED --  
SEND TO:
  - R. C. LEEDOM  
  WESTINGHOUSE DEFENSE & ELECTRONICS SYSTEMS CNTR.  
  BOX 746, M.S. 338  
  BALTIMORE, MD  21203  

CONVERTED TO MICROSOFT 8 K BASIC 3/16/78 BY JOHN GORDERS
LINE NUMBERS FROM VERSION STREK7 OF 1/12/75 PRESERVED AS
MUCH AS POSSIBLE WHILE USING MULTIPLE STATEMENTS PER LINE
SOME LINES ARE LONGER THAN 72 CHARACTERS; THIS WAS DONE
BY USING "?" INSTEAD OF "PRINT" WHEN ENTERING LINES

November, 2023 ported to BBC Basic and enhanced in a number of ways
Lee Morgan 11/12/23

Ported to python, 08 October 2026