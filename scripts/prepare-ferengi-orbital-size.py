from pathlib import Path
exec(Path('D:/aramada/scripts/build-bajor-redesign-v4.py').read_text().split('for name,d in before.items():')[0])
import ast
tree=ast.parse((repo/'scripts/stage-approved-visual-refresh.py').read_text())
for node in tree.body:
 if isinstance(node,ast.FunctionDef)and node.name in ['load_model','visible_points']:exec(compile(ast.Module(body=[node],type_ignores=[]),'model-helpers','exec'))
P=json.loads((repo/'reports/ferengi-orbital-size-before.json').read_text());stage=repo/'patches/ferengi-miner-size-20261025';reportfile=repo/'reports/ferengi-miner-size-prepared.json';pack=json.loads(reportfile.read_text());assert pack['status']=='PREPARED - NOT APPLIED'
def num(v):return float(str(v).rstrip('fF'))
def span(n):return np.ptp(visible_points(load_model(root/'SOD'/(P[n]['basename']+'.sod'))),axis=0).max()
target=span('forbital')*num(P['forbital'].get('scalesod',1));rows=[]
for n in ['xfgmetal2','xfgmetal3','xbgmetal2','xbgmetal3']:
 d=P[n];src=Path(d['file']);rel=src.relative_to(root).as_posix();old=src.read_text(encoding='latin1');oldscale=num(d.get('scalesod',1));newscale=target/span(n);factor=newscale/oldscale;fields={'ScaleSOD':newscale}
 for key in ['footprintBuffer','eastBuffer','westBuffer','northBuffer','southBuffer']:
  if key.lower()in d:fields[key]=num(d[key.lower()])*factor
 t=old
 for k,v in fields.items():t=put(t,k,format(v,'.12g'))
 allowed={k.lower()for k in fields}
 def stripped(text):return'\n'.join(line for line in text.splitlines()if line.strip()and(re.match(r'^[ \t]*(\w+)[ \t]*=',line)is None or re.match(r'^[ \t]*(\w+)[ \t]*=',line)[1].lower()not in allowed))
 assert stripped(t)==stripped(old),'Unexpected gameplay change '+n
 out=stage/'overlay'/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));assert abs(span(n)*newscale-target)<.001
 rows.append({'unit':n+'.odf','file':rel,'oldScale':oldscale,'newScale':newscale,'factor':factor,'targetWorldSpan':target,'fields':fields,'sourceHash':hashlib.sha256(src.read_bytes()).hexdigest(),'stagedHash':hashlib.sha256(out.read_bytes()).hexdigest()})
pack['orbitals']=rows;pack['orbitalReference']='forbital';pack['orbitalTargetWorldSpan']=target;(stage/'manifest.json').write_text(json.dumps(pack,indent=2));reportfile.write_text(json.dumps(pack,indent=2));(repo/'reports/ferengi-orbital-size-prepared.json').write_text(json.dumps({'status':'PREPARED - NOT APPLIED','orbitals':rows,'reference':'forbital'},indent=2));
with(stage/'README.md').open('a')as f:f.write('\nAlso includes all four Ferengi metal orbital variants. Their rendered hull size matches the current Federation orbital, with proportional placement buffers; mining, weapons and economy fields are unchanged.\n')
s=json.loads((repo/'status.json').read_text(encoding='utf-8-sig'));s['current']='Ferengi size patch prepared: eight miners 45% smaller; four metal orbitals match the current Federation orbital. Mining, weapons, costs, capacities and crew unchanged. NOT APPLIED.';(repo/'status.json').write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n[Ferengi orbital size] Prepared four orbital definitions matched to Federation world span '+str(target)+'. Added to pending Ferengi size patch; NOT APPLIED.\n')
print(json.dumps({'status':pack['status'],'orbitals':len(rows),'referenceSpan':target,'newScales':[r['newScale']for r in rows]}))
