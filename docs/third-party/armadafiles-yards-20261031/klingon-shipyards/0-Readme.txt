Adding the Wireframes:

***First, back up any files that are to be modded(you already knew that).***

Next, find these lines in the gui global sprite file and delete them.

kyardw1				klingwireframe05	0	0	48	48		
kyardw2				klingwireframe05	48	0	48	48		
kyardw3				klingwireframe05	96	0	48	48		
kyardw4				klingwireframe05	144	0	48	48		
kyardw5				klingwireframe05	192	0	48	48

kyard2w1			klingwireframe05	0	48	48	48		
kyard2w2			klingwireframe05	48	48	48	48		
kyard2w3			klingwireframe05	96	48	48	48		
kyard2w4			klingwireframe05	144	48	48	48		
kyard2w5			klingwireframe05	192	48	48      48


Now add this line under the stock klingon wireframe entries:

@reference=128

Then add these lines under that one:

kyardw1                         kyardwf                 0       0       128     128
kyardw2                         kyardwf                 0       0       128     128
kyardw3                         kyardwf                 0       0       128     128
kyardw4                         kyardwf                 0       0       128     128
kyardw5                         kyardwf                 0       0       128     128

kyard2w1                        kyard2wf                0       0       128     128
kyard2w2                        kyard2wf                0       0       128     128
kyard2w3                        kyard2wf                0       0       128     128
kyard2w4                        kyard2wf                0       0       128     128
kyard2w5                        kyard2wf                0       0       128     128

Lastly, edit the following line:

b_kyard2			gbkyard200		0	0	64	64

To read like this:

b_kyard2			gbkyard2		0	0	64	64

After that just drop all of the files into their appropriate folders and place whatever ships you want into the build menus.

Kyard2 was done completely by me using modified stock texures that I got from the SFC: Project Armada done by Darkdrone.
Kyard was a partial kitbash of the original kyard from Armada II using the same textures.

Operative34997