"""Cap HWP geometry and placement padding below four native grid squares."""
from pathlib import Path
exec(Path('D:/aramada/scripts/preview-vanilla-station-direction.py').read_text().split('rows=[];sources=[]')[0])
import hashlib
stage=repo/'patches/hwp-under-four-squares-20261026';O=stage/'overlay';stage.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
grid=float(re.search(r'STATION_PLACEMENT_GRID_SIZE\s*=\s*([\d.]+)',(root/'RTS_CFG.h').read_text(encoding='latin1'))[1]);limit=grid*3.8;idx={p.stem.lower():p for p in(root/'odf/stations').glob('*.odf')}
def props(t):return {k.lower():v.split('//')[0].strip().strip('"')for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t)}
for n,a in d['assets'].items():
 if a['kind']!='hwp':continue
 path=idx[n];t=path.read_text(encoding='latin1');before=props(t);scale=float(before['scalesod']);points=visible_points(native(before['basename']));dims=np.ptp(points,axis=0);span=float(max(dims[0],dims[2])*scale);newScale=min(scale,limit/max(dims[0],dims[2]));t=put(t,'ScaleSOD',format(newScale,'.12g'))
 # Zero extra padding lets the engine use the scaled model's natural footprint.
 for key in ['footprintBuffer','northBuffer','southBuffer','eastBuffer','westBuffer']:t=put(t,key,0)
 after=props(t);allowed={'scalesod','footprintbuffer','northbuffer','southbuffer','eastbuffer','westbuffer'};diff={k for k in before.keys()|after.keys()if before.get(k)!=after.get(k)};assert diff<=allowed
 newSpan=float(max(dims[0],dims[2])*newScale);assert newSpan<grid*4 and newSpan<=span+1e-7;assert before.get('latinumtransferrate')==after.get('latinumtransferrate')
 f=O/path.relative_to(root);f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));rows.append({'unit':n,'beforeSpan':span,'afterSpan':newSpan,'gridSquares':newSpan/grid,'scale':newScale,'latinumTransferRate':after.get('latinumtransferrate'),'statsAndWeaponsUnchanged':True,'extraFootprintPadding':0})
files={p.relative_to(O).as_posix():sha(p)for p in O.rglob('*')if p.is_file()};(stage/'patch.json').write_text(json.dumps({'status':'PASS','files':files,'sourceHashes':{r:sha(root/r)for r in files},'description':'All HWP models and natural construction footprints are below four grid squares, capped at 3.8. Smaller platforms not enlarged; latinum unloading and combat stats preserved.'},indent=2));(stage/'validation.json').write_text(json.dumps({'status':'PASS','gridSize':grid,'maximumSpan':limit,'units':rows,'runtimeVerified':False},indent=2));print(json.dumps(rows,indent=2))
