from pathlib import Path
import json,re,hashlib
from PIL import Image
root=Path('D:/armadaIII');repo=Path('D:/aramada');errors=[];checked=0
s=(root/'Sprites/gui_global.spr').read_text();icons={}
for line in s.splitlines():
 a=line.split()
 if len(a)==6 and not a[0].startswith(('#','@','//')):
  try:icons[a[0]]=(a[1],*[int(v)for v in a[2:]])
  except ValueError:pass
m=json.loads((repo/'bajor/rebuild-manifest.json').read_text(encoding='utf-8-sig'));names=[u['odf']for u in m['units']]+['xbjuconst'];tex={p.stem.lower():p for p in (root/'Textures').rglob('*.tga')}
for name in names:
 for alias in ['b_'+name]+[name+'w'+str(i)for i in range(1,6)]:
  if alias not in icons:errors.append('Missing mapping '+alias);continue
  t,x,y,w,h=icons[alias];p=tex.get(t.lower())
  if not p:errors.append('Missing texture '+t);continue
  im=Image.open(p)
  if min(x,y)<0 or x+w>im.width or y+h>im.height:errors.append('Invalid bounds '+alias)
  if not im.crop((x,y,x+w,y+h)).getbbox():errors.append('Empty icon '+alias)
  checked+=1
ai=json.loads((repo/'reports/bajoran-federation-ai.json').read_text(encoding='utf-8-sig'));aiChecked=0
for f in ai['files']:
 a=root/f['path'];b=Path(ai['stage'])/f['path']
 if a.read_bytes()!=b.read_bytes():errors.append('AI differs from validated package '+f['path'])
 aiChecked+=1
out={'target':str(root),'iconMappingsChecked':checked,'liveAiProfilesCompared':aiChecked,'errors':errors,'runtimeVerified':False}
(repo/'reports/bajoran-postinstall-audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
