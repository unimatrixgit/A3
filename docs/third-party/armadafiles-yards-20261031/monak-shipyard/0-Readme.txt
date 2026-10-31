******First, back up any files that are to altered or overwritten.*******

Now, first, find these lines in the gui_global.spr file and delete them.

cbasew1				cardwireframe04	0	144	48	48		
cbasew2				cardwireframe04	48	144	48	48		
cbasew3				cardwireframe04	96	144	48	48		
cbasew4				cardwireframe04	144	144	48	48		
cbasew5				cardwireframe04	192	144	48	48

Now add this line under the Cardassian wireframes lines:

@reference=128

Next, place these lines under that one:

cbasew1				cbasewf         0       0      128     128		
cbasew2				cbasewf         0       0      128     128
cbasew3				cbasewf         0       0      128     128
cbasew4				cbasewf         0       0      128     128
cbasew5				cbasewf         0       0      128     128

Also add these lines under the ones above:

cyardw1				cyard4wf        0       0      128     128	
cyardw2				cyard4wf        0       0      128     128
cyardw3				cyard4wf        0       0      128     128
cyardw4				cyard4wf        0       0      128     128
cyardw5				cyard4wf        0       0      128     128

Lastly, find this line:

b_cbase                         gbcbase         0       0       64      64

And place this line underneath it:

b_cyard4                        gbcyard4        0       0       64      64

That's it for the sprites. After that just place the files into the appropriate folders. Then go into each of the tech trees
and make the following entry:

cyard4.odf   1  cresear2.odf                          // Monak Shipyard

Then, add cyard4 as one of the items in the cardassian contruction ship .odf file.
After that, just put whatever ships you want the yard to build into cyard4.odf menu.

The Monak Shipyard was done completely by me using stock Armada II cyard2.tga file(enhanced by me). The Starbase was done by
me except for the five "points" those were used from the stock cardie starbase. Stock textures enhanced by me as well.

If you would like to use this mod, please give me credit for my work and if you don't mind, please ask me as well. Thanks.


Operative34997
