from pathlib import Path
import json,re,hashlib,datetime,subprocess,collections
repo=Path('D:/aramada');root=Path('D:/armadaIII')
stage=repo/'patches/armadafiles-yards-20261031';overlay=stage/'overlay'
manifest=json.loads((stage/'manifest.json').read_text())
assert subprocess.check_output(['powershell','-NoProfile','-Command','@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'],text=True).strip()=='0'
assert hashlib.sha256((root/'Sprites/gui_global.spr').read_bytes()).hexdigest()==manifest['sourceSpriteSha256']
sprite=(overlay/'Sprites/gui_global.spr').read_text(encoding='latin1')
def props(text):
 return {k.lower():v.split('//')[0].strip() for k,v in re.findall(r'(?mi)^\s*(\w+)\s*=\s*([^\r\n]*)',text)}
for row in manifest['units']:
 current=root/row['odf'];assert hashlib.sha256(current.read_bytes()).hexdigest()==row['oldOdfSha256']
 a=props(current.read_text(encoding='latin1'));b=props((overlay/row['odf']).read_text(encoding='latin1'))
 assert {k for k in a.keys()|b.keys() if a.get(k)!=b.get(k)}<={'basename','scalesod'}
 for alias in row['spriteAliases']:assert len(re.findall(r'(?mi)^'+re.escape(alias)+r'[ \t]+',sprite))==1
repairnames=['fremmeler','mysyard']+['xyr_'+n for n in ['f','b','k','r','c','d','bj','br','fg','bg']]
repairs={n:hashlib.sha256((root/'odf/stations'/(n+'.odf')).read_bytes()).hexdigest() for n in repairnames}
backup=Path('D:/Xaramada-Modwork/backups')/('armadafiles-yards-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
files=[]
for source in overlay.rglob('*'):
 if not source.is_file():continue
 rel=source.relative_to(overlay)
 assert rel.parts[0] in ['SOD','odf','Textures','Sprites']
 target=root/rel
 if target.exists():
  saved=backup/rel;saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(target.read_bytes());target.chmod(0o666)
 target.parent.mkdir(parents=True,exist_ok=True);data=source.read_bytes();target.write_bytes(data)
 mirror=repo/'bajor/overlay'/rel;mirror.parent.mkdir(parents=True,exist_ok=True)
 if mirror.exists():mirror.chmod(0o666)
 mirror.write_bytes(data);assert target.read_bytes()==mirror.read_bytes();files.append(rel.as_posix())
for n,sha in repairs.items():assert hashlib.sha256((root/'odf/stations'/(n+'.odf')).read_bytes()).hexdigest()==sha
report={'backup':str(backup),'units':len(manifest['units']),'races':dict(collections.Counter(r['race'] for r in manifest['units'])),'installedFiles':files,'repairDockHashesUnchanged':repairs,'runtimeVerified':False,'validation':['55 single-source models','660 unique GUI aliases','Only model reference and visual scale changed in unit properties','All live/source copies verified','12 dedicated repair docks unchanged']}
(repo/'reports/armadafiles-yards-installed-20261031.json').write_text(json.dumps(report,indent=2)+'\n')
p=repo/'status.json';status=json.loads(p.read_text());status['current']='ArmadaFiles package installed:55 production yards across all factions, complete downloaded hulls with matching build/group icons. No merged models;12 dedicated repair docks unchanged. File checks passed; gameplay and docking tests pending.';p.write_text(json.dumps(status,indent=2)+'\n')
with (repo/'build.log').open('a') as out:out.write('\n'+datetime.datetime.now().isoformat()+' '+status['current']+'\n')
print(status['current']);print('Backup',backup,'files',len(files))
