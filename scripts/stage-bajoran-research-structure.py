from pathlib import Path
import re,json,hashlib
repo=Path('D:/aramada');root=Path('D:/armadaIII');p=repo/'reports/bajoran-durability-research.json';r=json.loads(p.read_text());stage=Path(r['stage']);mapping={'fbase':'bjbase','fyard':'bjyard','fyard2':'bjyard2','fyard3':'bjyard3','fresear':'bjresear','fresear2':'bjresear2','fupgrade':'bjupgrade'}
for n in [1,2,3,4,5,6,7,8,9,11,12,13,14,15,16,21,22,23,24,25]:mapping['fedpod'+str(n)]='bjpod'+str(n)
for src in (root/'techtree').glob('*.tt'):
 t=src.read_text(encoding='latin1')
 if not re.search(r'(?mi)^fresear\.odf[ \t]+2[ \t]+fbase\.odf[ \t]+fyard\.odf',t):continue
 for fed,bj in mapping.items():
  if not fed.startswith('fedpod'):continue
  m=re.search(r'(?mi)^'+fed+r'\.odf[^\r\n]*',t)
  if not m:continue
  line=m[0]
  for a,b in mapping.items():line=re.sub(r'(?i)\b'+a+r'(?=\.odf)',b,line)
  t,n=re.subn(r'(?mi)^'+bj+r'\.odf[^\r\n]*',line,t);assert n==1,(src,bj)
 rel='techtree/'+src.name;o=stage/rel;o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));r['files'].append({'path':rel,'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'sha256':hashlib.sha256(o.read_bytes()).hexdigest()})
r['researchStructure']='Federation research building/pod definitions and upgrade chains, with matching Bajor dependencies; paired yard/lab unlock rules retained.';p.write_text(json.dumps(r,indent=2))
s=(repo/'scripts/audit-bajoran-progression.cjs').read_text().replace("root+'/techtree/tech1.tt'","'D:/Xaramada-Modwork/bajor-durability-research/techtree/tech1.tt'").replace('bajoran-progression-live.json','bajoran-progression-durability-research.json');(repo/'scripts/audit-bajoran-durability-research.cjs').write_text(s)
print('Research prerequisites staged; total files',len(r['files']))
