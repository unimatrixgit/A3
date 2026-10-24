Bajoran Starbase V2 by CanadianBorg

This is my second mod, so any advice or pointers are appreciated.

The Bajoran Starbase I designed is based on a retextured asteroid model converted from Starfleet Command 1 (yes, I have the original), and the rest is scratch-built.

Thanks to Mishkaco for letting me use his Bajoran ships.

Thanks to FahreS for his transparent textures tutorial. As you can (or can't, they're transparent) see, I used them in the dome. Thanks man!

Installation:

Open the archive file and extract the folder "Bajoran Starbase" somewhere outside your A2 directory.

Copy all the folders inside to your root A2 directory.

Now, open gui_global.spr in the "sprites" folder in your A2 main directory with Notepad, and scroll down to the Federation build buttons. Now enter:

b_bajbase			gbbajbase		0	0	64	64
b_bajscout			gbbajscout		0	0	64	64
b_bajdestroy			gbbajdestroy		0	0	64	64

below the last item.

Close gui_global.spr and go to the techtree folder within the A2 directory with Notepad. Now open tech1.tt. Scroll down to the Federation stations and enter the following:

bajbase.odf 1 ftrading.odf

Now go up to Federation ships and add:

bajscout.odf 1 bajbase.odf
bajdestroy.odf 1 bajbase.odf

Now save and close tech1.tt. Open fulltech.tt with Notepad and enter the following anywhere in the list:

bajbase.odf 0
bajscout.odf 0
bajdestroy.odf 0

Now save and close the file.

Now go to the odf folder, and go "ships". Open fconst.odf with Notepad, and enter the following:

buildItemxx = "bajbase"

Where "xx" is the next number in the list (replace it with this number).

That's it! You're ready to use the Bajoran Starbase and ships in your game! I might be coming out with a V3 of this by the way, so stay tuned!

*******************************************************************************************************************************************************************************
Legalities

This mod is not made or supported by Activision or Paramount
CanadianBorg Industries cannot be held responsible for any damage to your computer or your game by this mod.

If you have any questions, concerns, or suggestions, you can e-mail me at sebastian.renmar@rogers.com

If you wish to use this station in any of your mods, please ask me first. Thank you.