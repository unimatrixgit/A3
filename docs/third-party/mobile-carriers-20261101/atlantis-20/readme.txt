Atlantis (The lost City of the Ancients) v2.0

Description:
	The lost City of the Ancients. It has been abandoned by the Ancients
 but left in perfect conditions due to being submerged during the siege from
 the Wraith, which forced the Ancients to leave their city. Atlantis is equipped
 with a powerful energy shield and armed with Dones!

Install the puddle jumper first
	- Atlantis lunches puddle jumpers and so needs the puddle jumper installed first

Installation:
	- Add the atlantis.odf to the /odf/ships folder
	- Add the atlantis2.odf to the /odf/ship folder
	- Add the satlantis.odf to the /odf/other folder
	- Add the drone.odf, drone2.odf and drone3.odf to the odf/ weapons/Pulse folder
	- Add the atlantis.sod to the /sod folder
	- Add the atlantishull2.tga, 404.tga, atlantishull2.tga, building6.tga, building.tga, buildings4.tga, buildings9, towers.tga and gbatlantis.tga to the /textures/rgb folder
	- Add the drone.wav to the sounds/ effects folder
	- Add the atlantis.bmp to /bitmaps/AdmiralsLog/ShipImages folder
	- Add the following lines to sprites/gui_global.spr 
@reference=64
@tmaterial=interface
b_atlantis			gbatlantis	0	0	128	128 (if the buttons doesn't appear properly then change the last two numbers to 64)

(if you would like a white blob where the wireframe should be instead of nothing that add this line)
@reference=256
atlantisw1			gbatlantis	0	0	128	128

	- Add the following line to techtree/tech1.tt and fulltech

atlantis.odf	0

	- Add the following line to the station that you wish your DC- 404 class to be build from odf/stations/(station of choice).odf

buildItemX = "atlantis"

remember to replace X with the next number in the sequence.

Weapon:

Installation:
	- Add the drone.odf to the /odf/weapons/Pulse folder
	- Add the drone2.odf to the /odf/weapons/Pulse folder
	- Add the drone3.odf to the /odf/weapons/Pulse folder


Info:

(There will be a V3)

Please check out The Stargate Project for A2 at 
http://forums.stargateproject.co.uk/index.php



Mod Usage:
	
this moddle was Origanly created by 'Me, ColdDarkParanoia'
I have created a build button, odf, admirals log picture, and the weapon for it.  


-------------------------------------------------------------------------------------------------------------------------------
if you would like to uses this ship in your mod could you please contact me.
just remember to give me the credit where it is due :)

i can be reached at ColdDarkParanoia@gmail.com 

activision can't be held resonsible for these files ect.. you know the rest.