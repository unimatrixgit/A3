from pathlib import Path
exec(Path('D:/aramada/scripts/build-bajor-redesign-v4.py').read_text().split('for name,d in before.items():')[0])
import ast
tree=ast.parse((repo/'scripts/validate-approved-visual-refresh.py').read_text())
for node in tree.body:
 if isinstance(node,ast.FunctionDef)and node.name in ['props','check','modelread']:exec(compile(ast.Module(body=[node],type_ignores=[]),'validation-helpers','exec'))
stage=Path('D:/Xaramada-Modwork/resource-science-redesign-stage');overlay=stage/'overlay';pack=json.loads((stage/'manifest.json').read_text());P=json.loads((repo/'reports/resource-science-all-before.json').read_text());checks=[]
idx={p.stem.lower():p for p in(root/'odf').rglob('*')if p.suffix.lower()=='.odf'};idx.update({p.stem.lower():p for p in(overlay/'odf').rglob('*.odf')});sprite=(overlay/'Sprites/gui_global.spr').read_text(encoding='latin1');podtotal=0;researchcount=0
for row in pack['units']:
 n=row['unit'];d=props(idx[n]);previous=props(Path(P[n]['file']));expected=dict(previous)
 for key,value in previous.items():
  if key.endswith('hardpoints')and'='in value:expected[key]=value.rsplit('=',1)[-1].strip().strip('"')
 diffs={k:(expected.get(k),d.get(k))for k in set(expected)|set(d)if k!='basename'and expected.get(k)!=d.get(k)};check(not diffs,n+': gameplay / menus unchanged '+str(diffs))
 m=modelread(overlay/'SOD'/(row['model']+'.sod'));old=modelread(root/'SOD'/((P[n].get('basename')or n)+'.sod'));names={z['id'].lower()for z in m.nodes}
 check({z['id']for z in old.nodes}.issubset({z['id']for z in m.nodes}),n+': source nodes preserved');check(len(old.animation_transforms)==len(m.animation_transforms),n+': animation channels retained')
 for node in m.nodes:
  if node['type']!='MESH':continue
  data=node['data'];v=data['vertices'];uv=data['texture_coordinates'];check(len(v)<=450,n+': conservative draw mesh');check(np.isfinite(v).all()and np.isfinite(uv).all(),n+': finite model geometry')
  if m.version>1.9101:check(data['bump_map']==1,n+': native diffuse texture flag')
  tex=overlay/'Textures/RGB'/(data['texture']+'.tga');check(tex.is_file(),n+': model texture exists');im=Image.open(tex);check(im.size==(256,256)and im.mode=='RGB',n+': 256px RGB model texture')
  for g in data['vertex_lighting_groups']:check(all(len(face)==3 and all(0<=vi<len(v)and 0<=ui<len(uv)for vi,ui in face)for face in g['faces']),n+': valid geometry / texture indices')
 for key,value in d.items():
  if re.fullmatch('weapon[0-9]+',key):check(value.lower()in idx,n+': unchanged weapon resolves '+value)
  if re.fullmatch('weaponhardpoints[0-9]+',key)or key.endswith('targethardpoints')or key in ['buildhardpoint','repairhardpoint','dockinghardpoint','podhardpoints','workerbeehardpoints']:
   for hp in re.findall('[A-Za-z0-9_]+',value):check(hp.lower()in names,n+': node exists '+hp)
  if re.fullmatch('(secondary)?builditem[0-9]+',key):check(value.lower()in idx,n+': research / production target exists '+value)
 if previous['classlabel']=='research':
  researchcount+=1;check(d.get('podhardpoints')==previous.get('podhardpoints'),n+': all original pod slots retained');check(len(row['podMounts'])==len(row['pods']),n+': every pod has a visible geometry mount');podtotal+=len(row['pods']);positions=[tuple(round(v,3)for v in p['position'])for p in row['podMounts']];check(len(set(positions))==len(positions),n+': pod mounts are separate')
 for key in ['b_'+n,'b_'+row['model']]+[p+'w'+str(i)for p in [n,row['model']]for i in range(1,6)]:
  matches=re.findall(r'(?mi)^'+re.escape(key)+r'[ \t]+([^\r\n]+)',sprite);check(len(matches)==1,n+': unique GUI sprite '+key);fields=matches[0].split();tex=overlay/'Textures/RGB'/(fields[0]+'.tga');check(tex.is_file(),n+': GUI texture present');im=Image.open(tex);check(im.size==(64,64)and im.mode=='RGB',n+': full-image RGB icon / portrait')
row=next(r for r in pack['units']if r['unit']=='xbassimst');d=props(idx['xbassimst']);check(d['builditem0']=='xbrepair'and d['buildhardpoint']==props(Path(P['xbassimst']['file']))['buildhardpoint'],'Assimilation Station: repair-drone production kept')
check(researchcount==34,'All 34 research facilities covered, including upgrade centres and Omega labs');check(all(n in [r['unit']for r in pack['units']]for n in ['xfomegalab','xbomegalab','fupgrade','bupgrade','kupgrade','rupgrade','cupgrade','dupgrade','bjupgrade']),'Upgrade centres and Omega labs explicitly present')
for row in pack.get('orbitalResize',[]):
 n=row['unit'];d=props(idx[n]);old=props(Path(P[n]['file']));allowed={k.lower()for k in row['scaledFields']};check(all(d.get(k)==old.get(k)for k in set(d)|set(old)if k not in allowed),n+': orbital gameplay unchanged')
 if row['borgMatchedToFederation']:check(abs(row['visualSpan']-pack['orbitalTargetSpan'])<.001,n+': Borg matches enlarged Federation orbital')
 else:check(abs(row['factor']-1.2)<.000001,n+': orbital enlarged 20 percent')
for rel,h in pack['files'].items():check(hashlib.sha256((overlay/rel).read_bytes()).hexdigest()==h,'staged integrity '+rel)
for rel,h in pack['sourceHashes'].items():check(hashlib.sha256((root/rel).read_bytes()).hexdigest()==h,'live baseline unchanged '+rel)
check(not any(rel.lower().startswith(('techtree/','ai/'))for rel in pack['files']),'No tech tree / AI / research effect changes')
result={'status':'PASS','checks':len(checks),'models':len(pack['units']),'researchFacilities':researchcount,'researchPodMounts':podtotal,'files':len(pack['files']),'runtimeVerified':False,'details':checks};(stage/'validation.json').write_text(json.dumps(result,indent=2));(repo/'reports/resource-science-redesign-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items()if k!='details'}))
