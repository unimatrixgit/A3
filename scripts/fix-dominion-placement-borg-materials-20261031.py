from pathlib import Path
exec(Path('scripts/stage-armadafiles-yards-20261031.py').read_text().split('targets=[]')[0])
import datetime,subprocess
manifest=json.loads((stage/'manifest.json').read_text());backup=Path('D:/Xaramada-Modwork/backups')/('dominion-placement-borg-materials-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));pending={};borg=[];dom=[]
for row in manifest['units']:
 if row['race']!='borg':continue
 p=root/row['model'];m=load(p);before=copy.deepcopy(m.nodes);oldanim=copy.deepcopy(m._animation_transforms)
 for material in m.materials:
  glow=any(k in material['name'].lower()for k in['glow','green','light'])
  material['ambient_color']=[.04,.32,.06]if glow else[.07,.17,.085]
  material['diffuse_color']=[.18,1.0,.24]if glow else[.52,.72,.56]
  material['specular_color']=[.1,.65,.15]if glow else[.16,.3,.19]
  material['specular_shininess']=32.0
 # Keep the node graph, vertices, UVs, textures and hardpoints byte-for-byte in the parsed structure.
 out=repo/'patches/borg-yard-materials-20261031'/row['model'];out.parent.mkdir(parents=True,exist_ok=True);w=IO();w.curr_sod_version=m.version
 with contextlib.redirect_stdout(io.StringIO()):w.write_file(m,str(out))
 check=load(out);assert check.nodes==before;assert check._animation_transforms==oldanim
 pending[row['model']]=out.read_bytes();borg.append({'unit':row['unit'],'model':row['model'],'materialsChanged':len(m.materials),'geometryUVsTexturesAnchorsUnchanged':True})
for n in ['dyard','dyard2','dyard3']:
 p=idx[n];t=p.read_text(encoding='latin1');before={'footprintBuffer':cache[n].get('footprintbuffer'),'avoidanceClass':cache[n].get('avoidanceclass')}
 for key,value in [('footprintBuffer',25),('avoidanceClass',1000)]:
  pat=r'(?mi)^(\s*'+key+r'\s*=\s*)[^\r\n]*'
  if re.search(pat,t):t=re.sub(pat,lambda m:m[1]+str(value),t)
  else:t+='\r\n'+key+' = '+str(value)+'\r\n'
 rel=p.relative_to(root).as_posix();pending[rel]=t.encode('latin1');dom.append({'unit':n,'before':before,'after':{'footprintBuffer':25,'avoidanceClass':1000}})
assert subprocess.check_output(['powershell','-NoProfile','-Command','@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'],text=True).strip()=='0','Game must be closed'
for rel,data in pending.items():
 p=root/rel;b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(p.read_bytes());p.chmod(0o666);p.write_bytes(data);out=repo/'bajor/overlay'/rel;out.parent.mkdir(parents=True,exist_ok=True)
 if out.exists():out.chmod(0o666)
 out.write_bytes(data);assert p.read_bytes()==out.read_bytes()
r={'backup':str(backup),'borgYards':borg,'dominionPlacement':dom,'installedFiles':list(pending),'runtimeVerified':False,'limitations':'Dominion constructors build a refinery, so AI execution is active. Yard placement settings normalized to working Federation yard values. Runtime blockage cause remains unconfirmed; fresh-match retest required. Borg changes are material coefficients only; original meshes, UVs, texture references and all node transforms verified unchanged.'};(repo/'reports/dominion-placement-borg-materials-20261031.json').write_text(json.dumps(r,indent=2)+'\n')
p=repo/'status.json';d=json.loads(p.read_text());d['current']=f'Dominion yard placement recovery installed:3 yards normalized to25 footprint buffer /1000 avoidance class, matching Federation settings; yard-first AI retained. Borg{len(borg)} production-yard materials darkened/tinted green with geometry/UVs/textures unchanged. File checks pass; runtime tests pending.';p.write_text(json.dumps(d,indent=2)+'\n')
with(repo/'build.log').open('a')as f:f.write('\n'+datetime.datetime.now().isoformat()+' '+d['current']+'\n')
subprocess.run(['git','add','-f','--',*['bajor/overlay/'+r for r in pending],'reports/dominion-placement-borg-materials-20261031.json','scripts/fix-dominion-placement-borg-materials-20261031.py','status.json','build.log'],check=True);print(d['current'])
