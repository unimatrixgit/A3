from pathlib import Path
import re,json,hashlib
root=Path('D:/armadaIII');repo=Path('D:/aramada');idx={p.name.lower():p for p in(root/'odf').rglob('*.odf')};stage=Path('D:/Xaramada-Modwork/omega-weapon-path-recovery');files=[]
def flatten(p,seen=None):
 seen=set()if seen is None else seen
 assert p.name.lower()not in seen;seen.add(p.name.lower());s=p.read_text(encoding='latin1')
 return re.sub(r'(?mi)^[ \t]*#include[ \t]+"([^"\r\n]+)"[^\r\n]*',lambda m:flatten(idx[m[1].lower()],set(seen)),s)
def props(s):return {k.lower():v.split('//')[0].strip()for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',s)}
for p in(root/'odf/weapons').glob('xow_*.odf'):
 t=p.read_text();inc=re.search(r'(?mi)^#include[ \t]+"([^"\r\n]+)"',t);assert inc
 native=idx[inc[1].lower()];assert native.parent!=p.parent
 rel=native.parent.relative_to(root)/p.name;dest=root/rel;assert not dest.exists()
 full=flatten(p);assert 'classlabel'in props(full)
 out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(full.replace('\r','').replace('\n','\r\n').encode('latin1'))
 assert props(flatten(p))==props(out.read_text(encoding='latin1'))
 files.append({'old':p.relative_to(root).as_posix(),'new':rel.as_posix(),'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'nativeEquivalent':native.name,'shotDelay':props(full).get('shotdelay')})
(repo/'reports/omega-weapon-path-recovery.json').write_text(json.dumps({'stage':str(stage),'target':str(root),'files':files,'applied':False,'effectiveWeaponPropertiesPreserved':True,'runtimeVerified':False},indent=2));print('Prepared',len(files),'Omega weapon definitions in matching native weapon folders; effective properties unchanged')
