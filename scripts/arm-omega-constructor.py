from pathlib import Path
import re,json,datetime,sys,contextlib,io
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils')
from sod_io import SodIO
class R(SodIO):
 def read_unknown_legacy_data(self,s):return [] if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
repo=Path('D:/aramada');backup=Path('D:/Xaramada-Modwork/backups')/('omega-constructor-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));pending=[]
def put(t,k,v):return re.sub(r'(?mi)^[ \t]*'+k+r'[ \t]*=[^\r\n]*','',t)+'\n'+k+' = '+str(v)+'\n'
for root in [Path('D:/ArmadaLab'),Path('D:/armadaIII')]:
 rel=Path('odf/ships/bconst2.odf');t=(root/rel).read_text(encoding='latin1')
 with contextlib.redirect_stdout(io.StringIO()):m=R().read_file(str(root/'SOD/bconst2.sod'))
 nodes={n['id'].lower()for n in m.nodes};assert all('hp'+str(i).zfill(2)in nodes for i in range(1,5))
 old=re.findall(r'(?mi)^\s*buildItem\d+\s*=\s*"([^"]+)"',t)
 t=re.sub(r'(?mi)^[ \t]*weapon(?:Hardpoints)?\d+[ \t]*=[^\r\n]*','',t)
 for k,v in {'unitName':'"Omega Powered Constructor"','tooltip':'"Omega Powered Constructor"','verboseTooltip':'"Omega Powered Constructor. Builds advanced Borg facilities. Armed with three cutting beams and a continuous torpedo launcher; retains Transwarp Drive."','alert':1,'combat':1,'can_sandd':1}.items():t=put(t,k,v)
 for i,(w,hp)in enumerate([('bc1phas','hp01'),('bc1phas','hp02'),('bc1phas','hp03'),('xbhwpr','hp04'),('xabtrans5','hp01')],1):
  t=put(t,'weapon'+str(i),'"'+w+'"');t=put(t,'weaponHardpoints'+str(i),'"'+hp+'"')
 assert re.findall(r'(?mi)^\s*buildItem\d+\s*=\s*"([^"]+)"',t)==old
 pending.append((root,rel,t))
for root,rel,t in pending:
 f=root/rel;b=backup/root.name/rel;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(f.read_bytes());f.chmod(0o666);data=t.replace('\r','').replace('\n','\r\n').encode('latin1');f.write_bytes(data);assert f.read_bytes()==data
 out=repo/('lab/overlay'if root.name=='ArmadaLab'else'bajor/overlay')/rel;out.write_bytes(data)
(repo/'reports/omega-constructor-armament.json').write_text(json.dumps({'backup':str(backup),'name':'Omega Powered Constructor','file':'bconst2.odf','normalWeapons':['bc1phas','bc1phas','bc1phas','xbhwpr'],'retainedSpecial':'xabtrans5','template':'kconst2 combat, alert, can_sandd flags','runtimeVerified':False},indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Omega Powered Constructor renamed and armed in armadaIII and ArmadaLab: 3 Borg beams + continuous Borg torpedo (0.375s), Transwarp retained in slot5. Klingon armed-constructor combat/alert/search-and-destroy flags copied; actual model hardpoints verified. Construction menu, costs and AI references unchanged. Backed up; gameplay pending.';p.write_text(json.dumps(s,indent=2));
with(repo/'build.log').open('a')as log:log.write('\n'+s['current']+'\n')
print(s['current'])
