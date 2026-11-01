Puddle jumer v2.0


Description:
	Small Ancient space craft built by the Atlantians. Highly maneuverable and equipped with stealth mode allowing
 complete invisibility. Small enough to fit through a stargate. Weapons:There are 2 types of drone. 1=the none-explosive drones used in the atlantian out-post on earth. 2=the explosive drones fired by the puddle-jumper
(no sheilds tho, However the hull is increadable strong and can withstand enormous pressure"


Installation:
	- Add the puddlejumper.odf to the /odf/ships folder
	- Add the puddlejumper.sod to the /sod folder
	- Add the jumper.tga, jumper underside.tga, jumper3.tga and gbjumper.tga to the /textures/rgb folder
	- Add the puddlejumper.bmp to /bitmaps/AdmiralsLog/ShipImages folder
	- Add the sprites.spr and the glows.spr to the /sprites folder
	- Add the following lines to sprites/gui_global.spr 
@reference=64
@tmaterial=interface
b_puddlejumper			gbjumper	0	0	64	64

(if you would like a white blob where the wireframe should be instead of nothing that add this line)
@reference=256
puddlejumperw1			gbjumper	0	0	128	128

	- Add the following line to techtree/tech1.tt and fulltech

puddlejumper.odf	0

	- Add the following line to the station that you wish your puddle jumper to be build from odf/stations/(station of choice).odf

buildItemX = "puddlejumper"

remember to replace X with the next number in the sequence.


Mod Usage:

This is Version 2 of my puddle jumper, Version two was original ment to be a poly reduced version of the bridge commander version created by By Dave975 and DKealt
E-Mail = daverussell_345@fsmail.net who very kindly gave me plermission to convert and release and use any of their material. the original model was 24,711 poly 
From that model ive managed to get it down to just over 1,000 polys. The only bits of the model that are left are the shape of the drive pods, which ive reduced Heavily 
every thing else ive rebuild from scratch using the original model as a scale for all the new parts as i rebuild them bit by bit. 

The Textures are the same as those in Version 1.

i can be reached at ColdDarkParanoia@gmail.com 

Neither Activision nor I can be held responcible for any damage cause to your machine with the use of these files.