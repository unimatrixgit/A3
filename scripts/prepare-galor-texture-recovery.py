from pathlib import Path
from PIL import Image
import shutil,json,hashlib
root=Path('D:/armadaIII');stage=Path('D:/Xaramada-Modwork/galor-texture-recovery');stage.mkdir(exist_ok=True);src=root/'Textures/RGB/Galor.tga';dest=stage/'Galor2.tga';shutil.copy2(src,dest);im=Image.open(dest);assert im.size==(256,256)and im.mode=='RGB';assert not(root/'Textures/RGB/Galor2.tga').exists()
r={'stage':str(dest),'target':'D:/armadaIII/Textures/RGB/Galor2.tga','source':str(src),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'affectedModel':'cogalor.sod','missingReference':'Galor2','applied':False,'runtimeVerified':False,'scope':'Add missing texture filename alias only; no model/ODF/stat/GUI changes.'};Path('D:/aramada/reports/galor-texture-recovery.json').write_text(json.dumps(r,indent=2));print('Missing texture alias prepared and format verified')
