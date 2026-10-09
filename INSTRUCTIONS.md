# Super Startrek Instructions

### To exit the game while playing
In the Command menu type `XXX`

### To save or restore while playing

Type `XXX` in the Command menu. You'll be prompted to save (S),
restore (R), or exit (X). Save files are numbered 1–3 and stored
as `SST_saved_1.json` etc. in the game's directory.

## Game commands and behaviour
You are the Commander of the USS Enterprise and your mission is to kill all Klingons in the Galaxy within a time limit.

You navigate the galaxy in search for Klingons to kill, and starbases to refuel, repair, re-arm.

You are in a galaxy that spans 8 x 8 quadrants in (row, column) format.  

Each quadrant has 8 x 8 sectors, also in (row, column) format.

You have the following commands:  
  - **NAV**: Warp engine control  
    Course is a circular numerical vector arrangement.
    Integer and real values may be used.
    One warp factor is the size of a Quadrant, therefore
    to get from quadrant 6,5 to 5,5 you would use 
    course 3, warp factor 1.  

```
    Courses:  
      4    3    2  
        \  |  /  
         \ | /  
     5 - - * - - 1  
         / | \  
        /  |  \
      6    7    8   
```

  - **SRS**: short range sensor scan  
    Shows a scan of your actual quadrant.  
    Symbols are:  
      `<*>` = Your Starship position - cyan  
      `+K+` = Klingon battle cruiser - red  
      `>!<` = Federation starbase (refuel/repair/re-arm here!) - magenta  
      ` * ` = Star - yellow

  - **LRS**: long range sensor scan  
    Show conditions in space for one quadrant on each side  
    of the Enterprise (which is in the middle of the scan)  
    The scan is coded in the form `###` where the units digit  
    is the number of stars, the tens digit is the number of  
    starbases, and the hundreds digit is the number of  
    Klingons.  

  - **PHA**: phaser control  
    Allows you to destroy the Klingon battle cruisers by  
    zapping them with suitably large units of energy to
    deplete their shield power. (Remember, Klingons have  
    phasers too!)  

  - **TOR**: photon torpedo control  
    Torpedo course is the same as used in warp engine control.  
    If you hit the Klingon vessel, it gets destroyed and cannot  
    fire back at you. If you miss, you are subject to his phaser  
    fire. In either case, you are also subject to the phaser fire  
    of all other Klingons in the quadrant.  

    The library-computer (**COM** command) has an option to compute  
    torpedo trajectory for you (option 2).  

  - **SHE**: shield control  
    Define the number of energy units to be assigned to the  
    shields. Energy is taken from total ship's energy. Note  
    that the status display Total Energy includes shield energy.  

  - **DAM**: Damage control report  
    Gives the state of repair of all devices. Where a negative  
    'state of repair' shows that the device is temporarily  
    damaged.  

  - **COM**: library-computer  
    The library-computer contains 6 options:  
    - Option 0: cumulative galactic record  
      This option shows computer memory of the result of all  
      previous short and long range sensor scans  
    - Option 1: status report  
      This option shows the number of Klingons, stardates,  
      and starbases remaining in the game.  
    - Option 2: photon torpedo data  
      Which gives directions and distance from the Enterprise  
      to all Klingons in your quadrant  
    - Option 3: starbase nav data  
      This option gives direction and distance to any  
      starbase within your quadrant  
    - Option 4: direction/distance calculator  
      This option allows you to enter coordinates for  
      direction/distance calculations  
    - Option 5: galactic *region name* map  
      This option prints the names of the sixteen major  
      galactic regions referred to in the game  

  - **XXX**: To quit mid-game.