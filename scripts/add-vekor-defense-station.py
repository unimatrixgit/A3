from pathlib import Path
import re,json,datetime,sys,contextlib,io
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils')
from sod_io import SodIO
class Reader(SodIO):
 def read_unknown_legacy_data(self,s):return [] if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
repo=Path('D:/aramada');stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup=Path('D:/Xaramada-Modwork/backups')/('vekor-defense-'+stamp)
def props(t):return {k.lower():v.strip() for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t)}
def put(t,k,v):return re.sub(r'(?mi)^[ \t]*'+k+r'[ \t]*=[^\r\n]*','',t)+'\n'+k+' = '+str(v)+'\n'
pending=[];records=[]
for root in [Path('D:/ArmadaLab'),Path('D:/armadaIII')]:
 t=(root/'odf/stations/cstation.odf').read_text(encoding='latin1')
 with contextlib.redirect_stdout(io.StringIO()):model=Reader().read_file(str(root/'SOD/cstation.sod'))
 nodes={n['id'].lower()for n in model.nodes}
 t=re.sub(r'(?mi)^[ \t]*(?:buildItem\d+|weapon(?:Hardpoints)?\d+|buildHardpoint|repairHardpoint)[ \t]*=[^\r\n]*','',t)
 heavy=props((root/'odf/stations/khwp.odf').read_text(encoding='latin1'))
 values={'unitName':'"Vekor-class Defense Station"','tooltip':'"Vekor-class Defense Station"','verboseTooltip':'"Compact Cardassian heavy defense station. Three beam banks, two torpedo banks and a rapid-fire torpedo launcher."','baseName':'"cstation"','ScaleSOD':'0.65','crewCost':200,'maximumCrew':200,'dilithiumCost':900,'metalCost':900,'latinumCost':0,'biomatterCost':0,'officerCost':8,'buildTime':90,'maxHealth':heavy['maxhealth'],'shieldRate':heavy['shieldrate'],'shieldProtection':'1.0','officerGain':0,'builder_ship':0,'repairFacility':0,'combat':1,'alert':1,'possibleCraftNames':'"Vekor" "Gul Vornar" "Korinas"'}
 for k in ['shieldGeneratorHitPoints','enginesHitPoints','weaponsHitPoints','lifeSupportHitPoints','sensorsHitPoints']:
  if k.lower() in heavy:values[k]=heavy[k.lower()]
 for k,v in values.items():t=put(t,k,v)
 weapons=['xp4b']*3+['xp4t']*2+['xp4r']
 for i,w in enumerate(weapons,1):
  hp='hp'+str(i+8).zfill(2);assert hp in nodes;t=put(t,'weapon'+str(i),'"'+w+'"');t=put(t,'weaponHardpoints'+str(i),'"'+hp+'"')
 pending.append((root,Path('odf/stations/chwp.odf'),t))
 for name in ['cconst','domconst']:
  rel=Path('odf/ships')/(name+'.odf');c=(root/rel).read_text(encoding='latin1');v=props(c);slots=[int(k[9:])for k in v if re.fullmatch('builditem[0-9]+',k)]
  if not any(x.strip('"').lower()=='chwp' for k,x in v.items()if k.startswith('builditem')):c+='\nbuildItem'+str(max(slots)+1)+' = "chwp"\n'
  pending.append((root,rel,c))
 for name in ['tech1','earlytech','fulltech','nosci','nosuper','nospweap']:
  rel=Path('techtree')/(name+'.tt');c=(root/rel).read_text(encoding='latin1');c=re.sub(r'(?mi)^chwp\.odf[^\r\n]*','',c);c+='\nchwp.odf 0 // Vekor-class Defense Station: unlocked\n';pending.append((root,rel,c))
 rel=Path('Sprites/gui_global.spr');c=(root/rel).read_text(encoding='latin1')
 # Copy sprite aliases in place to retain their original texture-size context.
 for original,alias in [('b_cstation','b_chwp')]+[('cstationw'+str(i),'chwpw'+str(i))for i in range(1,6)]:
  matches=list(re.finditer(r'(?mi)^'+original+r'[ \t]+[^\r\n]*',c));assert matches,original
  if not re.search(r'(?mi)^'+alias+r'[ \t]',c):
   m=matches[0];c=c[:m.end()]+'\n'+re.sub('^'+original,alias,m[0])+c[m.end():]
 pending.append((root,rel,c));records.append({'root':str(root),'stats':values,'weapons':weapons,'constructors':['cconst','domconst'],'unlocked':True})
for root,rel,t in pending:
 f=root/rel
 if f.exists():
  b=backup/root.name/rel;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(f.read_bytes());f.chmod(0o666)
 data=t.replace('\r','').replace('\n','\r\n').encode('latin1');f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
 out=repo/('lab/overlay'if root.name=='ArmadaLab'else'bajor/overlay')/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
 assert f.read_bytes()==data
(repo/'reports/vekor-defense-station.json').write_text(json.dumps({'backup':str(backup),'records':records,'runtimeVerified':False},indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Vekor-class Defense Station installed in Lab and armadaIII: compact Nor model, 5250 health, 6.8 shield regeneration, 200 crew/max, 900 dilithium + 900 metal, 8 officers, 90 seconds. 3 beams + 2 torpedoes + rapid torpedo; unlocked for cconst and domconst in 6 skirmish tech trees. Existing Nor icon and wireframes aliased. Backed up; gameplay pending.';p.write_text(json.dumps(s,indent=2));
with(repo/'build.log').open('a')as log:log.write('\n'+s['current']+'\n')
print(json.dumps({'files':len(pending),'backup':str(backup),'status':s['current']}))
