from pathlib import Path
exec(Path('D:/aramada/scripts/build-bajor-redesign-v4.py').read_text().split('for name,d in before.items():')[0])
import ast
tree=ast.parse((repo/'scripts/validate-approved-visual-refresh.py').read_text())
for node in tree.body:
 if isinstance(node,ast.FunctionDef)and node.name in ['props','check','modelread']:exec(compile(ast.Module(body=[node],type_ignores=[]),'validation-helpers','exec'))
stage=repo/'patches/array-defense-update-20261025';overlay=stage/'overlay';pack=json.loads((stage/'manifest.json').read_text());P=json.loads((repo/'reports/array-autoattack-before.json').read_text());checks=[];idx={p.stem.lower():p for p in(root/'odf').rglob('*')if p.suffix.lower()=='.odf'};idx.update({p.stem.lower():p for p in(overlay/'odf').rglob('*.odf')});sprite=(root/'Sprites/gui_global.spr').read_text(encoding='latin1')
for r in pack['arrays']:
 n=r['unit'];d=props(idx[n]);old=props(Path(P[n]['file']));m=modelread(root/'SOD'/(d['basename']+'.sod'));nodes={z['id'].lower()for z in m.nodes};check(d['rangescan']=='750'and d['canattack']=='1'and d['combat']=='1',n+': targeting / combat settings')
 banks={int(k[6:]):v for k,v in d.items()if re.fullmatch('weapon[0-9]+',k)};check(sorted(banks)==list(range(1,len(banks)+1)),n+': weapon slots contiguous');check([banks[i]for i in range(1,11)]==['iaautob']*6+['iaautot']*4,n+': six beams / four torpedoes retained')
 for i,w in banks.items():
  check(w in idx,n+': weapon resolves '+w);check(d['weaponhardpoints'+str(i)].lower()in nodes,n+': weapon hardpoint exists')
 for i in range(11,len(banks)):
  if i<r['detectorSlot']:check(d['weapon'+str(i)]==old['weapon'+str(i)],n+': existing special '+str(i)+' unchanged')
 check(d['weapon'+str(r['detectorSlot'])]=='iaacloak',n+': passive cloak detector')
 check(('xbarraywarp'in banks.values())==(n=='xbtarray'),n+': transwarp remains Borg-only')
 for craft in r['newSmallCraft']:check(any(v==craft for k,v in d.items()if re.fullmatch('builditem[0-9]+',k)),n+': small craft in menu '+craft);check(bool(re.search(r'(?mi)^b_'+craft+r'\s',sprite)),n+': small craft icon exists '+craft)
 check(len([k for k in d if re.fullmatch('builditem[0-9]+',k)])<=14,n+': production menu capacity')
 for key in ['maxhealth','shieldrate','maxspecialenergy','specialenergyrate','crewcost','maximumcrew','dilithiumcost','metalcost','latinumcost','biomattercost','buildtime','footprintbuffer','basename']:check(d.get(key)==old.get(key),n+': preserve '+key)
for alias,source in [('iaautob','bb3phas'),('iaautot','bb3phot')]:
 d=props(idx[alias]);old=props(idx[source]);check(float(d['range'])==float(old['range'].rstrip('fF'))*1.25,alias+': range increased exactly 25 percent')
 for key in ['shotdelay','hitchance','ordname','classlabel']:check(d.get(key)==old.get(key),alias+': native weapon '+key+' unchanged')
check(props(idx['iaacloak'])['classlabel']=='detectcloak','Detector uses native class')
for tree in ['tech1','earlytech','fulltech','nosci','nosuper','nospweap']:
 t=(overlay/'techtree'/(tree+'.tt')).read_text(encoding='latin1');check(len(re.findall(r'(?mi)^iaacloak\.odf\s+0\b',t))==1,tree+': built-in detector registered once')
 for r in pack['arrays']:
  for craft in r['newSmallCraft']:
   oldrule=re.search(r'(?mi)^'+craft+r'\.odf[^\r\n]*',(root/'techtree'/(tree+'.tt')).read_text(encoding='latin1'))[0];check(oldrule in t,tree+': existing craft research preserved '+craft)
for r in pack['files']:
 src=root/r['file'];check((not src.exists()if r['sourceHash']is None else hashlib.sha256(src.read_bytes()).hexdigest()==r['sourceHash']),'Live baseline '+r['file']);check(hashlib.sha256((overlay/r['file']).read_bytes()).hexdigest()==r['stagedHash'],'Staged integrity '+r['file'])
result={'status':'PASS','checks':len(checks),'arrays':len(pack['arrays']),'files':len(pack['files']),'runtimeVerified':False};(stage/'validation.json').write_text(json.dumps(result,indent=2));(repo/'reports/array-defense-update-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
