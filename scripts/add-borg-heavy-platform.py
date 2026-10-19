from pathlib import Path
import re,json,datetime,sys,contextlib,io
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils')
from sod_io import SodIO
class Reader(SodIO):
 def read_unknown_legacy_data(self,s):return [] if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
repo=Path('D:/aramada');backup=Path('D:/Xaramada-Modwork/backups')/('borg-heavy-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));pending=[]
def put(t,k,v):return re.sub(r'(?mi)^[ \t]*'+k+r'[ \t]*=[^\r\n]*','',t)+'\n'+k+' = '+str(v)+'\n'
for root in [Path('D:/ArmadaLab'),Path('D:/armadaIII')]:
 t=(root/'odf/stations/bturret2.odf').read_text(encoding='latin1')
 with contextlib.redirect_stdout(io.StringIO()):model=Reader().read_file(str(root/'SOD/xvstock_bturret2.sod'))
 nodes={n['id'].lower()for n in model.nodes};assert all('hp'+str(i).zfill(2)in nodes for i in range(1,5))
 t=re.sub(r'(?mi)^[ \t]*weapon(?:Hardpoints)?\d+[ \t]*=[^\r\n]*','',t)
 values={'unitName':'"Oblivion Defense Nexus"','tooltip':'"Oblivion Defense Nexus"','verboseTooltip':'"Borg heavy defense platform. Three beam banks, two torpedo banks and one rapid-fire torpedo launcher."','ScaleSOD':'1.35','maxHealth':5250,'shieldRate':6.8,'weaponsHitPoints':1000,'crewCost':200,'maximumCrew':200,'dilithiumCost':900,'metalCost':900,'officerCost':8,'buildTime':90}
 for k,v in values.items():t=put(t,k,v)
 for i,w in enumerate(['xp6b']*3+['xp6t']*2+['xbhwpr'],1):
  t=put(t,'weapon'+str(i),'"'+w+'"');t=put(t,'weaponHardpoints'+str(i),'"hp'+str((i-1)%4+1).zfill(2)+'"')
 pending.append((root,Path('odf/stations/bhwp.odf'),t))
 w=(root/'odf/weapons/Photons/xp6t.odf').read_text(encoding='latin1')
 for k,v in {'shotDelay':'0.375','maxShots':'1','minimumShotInterval':'0.375','saveFire':'0','wpnName':'"Rapid-fire Borg Torpedo"'}.items():w=put(w,k,v)
 pending.append((root,Path('odf/weapons/Photons/xbhwpr.odf'),w))
 rel=Path('odf/ships/bconst2.odf');c=(root/rel).read_text(encoding='latin1');assert not re.search(r'(?mi)^buildItem6\s*=',c);c+='\nbuildItem6 = "bhwp"\n';pending.append((root,rel,c))
 for name in ['tech1','earlytech','fulltech','nosci','nosuper','nospweap']:
  rel=Path('techtree')/(name+'.tt');c=(root/rel).read_text(encoding='latin1');c=re.sub(r'(?mi)^bhwp\.odf[^\r\n]*','',c)+'\nbhwp.odf 0 // Oblivion Defense Nexus: unlocked\n';pending.append((root,rel,c))
 rel=Path('Sprites/gui_global.spr');c=(root/rel).read_text(encoding='latin1')
 for original,alias in [('b_bturret2','b_bhwp')]+[('bturret2w'+str(i),'bhwpw'+str(i))for i in range(1,6)]:
  m=re.search(r'(?mi)^'+original+r'[ \t]+[^\r\n]*',c);assert m
  if not re.search(r'(?mi)^'+alias+r'[ \t]',c):c=c[:m.end()]+'\n'+re.sub('^'+original,alias,m[0])+c[m.end():]
 pending.append((root,rel,c))
for root,rel,t in pending:
 f=root/rel
 if f.exists():
  b=backup/root.name/rel;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(f.read_bytes());f.chmod(0o666)
 data=t.replace('\r','').replace('\n','\r\n').encode('latin1');f.write_bytes(data);assert f.read_bytes()==data
 out=repo/('lab/overlay'if root.name=='ArmadaLab'else'bajor/overlay')/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
(repo/'reports/borg-heavy-platform.json').write_text(json.dumps({'unit':'bhwp','name':'Oblivion Defense Nexus','backup':str(backup),'stats':values,'constructor':'bconst2','slot':6,'runtimeVerified':False},indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Oblivion Defense Nexus installed in ArmadaLab and armadaIII. Borg heavy platform: 5250 health, 6.8 shield regeneration, 200 crew/max, 900 dilithium + 900 metal, 8 officers, 90s. 3 Borg beams + 2 torpedo banks + rapid torpedo. bconst2 slot6, unlocked in six skirmish tech trees, Borg model/icon/wireframes retained. Backed up and file-checked; gameplay pending.';p.write_text(json.dumps(s,indent=2));
with(repo/'build.log').open('a')as log:log.write('\n'+s['current']+'\n')
print(s['current'])
