from pathlib import Path
import re,shutil,json,datetime,subprocess,hashlib
from PIL import Image,ImageDraw
repo=Path('D:/aramada');r=Path('D:/armadaIII');o=Path('D:/Xaramada-Modwork/borg-station-autofire');o.mkdir(exist_ok=True)
def put(rel,t):
 p=o/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='latin1')
def edit(t,vals):
 for k,v in vals.items():t=re.sub(r'^\s*'+k+r'\s*=.*$', '',t,flags=re.M|re.I)+'\n'+k+' = '+v+'\n'
 return t
for n in ['xbharvbeam','xbassimbeam']:
 rel=Path('odf/special_weapons')/(n+'.odf');t=(r/rel).read_text(encoding='latin1');t=edit(t,{'special':'0','needTarget':'1','targetAlliedCraft':'0','targetAlliedBuildings':'0','targetEnemyCraft':'1','targetEnemyBuildings':'1','restrictFireArc':'0','switchToAttack':'1','shotDelay':'1.0','verboseTooltip':'"Automatically engages enemy targets in range; native assimilation beam."'})
 put(rel,t)
for n in ['xbharvest','xbassimst']:
 rel=Path('odf/stations')/(n+'.odf');t=(r/rel).read_text(encoding='latin1');put(rel,edit(t,{'weaponHardpoints1':'"hp01"','combat':'1','alert':'1','SHOW_SW_AUTONOMY':'1'}))
# Extend the existing model-icon system with compact colored beam badges.
source=Path('D:/Xaramada-Modwork/borg-assimilation-stations/Textures/RGB/xbstatbtn.tga');im=Image.open(source).convert('RGB');draw=ImageDraw.Draw(im)
for x,color in [(0,(30,170,255)),(64,(40,255,65))]:
 draw.rounded_rectangle((x+34,39,x+62,62),radius=4,fill=(5,12,18),outline=color,width=1)
 draw.line((x+38,57,x+58,44),fill=tuple(c//3 for c in color),width=9)
 draw.line((x+38,57,x+58,44),fill=color,width=5)
 draw.line((x+38,57,x+58,44),fill=(210,255,255)if x==0 else(220,255,210),width=1)
 draw.ellipse((x+35,54,x+41,60),fill=color)
p=o/'Textures/RGB/xbstatbtn.tga';p.parent.mkdir(parents=True,exist_ok=True);im.save(p);im.crop((0,0,192,64)).resize((768,256)).save(repo/'borg/artwork/assimilation-stations/beam-badges-preview.png')
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running'
b=Path('D:/Xaramada-Modwork/backups')/('borg-autofire-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));files=[]
for p in o.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(o);dst=r/rel;back=b/rel;back.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,back);shutil.copy2(p,dst);assert p.read_bytes()==dst.read_bytes()
 if p.suffix=='.odf':shutil.copy2(p,repo/'overlay'/rel)
 files.append({'path':str(rel),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
report={'installed':True,'backup':str(b),'files':files,'changes':['Station-only beam special=0; retain native toggleweapon and ordnance behavior.','Enemy-only targeting; single firing hardpoint per station to avoid multiple simultaneous effects.','Brighter model icons with cyan/green beam badges. Native technology dimming unchanged.'],'source':'https://www.armadafleetcommand.com/onscreen/armada/viewtopic.php?t=4380','gameplayVerified':False,'note':'Retains energy usage, boarding crew, capture mechanics and repair drone production. Automatic targeting/capture require in-game verification.'}
(repo/'reports/borg-station-autofire.json').write_text(json.dumps(report,indent=2));f=repo/'status.json';s=json.loads(f.read_text(encoding='utf-8-sig'));s['current']='Installed Borg station automatic enemy-targeting beams and brighter cyan/green beam-badge icons. Five files backed up and verified. Energy and crew costs remain; automatic fire/capture gameplay test pending.';s['features'].append({'id':'borg-station-autofire','title':'Borg station autofire and icons','steps':[{'label':'Configure enemy-only beams','done':True},{'label':'Generate beam badges','done':True},{'label':'Install and verify files','done':True},{'label':'Gameplay test','done':False}]});s['steps']=[{'label':a['title']+': '+v['label'],'done':v['done']}for a in s['features']for v in a['steps']];f.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a')as log:log.write('\nInstalled station autofire and beam-badge icons; five files. Native toggleweapon retained, special=0, one emitting hardpoint, enemy targets only. Runtime pending.\n')
print('Installed and verified',len(files),'files.')
