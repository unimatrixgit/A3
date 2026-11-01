|------------------------------------------|
|   Aurora Warship Installation Read-me    |
|------------------------------------------|
|            Read-me created by:           |
|       wraith_shadow  and  Greathor       |
|------------------------------------------|

Step 1 -
	Add the aurora.odf to the /odf/ships folder
----------------------------------------------------------------------------------------------
Step 2 -
	Add the aurora.sod to the /sod folder
----------------------------------------------------------------------------------------------
Step 3 -
	Add the following files to the /textures/rgb folder

aurora1.tga
aurora2.tga
aurora3.tga
wdrone2.tga
gbaurora.tga
waurora.tga
----------------------------------------------------------------------------------------------
Step 4 -
	Add the aurora.bmp to /bitmaps/AdmiralsLog/ShipImages folder
----------------------------------------------------------------------------------------------
Step 5 -
	Add the following lines to "sprites/gui_global.spr" below,
		" @reference=64
		@tmaterial=interface "

b_aurora			gbaurora		0	0	64	64

	(if the buttons doesn't appear properly then change the last two numbers to 128)
----------------------------------------------------------------------------------------------
Step 6 -
	Add the following lines to "sprites/gui_global.spr" below,
		" # Federation wireframes "
@reference=128
auroraw1			waurora		40 	0	40 	40
auroraw2			waurora		0 	40 	40 	40
auroraw3			waurora		40 	40 	40 	40
auroraw4			waurora		80 	0	40 	40
auroraw5			waurora		0 	0 	40 	40

	(if there is already a "@reference=128", just start copying at auroraw1)
----------------------------------------------------------------------------------------------
Step 7 -
	Add the following line to techtree/tech1.tt and fulltech

aurora.odf 0
----------------------------------------------------------------------------------------------
Step 8 -
	Add the following line to the station that you wish your Aurora Warship to be build from 
	odf/stations/(station of choice).odf

buildItemX = "aurora"

remember to replace X with the next number in the sequence.

			

Step 9 -

Go into weapon sprite and add

# Drone Weapon
wdrone	      wdrone	      0	0	256	64	@anim=tex1x4

# Drone Weapon
wdrone2	      wdrone2	      0	0	256	64	@anim=tex1x4