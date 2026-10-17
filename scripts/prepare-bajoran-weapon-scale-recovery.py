from pathlib import Path
import re,json,hashlib
root=Path('D:/armadaIII');stage=Path('D:/Xaramada-Modwork/bajor-weapon-scale-recovery');idx={p.name.lower():p for p in (root/'odf').rglob('*.odf')};files=[];changes=[]
def save(rel,data):
 p=root/rel;o=stage/rel;o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes(data.replace('\r','').replace('\n','\r\n').encode('latin1'));files.append({'path':rel,'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None,'sha256':hashlib.sha256(o.read_bytes()).hexdigest()})
def flatten(p,seen=None):
 seen=set()if seen is None else seen
 assert p.name.lower()not in seen;seen.add(p.name.lower());s=p.read_text(encoding='latin1')
 return re.sub(r'(?mi)^[ \t]*#include[ \t]+"([^"\r\n]+)"[^\r\n]*',lambda m:flatten(idx[m[1].lower()],set(seen)),s)
for p in (root/'odf/weapons').glob('xbj_*.odf'):
 t=p.read_text();m=re.fullmatch(r'\s*#include\s+"([^"]+)"\s*',t)
 if not m:continue
 native=idx[m[1].lower()];full=flatten(native);assert re.search(r'(?mi)^classLabel[ \t]*=',full),p.name
 save('odf/weapons/'+p.name,'// Standalone native weapon definition; Bajoran tech identity retained.\n'+full);changes.append({'weapon':p.stem,'native':native.name,'includesFlattened':True})
for p in (root/'odf/ships').glob('bj*.odf'):
 t=p.read_text(encoding='latin1');m=re.search(r'(?mi)^ScaleSOD[ \t]*=[ \t]*([\d.]+)',t)
 if not m:continue
 old=float(m[1]);factor=.55 if p.stem=='bjfreight'else 1.0 if p.stem=='bjnerys'else 1.6
 if factor==1:continue
 new=round(old*factor,4);t=re.sub(r'(?mi)^ScaleSOD[ \t]*=[^\r\n]*','ScaleSOD = '+str(new),t)
 if p.stem=='bjfreight':t+='\nphysicsFile = "bjfreightphys.odf"\n'
 save('odf/ships/'+p.name,t);changes.append({'ship':p.stem,'scaleBefore':old,'scaleAfter':new})
p=idx['sconstphys.odf'];t=p.read_text(encoding='latin1')
for key,value in {'combatSpeed':'37.5','impulseSpeed':'75','forwardAccel':'1.3','turnOmega':'1.0','turnAlpha':'1.0'}.items():
 t,n=re.subn(r'(?mi)^'+key+r'[ \t]*=[^\r\n]*',key+' = '+value,t);assert n==1,key
save('odf/other/bjfreightphys.odf',t)
report={'stage':str(stage),'files':files,'changes':changes,'applied':False,'runtimeVerified':False,'note':'Flattened standalone weapon definitions preserve Bajor research IDs. Combat ship scale +60%, Kira previous correction retained, resource freighter scale -45%, impulse/combat speed +50%; separate faction physics.'}
Path('D:/aramada/reports/bajoran-weapon-scale-recovery.json').write_text(json.dumps(report,indent=2));print('Prepared',len(files),'files;',len([c for c in changes if 'weapon'in c]),'standalone weapons')
