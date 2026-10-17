from pathlib import Path
import re,json,hashlib
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
stage=Path('D:/Xaramada-Modwork/cubes-no-blue-beam');files=[];changes=[];before={}
def weapons(d):return [(int(k[6:]),v,d.get('weaponhardpoints'+k[6:],''))for k,v in sorted(d.items(),key=lambda x:int(x[0][6:])if re.fullmatch(r'weapon\d+',x[0])else 999)if re.fullmatch(r'weapon\d+',k)]
for n,p in idx.items():
 if p.parent.name.lower()=='ships':before[n]=weapons(props(n))
for n,oldweapons in before.items():
 p=idx[n];d=props(n);isCube=d.get('race')=='borg'and ('cube'in d.get('unitname','').lower()or p.stem.lower()in ['blocutus','bmama','tcube','xoblocutus'])
 if not isCube:continue
 kept=[(i,v,hp)for i,v,hp in oldweapons if v.lower()not in ['xacassim','gborgbor']]
 if len(kept)==len(oldweapons):continue
 assert all(v and hp for i,v,hp in kept),(n,'Missing existing weapon or hardpoint')
 t=p.read_text(encoding='latin1');t=re.sub(r'(?mi)^[ \t]*weapon(?:hardpoints?)?\d+[ \t]*=[^\r\n]*(?:\r?\n)?','',t)
 t+='\n// Blue auto-assimilation beam removed. Remaining weapon order and hardpoints preserved.\n'
 for j,(i,v,hp)in enumerate(kept,1):t+='weapon'+str(j)+' = "'+v+'"\nweaponHardpoints'+str(j)+' = "'+hp+'"\n'
 rel=p.relative_to(root).as_posix();o=stage/rel;o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));files.append({'path':rel,'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sha256':hashlib.sha256(o.read_bytes()).hexdigest()});changes.append({'unit':n,'before':oldweapons,'after':[(j,v,hp)for j,(i,v,hp)in enumerate(kept,1)]})
# Resolve inheritance against the entire staged cube set, proving no hidden trailing slot survives.
for f in files:idx[Path(f['path']).name.lower()]=stage/f['path']
cache.clear();targets={x['unit']:x for x in changes}
for n,old in before.items():
 new=weapons(props(n))
 if n in targets:
  assert new==targets[n]['after'],(n,new,targets[n]['after'])
  assert [i for i,v,hp in new]==list(range(1,len(new)+1))
  assert not any(v.lower()in ['xacassim','gborgbor']for i,v,hp in new)
 else:assert new==old,('Non-cube weapon change',n)
r={'target':str(root),'stage':str(stage),'files':files,'changes':changes,'applied':False,'runtimeVerified':False,'greenBeamPreserved':True,'remainingRelativeOrderPreserved':True,'matchingHardpointsPreserved':True,'specialButtonHotkeysUnchanged':True,'nonCubeWeaponsUnchanged':True};(repo/'reports/cubes-no-blue-beam.json').write_text(json.dumps(r,indent=2));print(json.dumps({'cubes':len(files),'weaponsPerCube':[len(x['after'])for x in changes],'nonCubeWeaponsUnchanged':True,'inheritanceVerified':True}))
