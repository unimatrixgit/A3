from pathlib import Path
exec(Path('D:/aramada/scripts/build-bajor-redesign-v4.py').read_text().split('for name,d in before.items():')[0])
import ast
tree=ast.parse((repo/'scripts/stage-approved-visual-refresh.py').read_text())
for node in tree.body:
 if isinstance(node,ast.FunctionDef)and node.name in ['visible_points','load_model']:exec(compile(ast.Module(body=[node],type_ignores=[]),'model-helpers','exec'))
stage=Path('D:/Xaramada-Modwork/resource-science-redesign-stage');overlay=stage/'overlay';pack=json.loads((stage/'manifest.json').read_text());P=json.loads((repo/'reports/resource-science-all-before.json').read_text());repairs=[]
for file in(overlay/'odf').rglob('*.odf'):
 t=file.read_text(encoding='latin1');fixed=re.sub(r'(?mi)^([ \t]*[A-Za-z0-9_]*hardpoints?[ \t]*=[ \t]*)(?:[A-Za-z0-9_]+[ \t]*=[ \t]*)+("[^\r\n]*)$',r'\1\2',t)
 if fixed!=t:file.write_bytes(fixed.replace('\r','').replace('\n','\r\n').encode('latin1'));repairs.append(file.relative_to(overlay).as_posix())
orbitals=['forbital','bbase2','borbital','korbital','rorbital','corbital','dorbital','bjorbital','brorbital','xfgmetal2','xfgmetal3','xbgmetal2','xbgmetal3']
def num(v):return float(str(v).rstrip('fF'))
def span(n):
 d=P[n];return np.ptp(visible_points(load_model(root/'SOD'/((d.get('basename')or n)+'.sod'))),axis=0).max()
target=span('forbital')*num(P['forbital'].get('scalesod',1))*1.2;changes=[]
for n in orbitals:
 d=P[n];file=Path(d['file']);rel=file.relative_to(root).as_posix();t=file.read_text(encoding='latin1');oldscale=num(d.get('scalesod',1));newscale=target/span(n)if n in ['bbase2','borbital']else oldscale*1.2;factor=newscale/oldscale;values={'ScaleSOD':newscale}
 for field in ['footprintBuffer','eastBuffer','westBuffer','northBuffer','southBuffer']:
  if field.lower()in d:values[field]=num(d[field.lower()])*factor
 for k,v in values.items():t=put(t,k,format(v,'.12g'))
 dest=overlay/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));pack['sourceHashes'][rel]=hashlib.sha256(file.read_bytes()).hexdigest();changes.append({'unit':n,'oldScale':oldscale,'newScale':newscale,'factor':factor,'visualSpan':span(n)*newscale,'borgMatchedToFederation':n in ['bbase2','borbital'],'scaledFields':values})
pack['orbitalResize']=changes;pack['orbitalTargetSpan']=target;pack['legacyHardpointSyntaxRepairs']=repairs;pack['gameplayFieldsChanged']='Only requested orbital scales / footprints and malformed legacy hardpoint declarations';pack['files']={p.relative_to(overlay).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in overlay.rglob('*')if p.is_file()};(stage/'manifest.json').write_text(json.dumps(pack,indent=2));(repo/'reports/resource-science-redesign-staged.json').write_text(json.dumps(pack,indent=2));print('Added orbital resizing:',len(changes),'models; target span:',round(target,3),'legacy hardpoint syntax repairs:',len(repairs))
