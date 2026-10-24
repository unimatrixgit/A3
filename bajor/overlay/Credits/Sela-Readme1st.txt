Romulan Admiral Sela Hero Mod V1.1 by Warlords Modding Union
For Armada 2 (It will work in A2 and looks alot better then the old A2 Warbird!)

Credits:
Armada 1 Warbird Mesh by Dawn
Armada 1 Warbird Textures cgi renders by Dawn
A1 Build Button by Quevey
A1 Wireframe by chyu Chen
Putting it together by ABubba91873

Special Weapons Credits:
RCRP by Kleotol aka X-Man from X-Treme mod for A1
Energy Capacitors aka X-Man from X-Treme mod A1

PLEASE READ ALL 3 README's FIRST FOR COMPLETE DIRECTIONS TO INSTALL THIS PROPERLY!!!!

Manual Installation "Recommended"

simply
1. put ship odf into your odf/ships folder
2. put special weapons odfs into your odf/special_weapons folder
3. put all tga's into your Textures/RGB folder
4. put the sod into your sod folder
5. Copy and paste sounds in sounds\ingame\voiceovers folder.

GUI GLOBAL

UNFER REF 64 COPY AND PASTE THIS

b_rsela        gbrsela   0   0   64  64

GUI GLOBAL

UNDER REF 128 COPY AND PASTE THIS

rselaw1			RWSela         	40	0	40	40		
rselaw2			RWSela		0	40	40	40		
rselaw3			RWSela		40	40	40	40		
rselaw4			RWSela		80	0	40	40		
rselaw5			RWSela		0	0	40	40	

IN TECH1 LOCATED IN YOUR odf/other FOLDER
COPY AND PASTE THIS

rsela.odf  0

you must now add this vessel to a shipyard

buildItemx = "rsela"

x being the next number from the last ship being built

IN YOUR EVENTS.DAT LOCATED IN YOUR STAR TREK ARMADA 2 ROOT DIRECTORY
COPY AND PASTE THIS AFTER THE PICARD SOUNDS

#################################################################################
# Sela SOUNDS

SelaAcknowledge{
Table
	Sound <romulan> "gvosel29.wav"
	Sound <romulan> "gvosel30.wav"
	Sound <romulan> "gvosel31.wav"
	Sound <romulan> "gvosel32.wav"
	Sound <romulan> "gvosel33.wav"
SoundPriority 1	
}

SelaSelect{
Table
	Sound <romulan> "gvosel01.wav"
	Sound <romulan> "gvosel02.wav"
	Sound <romulan> "gvosel18.wav"
	Sound <romulan> "gvosel19.wav"
	Sound <romulan> "gvosel25.wav"
	Sound <romulan> "gvosel35.wav"
SoundPriority 1	
}

SelaAttack{
Table
	Sound <romulan> "gvosel03.wav"
	Sound <romulan> "gvosel05.wav"
	Sound <romulan> "gvosel06.wav"
	Sound <romulan> "gvosel09.wav"
	Sound <romulan> "gvosel10.wav"
	Sound <romulan> "gvosel11.wav"
SoundPriority 1		
}

SelaRedAlert{
Table
	Sound <romulan> "devred.wav"
SoundPriority 1	
}

SelaYellowAlert{
Table
	Sound <romulan> "devyellow.wav"
SoundPriority 1	
}

SelaGreenAlert{
Table
	Sound <romulan> "devgreen.wav"
SoundPriority 1	
}

SelaStop{
Table
	Sound <romulan> "gvosel21.wav"
	Sound <romulan> "gvosel36.wav"
	Sound <romulan> "gvosel37.wav"
SoundPriority 1		
}

SelaMove{
Table
	Sound <romulan> "gvosel22.wav"
	Sound <romulan> "gvosel23.wav"
	Sound <romulan> "gvosel24.wav"
SoundPriority 1		
}
	
SelaRepair{
Table
	Sound <romulan> "gvosel13.wav"
SoundPriority 1		
}

SelaTransport{
Table
	Sound <romulan> "devtransport.wav"
SoundPriority 1	
}

SelaCloakEngage{
Table
	Sound <romulan> "gvosel27.wav"
SoundPriority 1	
}

SelaCloakDisengage{
Table
	Sound <romulan> "gvosel28.wav"
SoundPriority 1	
}

SelaSelfDestruct{
Table
      Sound <romulan> "devselfdestruct.wav"
SoundPriority 1	
}

###################################################################################

PLEASE SEE README2ND TO INSTALL ENERGY CAPACITOR WEAPON

PLEASE SEE README3RD TO INSTALL ROMULAN CHAIN REACTION TORPEDO 

this model uses high res textures if your video card cannot handle them
or if the ship ingame looks white you'll need to resize them to 256 using
a paint program that can save in 24 bit tga!

THIS SHIP MOD IS NOT SUPPORTED BY ACTIVISION OR MAD DOC

IF YOU HAVE A PROBLEM e-mAIL ME AT
ABubba91873@darkforces.com

VISIT OUR FORUM HERE

http://www.unitedfederation.net/forums/index.php?s=

VISIT OUR WEBSITE FOR OTHER GREAT DOWNLOADS

http://www.armadafleetcommand.com/~warlords/frame.htm

enjoy!

Warlords Modding Union Members

Ares 1999        Founder and leader
Quevey           Model Maker, Public Relations
Dawn             Model maker
Kleotol          X-Treme 2 mod for A2
ABubba91873      Public Relations, Idea Man
Westworld        Naval Armada Mod for A2
The Great One    Model Maker and Webmaster
Gul Straxus      Model Maker
Chyu Chen        Wireframes Maker
Captain Future   Weapons Maker
Terradyhne       Model Maker
Paal             Model Maker Naval Armada A2
Major Payne      Model Maker, Kitbasher Borg Incursion 2
Ben Maxwell      DA2 mod for A1, Model Maker 
