from pathlib import Path
import re,json,contextlib,io
exec(Path('D:/aramada/scripts/build-bajoran-redesign-v3.py').read_text().split('ROOT=')[0])
r=Path('D:/armadaIII');o=Path('D:/Xaramada-Modwork/borg-nexus-weapons');p=r/'odf/stations/bbase.odf';t=p.read_text(encoding='latin1');old=t
# Replace only weapon arrays, leaving all other unit fields byte-content equivalent.
t=re.sub(r'^[ \t]*weapon(?:Hardpoints)?\d+[ \t]*=[^\r\n]*(?:\r?\n)?','',t,flags=re.M|re.I)
t+='\n// Independent Nexus defense banks; original weapon definitions unchanged.\n'
for i,hp in enumerate(range(9,15),1):t+=f'weapon{i} = "bbpulse"\nweaponHardpoints{i} = "hp{hp:02}"\n'
for i,hp in [(7,9),(8,12)]:t+=f'weapon{i} = "bc1phot"\nweaponHardpoints{i} = "hp{hp:02}"\n'
with contextlib.redirect_stdout(io.StringIO()):m=IO().read_file(str(r/'SOD/bbase.sod'))
anchors={n['id'].lower()for n in m.nodes};assert all('hp'+str(n).zfill(2)in anchors for n in range(9,15));assert len(re.findall(r'^weapon\d+\s*=',t,re.M))==8
strip=lambda s:re.sub(r'^[ \t]*weapon(?:Hardpoints)?\d+[ \t]*=[^\r\n]*(?:\r?\n)?','',s,flags=re.M|re.I).strip()
assert strip(t.split('// Independent Nexus defense banks')[0])==strip(old)
d=o/'odf/stations/bbase.odf';d.parent.mkdir(parents=True,exist_ok=True);d.write_text(t,encoding='latin1')
report={'target':str(r),'file':'odf/stations/bbase.odf','before':{'pulseBanks':1,'torpedoBanks':1,'nominalDamagePerSecond':200},'after':{'pulseBanks':6,'torpedoBanks':2,'nominalDamagePerSecond':600},'note':'Nominal base damage / shot delay only; excludes misses, arcs, target modifiers, upgrades and runtime behavior. No shared weapon or durability/cost changes.','hardpointsValidated':True,'installed':False,'gameplayVerified':False}
Path('D:/aramada/reports/borg-nexus-weapons.json').write_text(json.dumps(report,indent=2))
f=Path('D:/aramada/status.json');s=json.loads(f.read_text(encoding='utf-8-sig'));s['current']='Borg Nexus defense upgrade staged: six independent pulse banks and two torpedo launchers, verified against current model hardpoints. Original weapon damage, costs and durability retained. Awaiting game closure before install.';s['features'].append({'id':'borg-nexus-weapons','title':'Borg Nexus defenses','steps':[{'label':'Compare starbase weapons','done':True},{'label':'Validate eight banks','done':True},{'label':'Install','done':False},{'label':'Gameplay test','done':False}]});s['steps']=[{'label':f['title']+': '+a['label'],'done':a['done']}for f in s['features']for a in f['steps']];f.write_text(json.dumps(s,indent=2),encoding='utf-8');print('Staged one-file patch; eight weapon slots and six model hardpoints verified.')
