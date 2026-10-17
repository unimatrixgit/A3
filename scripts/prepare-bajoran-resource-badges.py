from pathlib import Path
from PIL import Image
import json,shutil,datetime,hashlib
src=Path('C:/Users/thoma/.codex/generated_images/01a145a1-f38b-7cd1-b2f0-542bd7532033/exec-0070e485-79e1-4109-aa20-2985f73b796d.png');out=Path('D:/aramada/bajor/artwork/resource-icons');shutil.copy2(src,out/'approved-resource-icons.png');im=Image.open(src).convert('RGB');w,h=im.size
for name,box in [('bjic08',(0,0,w//2,h//2)),('bjic29',(w//2,0,w,h//2))]:
 tile=im.crop(box).resize((64,64),Image.Resampling.LANCZOS);tile.save(out/(name+'-badged.tga'));tile.save(out/(name+'-badged.png'))
(out/'generation-notes.txt').write_text('Built-in image_gen edit. Prompt: Preserve the existing bronze/ivory Bajoran building silhouettes on black; add cyan dilithium crystal badge to mining icon and silver metal ingots to orbital icon, readable at 64x64. Approved by user. Output cropped to two 64x64 native TGA textures.\n')
print('Prepared two approved native-size TGA textures')
