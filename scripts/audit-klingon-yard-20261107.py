from pathlib import Path
import sys,ast,contextlib,io,json,re
import numpy as np
from PIL import Image
R=Path('D:/aramada');L=Path('D:/armadaIII')
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils');from sod_io import SodIO
for n in ast.parse((R/'scripts/stage-armadafiles-yards-20261031.py').read_text()).body:
 if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ['IO','load','matrix','world_nodes','bounds']:exec(compile(ast.Module(body=[n],type_ignores=[]),'h','exec'))
for unit in ['kyard','kyard2','kyard3','fyard','ryard','cyard','dyard']:
 s=(L/'odf/stations'/f'{unit}.odf').read_text();base=re.findall(r'(?im)^baseName\s*=\s*"([^"]+)"',s)[-1];scale=float(re.findall(r'(?im)^ScaleSOD\s*=\s*([\d.]+)',s)[-1]);m=load(L/'SOD'/f'{base}.sod');lo,hi=bounds(m)
 print(unit,base,'span',((hi-lo)*scale).tolist(),'materials',m.materials if unit.startswith('k') else '')
 if unit.startswith('k'):
  print('animations',str(m._animation_transforms)[:350]);print('mesh modes',[(n['id'],n['data']['texture'],n['data']['texture_material']) for n in m.nodes if n['type']=='MESH'][:20])
  for t in {n['data']['texture'] for n in m.nodes if n['type']=='MESH'}:
   for p in (L/'Textures/RGB').glob(t+'.*'):
    with Image.open(p) as im: print('texture',p.name,im.mode,im.size,'alpha',im.getchannel('A').getextrema() if im.mode=='RGBA' else None,'zero',round(np.mean(np.asarray(im.getchannel('A'))==0),3) if im.mode=='RGBA' else None)
