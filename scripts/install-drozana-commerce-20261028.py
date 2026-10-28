"""Install the validated Drozana package only after Armada III is closed."""
from pathlib import Path
import json,hashlib,datetime,shutil,subprocess
repo=Path('D:/aramada');root=Path('D:/armadaIII');stage=repo/'patches/drozana-commerce-20261028';O=stage/'overlay';manifest=json.loads((stage/'manifest.json').read_text());validation=json.loads((stage/'validation.json').read_text());native=json.loads((stage/'ferengi-handling-native-validation.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert subprocess.check_output(['powershell','-NoProfile','-Command','@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'],text=True).strip()=='0','Armada III must be closed.'
assert validation['status']=='PASS'and native['emulatedTests']==64
for rel,digest in manifest['files'].items():assert sha(O/rel)==digest,('Staged file changed',rel)
for rel,digest in manifest['sourceHashes'].items():assert sha(root/rel)==digest,('Installed source changed',rel)
candidate=stage/'engine-candidate/Armada2.exe';exe=root/'Armada2.exe';assert sha(exe)==native['sourceSha256']and sha(candidate)==native['candidateSha256']
backup=Path('D:/Xaramada-Modwork/backups')/('drozana-installed-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));files=[]
for rel in list(manifest['files'])+['Armada2.exe']:
 p=root/rel
 if p.exists():b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b)
for rel in manifest['files']:
 p=root/rel;p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():p.chmod(0o666)
 shutil.copy2(O/rel,p);assert sha(p)==manifest['files'][rel];out=repo/'bajor/overlay'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out);files.append(rel)
exe.chmod(0o666);shutil.copy2(candidate,exe);assert sha(exe)==native['candidateSha256']
manifest['status']='INSTALLED_GAMEPLAY_PENDING';manifest['backup']=str(backup);manifest['runtimeVerified']=False;manifest['installedFiles']=len(files)+1;(stage/'manifest.json').write_text(json.dumps(manifest,indent=2));(repo/'reports/drozana-installed-20261028.json').write_text(json.dumps({'target':str(root),'backup':str(backup),'files':files+['Armada2.exe'],'nativeHandlingTests':64,'exeSha256':sha(exe),'runtimeVerified':False},indent=2))
notes='''# Drozana commerce package — 28 October 2026

Installed only in D:/armadaIII; original Xaramada and ArmadaLab untouched.

- Drozana Commerce Exchange: original K7-family-inspired station model, Ferengi-operated trading facility. Built by xfgconst after xfgmerc.
- Assimilated Drozana Foundry: Borg-only xbgconst construction option, requires xbgmerc and byard2. Nine combat conversions: Federation, Klingon, Romulan, Cardassian, Dominion, Borg, Bajoran, Breen and Ferengi. No Species 8472. These are craft/CraftProcess attack vessels, never cargo ships.
- Each conversion retains its source faction freighter hull with added Borg machinery, two beams, one torpedo, blue Auto-Assimilator, Transwarp and sphere Regeneration. Existing borpod1/3/4 research still governs those abilities.
- 3,000 special energy, 85/s regeneration: three-ability capacity baseline and sustain budget with 20% headroom. Sustained-use assumptions: blue beam50/s, regeneration80/30s, transwarp1000/60s.
- Standard trade cargo values doubled at their original definitions. No ship-specific 3x bonus, per the user's uniform2x choice. Station commission unchanged.
- Player-buildable Ferengi trade ship xfgtrade capacity1000, twice native500. This replaces its previous modded1500 setting.
- Native per-ship handling patch doubles only xfgtrade LoadCargo/UnloadCargo transfer amounts. ODF name matching is case-insensitive with optional directory and .odf extension; other ships and station-wide handling rates unchanged. 64 x86-emulated selector, transfer, register, flags and stack tests passed; real game testing pending.
- Engine patch detours: LoadCargo0x4ae1c0, UnloadCargo0x4ae440; name lookup via existing GameObjectClass::GetOdfName0x4ce370. New .fgdock code section; original routine addresses preserved. The installed original executable is backed up. Full executable is not committed: the generator recreates it from the verified local base binary.

Design references: [Drozana Station, STO Wiki](https://sto.fandom.com/wiki/Drozana_Station), [official STO Drozana lore reference](https://www.playstartrekonline.com/en/news/article/11084713). New station geometry and Borg fittings were authored locally; no STO model was extracted. Hulls/textures use the installation's existing faction assets; source freighter ODFs are recorded in manifest.json.

Visual/model/reference/technology checks and native hook emulation passed. Installation hashes verified. No gameplay success is claimed until tested.
''';(stage/'CHANGELOG.md').write_text(notes,encoding='utf-8')
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Drozana package installed in armadaIII: two new stations, nine Borg-only assimilated combat freighters, doubled native trade cargo values, Ferengi trade ship capacity1000 and ship-only2x load/unload engine hook. 11 models/ref chains and64 emulated native cases passed;47 installed files hash verified. Backups retained; gameplay pending.';p.write_text(json.dumps(s,indent=2))
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n'+datetime.datetime.now().isoformat()+' '+s['current']+'\n')
p=repo/'TRANSFER-HANDOFF.md';t=p.read_text(encoding='utf-8-sig');p.write_text('# Latest — Drozana commerce installed 28 October 2026\n\n'+s['current']+'\nBackup: '+str(backup)+'\nThe executable now has a name-scoped Ferengi cargo speed hook (.fgdock). Generator/64-case emulation: scripts/stage-ferengi-transfer-hook-20261028.py. Two native entry detours0x4ae1c0 and0x4ae440; current engine original source hash is in patches/drozana-commerce-20261028/ferengi-handling-native-validation.json. Do not rerun unguarded doubling/size scripts. Test trading, foundry production and each new attack ship.\n\n'+t,encoding='utf-8')
print(json.dumps({'installedFiles':len(files)+1,'backup':str(backup),'runtimeVerified':False}))
