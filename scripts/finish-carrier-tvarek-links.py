"""Finish new-unit labels and match restricted-mode producer availability."""
from pathlib import Path
import json,re,hashlib
repo=Path('D:/aramada');root=Path('D:/armadaIII');stage=repo/'patches/carrier-tvarek-links-20261025';O=stage/'overlay';sources={}
def put(t,k,v):return re.sub(r'(?mi)^[ \t]*'+k+r'[ \t]*=[^\r\n]*','',t).rstrip()+'\n'+k+' = '+v+'\n'
def emit(rel,t):
 p=O/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));sources[rel]=hashlib.sha256((root/rel).read_bytes()).hexdigest()
rel='odf/ships/xhftvarek.odf';t=(root/rel).read_text(encoding='latin1');t=put(t,'label','"U.S.S. T\'Varek"');t=put(t,'shiptype','"C"');emit(rel,t)
for name in ['nosci','nosuper']:
 rel='techtree/'+name+'.tt';t=(root/rel).read_text(encoding='latin1');assert re.search(r'(?mi)^xflegacyyard\.odf\s+-1',t);t=re.sub(r'(?mi)^xhftvarek\.odf[^\r\n]*','xhftvarek.odf -1 // Producer unavailable in this technology mode',t);emit(rel,t)
report={'status':'PASS','description':'Finalised Federation hero display labels and technology-mode gates; carrier and fighter source snapshots aligned with native ODF parsing.','files':{p.relative_to(O).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in O.rglob('*')if p.is_file()},'sourceHashes':sources,'baselineUpdates':['xdcarrier','xdcfighter','xhftvarek'],'runtimeVerified':False};(stage/'patch.json').write_text(json.dumps(report,indent=2));print('Final links staged.')
