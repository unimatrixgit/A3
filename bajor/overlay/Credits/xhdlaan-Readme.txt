*****************************************************************************************************************
Dominion Ships - FOR ARMADA 2

*****************************************************************************************************************


INSTALLATION --------------

Place the sod files in your sod folder

Place the odf files into the relevent odf folders. (ships, and weapons)

Add all the bitmap files to your bitmaps/AdmiralsLog/ShipImages folder.

Add all the TGA files to your textures/RGB folder.

-----------------------
 
Locate a suitable yard to build from (eg cyard2) from within your odf/stations folder.
Add the following in your construction parameters:

buildItem4 = "jcruisex"
buildItem5 = "warcruiser"


Locate the file ec_named from within your odf/other folder.
Add the following lines to the list:

item2 = "bug"
item3 = "jcruisex"
item4 = "warcruiser"


This will make the new ships available in the map editor. (you will find them under cardassian named ships)

-----------------------
-----------------------

Locate your gui_global file from within your sprite folder. 
Add the following at the end of the federation build buttons:

b_warcruiser	gbwarcruiser	0	0	64	64
b_bug			gbbug			0	0	64	64	
b_jcruisex		gbjcruisex		0	0	64	64


Next scroll down to where it says:
 
## SPRITE DATA  ##

# Ship Wireframes

Underneath this add the following:


@reference=256
@tmaterial=interface

warcruiserw1		domw1		0	0	128	128
bugw1				domw1		128	0	128	128
jcruisex			domw1		0	128	128	128


-----------------------

Locate your fulltech file from within your techtree folder.
Add the following:

warcruiser.odf	 0
bug.odf	 0
jcruisex	 0

repeat this with the file named tech1.

---------------------------------END----------------------------------------------------------------------------

 
*****************************************************************************************************************
CREDITS AND COPYRIGHT

Meshes: Built by Avon
Textures: Avon
Odfs, buttons, and all other stuff: Avon

Research, ideas, guidance, and dohnuts: From Transmission

Assault ship based on designs by RavenNight
Warcruiser based on Dominion Wars game


These ships were built for people to enjoy. If you want to re-release my models in any form 
that is ok, but you MUST give credit 

---------------------------------------------------------------
This is a freeware mod and not to be used for commercial gain. You instal this mod at your own risk.

THIS MOD IS NOT MADE, DISTRIBUTED, OR SUPPORTED BY ACTIVISION. 

Copyright notices: 

Star Trek, Star Trek: Deep Space Nine, Star Trek: The Next Generation, Star Trek: Voyager 
(and the various logo devices used in them) are copyright Paramount Pictures, as are the characters, 
related images, and sound from those productions. TM & (C) ACTIVISION & PARAMOUNT PICTURES


*****************************************************************************************************************



