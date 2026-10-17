from pathlib import Path
from PIL import Image
import shutil,json
src=Path('C:/Users/thoma/.codex/generated_images/01a145a1-f38b-7cd1-b2f0-542bd7532033/exec-f5db9640-a20b-47aa-84f4-437b80362310.png');art=Path('D:/aramada/bajor/artwork/armadafiles-adaptation');shutil.copy2(src,art/'normal-adapted.png');out=Path('D:/Xaramada-Modwork/bajor-armadafiles-textures/Textures/RGB');Image.open(src).convert('RGB').resize((512,512),Image.Resampling.LANCZOS).save(out/'bjrhull.tga');print('Normal atlas staged at native 512x512 RGB24')
