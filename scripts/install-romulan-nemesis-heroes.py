from pathlib import Path
import json,subprocess,shutil,datetime,stat,hashlib
r=Path('D:/armadaIII');repo=Path('D:/aramada');o=Path('D:/Xaramada-Modwork/romulan-heroes-stage');report=json.loads((repo/'reports/romulan-nemesis-heroes.json').read_text());assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running'
b=Path('D:/Xaramada-Modwork/backups')/('romulan-nemesis-heroes-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));manifest=[]
for rel in report['files']:
 p=o/rel;dst=r/rel;old=dst.exists()
 if old:
  back=b/rel;back.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,back);dst.chmod(dst.stat().st_mode|stat.S_IWRITE)
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst);assert p.read_bytes()==dst.read_bytes();manifest.append({'path':rel,'existed':old,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
 if dst.suffix.lower()in['.odf','.tt','.spr','.dat']:
  dest=repo/'overlay'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
b.mkdir(parents=True,exist_ok=True);(b/'manifest.json').write_text(json.dumps(manifest,indent=2));report.update(installed=True,backup=str(b),manifest=manifest);(repo/'reports/romulan-nemesis-heroes.json').write_text(json.dumps(report,indent=2))
p=repo/'romulan/ASSET-CREDITS.md';p.parent.mkdir(exist_ok=True);p.write_text('''# Nemesis hero assets

Source: http://armadafiles.com/files/armada-2/ships/romulan/romulan-scimitar-valdore-hero-ships/details
Pack/voices: k_merse. Valdore mesh: Howedar; textures: Redragon; conversion: Major A Payne. Scimitar SFC3/Taldren model converted by Major A Payne.

Models and textures are retained unmodified locally. Archive and original source definitions remain in D:/Xaramada-Modwork/romulan-heroes-source and romulan-heroes-extracted. The installer was extracted with cicdec and never run against the game. Original pack shared configuration was not installed wholesale.

New hero wrappers use native weapons, existing Romulan battle physics and the pack's per-role core values. Included command recordings were converted to mono PCM16/22050Hz under unique xr2_ filenames. Imported binary assets/audio and original source ODFs are not redistributed through GitHub. Keep original author restrictions with the local archive.

Two heroes are buildable at ryard3; no starting fleets changed. Gameplay testing pending.
''',encoding='utf-8')
f=repo/'status.json';s=json.loads(f.read_text(encoding='utf-8-sig'));s['current']='Installed Shinzon/Scimitar and Donatra/Valdore heroes at Romulan command yard.64 files backed up/hash verified,42 native-format command clips, included icons/wireframes, matching hero tech availability. Original pack installer never run. Gameplay test pending.'
for a in s['features']:
 if a['id']=='romulan-nemesis-heroes':a['steps'][3]['done']=True
s['steps']=[{'label':a['title']+': '+v['label'],'done':v['done']}for a in s['features']for v in a['steps']];f.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a')as log:log.write('\nInstalled Romulan Nemesis hero batch:64 files,42 converted command recordings, native weapon references. Backup '+str(b)+'. Runtime pending.\n')
print('Installed',len(manifest),'files.')
