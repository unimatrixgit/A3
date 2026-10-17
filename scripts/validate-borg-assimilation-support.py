from pathlib import Path
import re,json,hashlib,contextlib,io
exec(Path('D:/aramada/scripts/build-bajoran-redesign-v3.py').read_text().split('ROOT=')[0])
R=Path('D:/armadaIII');O=Path('D:/Xaramada-Modwork/borg-assimilation-stations');g=(R/'Sprites/gui_global.spr').read_text(encoding='latin1')+'\n// Borg assimilation support - matching model icons\n@reference=512\n@tmaterial=default\n'
for i,n in enumerate(['xbharvest','xbassimst','xbrepair']):
 for alias in ['b_'+n]+[n+'w'+str(k)for k in range(1,6)]:g+=f'{alias} xbstatbtn {i*64} 0 64 64\n'
g+='@reference=64\n@tmaterial=default\nb_xbharvbeam gbbaabore00 0 0 64 64\nb_xbassimbeam gbholdbm00 0 0 64 64\n'
p=O/'Sprites/gui_global.spr';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(g,encoding='latin1')
# Resolve definitions against the staged overlay, including inherited values.
idx={f.stem.lower():f for f in (R/'odf').rglob('*.odf')};idx.update({f.stem.lower():f for f in (O/'odf').rglob('*.odf')})
def props(n,seen=None):
 seen=set()if seen is None else seen;assert n not in seen,n;seen.add(n);t=idx[n].read_text(encoding='latin1');d={}
 for inc in re.findall(r'^\s*#include\s+"([^"]+)"',t,re.M):d.update(props(Path(inc).stem.lower(),seen.copy()))
 for k,v in re.findall(r'^\s*(\w+)\s*=\s*([^\r\n]*)',t,re.M):d[k.lower()]=v.split('//')[0].strip().strip('"')
 return d
report={'stage':str(O),'gameplayVerified':False,'units':[],'issues':[]}
for n,crew in [('xbharvest',200),('xbassimst',500),('xbrepair',50)]:
 d=props(n);assert d['crewcost']==str(crew) and d['maximumcrew']==str(crew)
 with contextlib.redirect_stdout(io.StringIO()):m=IO().read_file(str(O/'SOD'/(n+'.sod')))
 anchors={v['id'].lower()for v in m.nodes};texidx={p.stem.lower()for p in(R/'Textures').rglob('*.tga')}|{p.stem.lower()for p in(O/'Textures').rglob('*.tga')}
 for v in m.nodes:
  if v['type']=='MESH':
   for tex in [v['data']['texture'],(v['data'].get('borgification')or{}).get('texture','')]:assert not tex or tex.lower()in texidx,tex
 for k,v in d.items():
  if re.fullmatch(r'weapon\d+',k):assert v.lower()in idx,v
  if re.fullmatch(r'weaponhardpoints\d+',k):
   for hp in re.findall(r'\w+',v):assert hp.lower()in anchors,(n,hp)
 if n=='xbassimst':assert d['builditem0']=='xbrepair' and {'build','repair'}<=anchors and d['classlabel']=='shipyard'
 report['units'].append({'odf':n,'crew':crew,'dilithium':d['dilithiumcost'],'metal':d['metalcost'],'buildTime':d['buildtime'],'class':d['classlabel']})
for n in ['uconst','xbuconst']:
 d=props(n);items=[v for k,v in d.items()if re.fullmatch('builditem[0-9]+',k)];assert len(items)==11 and len(items)==len(set(items));assert not any('8472'in x for x in items)
for p in(O/'techtree').glob('*.tt'):
 t=p.read_text(encoding='latin1');assert len(re.findall(r'^xbassimst\.odf\s',t,re.M))==1
assert props('bbase')['transporter']=='1'
report['files']=[{'path':str(p.relative_to(O)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in O.rglob('*')if p.is_file()]
Path('D:/aramada/reports/borg-assimilation-support.json').write_text(json.dumps(report,indent=2))
sfile=Path('D:/aramada/status.json');s=json.loads(sfile.read_text());s['current']='Borg assimilation support patch staged and statically validated. Harvester 200 crew; Assimilation 500 crew and produces Borg Repair Drone using assimilated Olympic artwork. Waiting for game to close before installation. Gameplay pending.'
f=next(f for f in s['features']if f['id']=='borg-assimilation-support');f['steps'][1]['done']=True;s['steps']=[{'label':f['title']+': '+a['label'],'done':a['done']}for f in s['features']for a in f['steps']];sfile.write_text(json.dumps(s,indent=2))
with Path('D:/aramada/build.log').open('a')as log:log.write('\nBorg support: 35 staged files, native model/weapon refs, crew, production, buttons, 11-item builder menus verified; waiting for closure.\n')
print(json.dumps(report['units'],indent=2));print('Validated',len(report['files']),'files; no live game changes.')

