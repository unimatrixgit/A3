from pathlib import Path
from PIL import Image
import re,json,hashlib
root=Path('D:/armadaIII'); stage=Path('D:/Xaramada-Modwork/bajor-icon-hotfix');stage.mkdir(exist_ok=True)
s=(root/'Sprites/gui_global.spr').read_text();atlas=Image.open(root/'Textures/RGB/bjrbuttons.tga');files=[];count=0
pattern=r'(?m)^(\S+) bjrbuttons (\d+) (\d+) 64 64[ \t]*$'
def fix(m):
 global count
 name,x,y=m.group(1),int(m.group(2)),int(m.group(3)); stem='bjic%02d'%(y//64*8+x//64);rel='Textures/RGB/'+stem+'.tga';p=stage/rel;p.parent.mkdir(parents=True,exist_ok=True)
 if rel not in files:atlas.crop((x,y,x+64,y+64)).save(p);files.append(rel)
 count+=1
 return '@reference=64\n@tmaterial=default\n%s %s 0 0 64 64'%(name,stem)
s=re.sub(pattern,fix,s);p=stage/'Sprites/gui_global.spr';p.parent.mkdir(exist_ok=True);p.write_bytes(s.replace('\r','').replace('\n','\r\n').encode('ascii'));files.append('Sprites/gui_global.spr')
assert count==318,count
report={'stage':str(stage),'files':files,'mappings':count,'applied':False,'runtimeVerified':False}
Path('D:/aramada/reports/bajoran-icon-hotfix.json').write_text(json.dumps(report,indent=2));print('Prepared',count,'mappings and',len(files)-1,'individual icons')

