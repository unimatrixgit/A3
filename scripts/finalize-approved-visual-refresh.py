"""Add safe model anchors for existing ODF references absent from legacy source models."""
from pathlib import Path
exec(Path('D:/aramada/scripts/build-bajor-redesign-v4.py').read_text().split('for name,d in before.items():')[0])
stage=Path('D:/Xaramada-Modwork/approved-visual-refresh-stage');overlay=stage/'overlay';pack=json.loads((stage/'manifest.json').read_text());added=[]
for row in pack['units']:
 path=overlay/'SOD'/(row['model']+'.sod');m=load(path);names={n['id'].lower()for n in m.nodes};parent=next(n for n in m.nodes if not n['parent']);odfs=list((overlay/'odf').rglob(row['unit']+'.odf'));assert len(odfs)==1;t=odfs[0].read_text(encoding='latin1');wanted=[]
 for key,values in re.findall(r'(?mi)^[ \t]*([A-Za-z0-9_]*Hardpoints?|weaponHardpoints[0-9]+)[ \t]*=[ \t]*([^\r\n]*)',t):wanted.extend(re.findall(r'"([A-Za-z0-9_]+)"',values))
 missing=sorted({hp for hp in wanted if hp.lower()not in names})
 if not missing:continue
 # Centre anchors are only fallbacks for references the original model did not supply.
 for hp in missing:m.nodes.append({'id':hp,'parent':parent['id'],'type':'NULL_OR_HARDPOINT','local_transform':[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],[0.,0.,0.]],'data':None})
 writer=IO();writer.curr_sod_version=m.version
 with contextlib.redirect_stdout(io.StringIO()):writer.write_file(m,str(path))
 check=load(path);assert all(hp in {n['id']for n in check.nodes}for hp in missing);added.append({'unit':row['unit'],'anchors':missing,'reason':'Existing ODF reference absent from original legacy SOD; centre fallback added without altering gameplay fields.'})
pack['legacyAnchorRepairs']=added;pack['files']={p.relative_to(overlay).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in overlay.rglob('*')if p.is_file()};(stage/'manifest.json').write_text(json.dumps(pack,indent=2));(repo/'reports/approved-visual-refresh-staged.json').write_text(json.dumps(pack,indent=2));print('Model-only legacy anchor repairs:',len(added),'models')
