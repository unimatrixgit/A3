from pathlib import Path
import sys,contextlib,io,re,copy,json,hashlib
import numpy as np
exec(Path('D:/aramada/scripts/build-bajoran-redesign-v3.py').read_text().split('ROOT=')[0])
root=Path('D:/armadaIII');stage=Path('D:/Xaramada-Modwork/bajor-mini-ds9-metal');stage.mkdir(parents=True,exist_ok=True)
with contextlib.redirect_stdout(io.StringIO()):m=IO().read_file(str(root/'SOD/fds9.sod'));old=IO().read_file(str(root/'SOD/br3_bjorbital.sod'))
t=(root/'odf/stations/bjorbital.odf').read_text();required=set(x.lower()for x in re.findall(r'\bhp\d+\b',t,re.I));names={n['id'].lower()for n in m.nodes};print('missing native DS9 hardpoints',sorted(required-names))
# Keep the existing orbital ODF and sprite identity unchanged; scale DS9 geometry internally.
factor=.4*.8858/.83684
for n in m.nodes:
 tr=np.array(n['local_transform'],dtype=float);tr[3]*=factor;n['local_transform']=tr.tolist()
 if n['type']=='MESH':n['data']['vertices']=(np.array(n['data']['vertices'])*factor).tolist()
# Add any needed orbital hardpoints with their old local anchors; native DS9 existing ones remain.
oldnodes={n['id'].lower():n for n in old.nodes};byid={n['id']:n for n in old.nodes}
def world(n,seen=None):
 seen=set()if seen is None else seen
 if n['id']in seen:return np.eye(4)
 seen.add(n['id']);tr=np.array(n['local_transform']);a=np.eye(4);a[:3,:3]=tr[:3].T;a[:3,3]=tr[3];par=byid.get(n['parent']);return world(par,seen)@a if par else a
rootnode=next(n for n in m.nodes if not n['parent']or n['parent']not in {x['id']for x in m.nodes})
for hp in required-names:
 n=copy.deepcopy(oldnodes[hp]);w=world(n);n['parent']=rootnode['id'];n['local_transform']=np.vstack([np.eye(3),w[:3,3]]).tolist();m.nodes.append(n)
m.set_nodes(m.nodes);o=stage/'br3_bjorbital.sod';writer=IO();writer.curr_sod_version=m.version
with contextlib.redirect_stdout(io.StringIO()):writer.write_file(m,str(o));check=IO().read_file(str(o))
assert required<={n['id'].lower()for n in check.nodes}
Path('D:/aramada/reports/bajoran-mini-ds9-metal.json').write_text(json.dumps({'stage':str(o),'target':'D:/armadaIII/SOD/br3_bjorbital.sod','sourceSha256':hashlib.sha256((root/'SOD/br3_bjorbital.sod').read_bytes()).hexdigest(),'sha256':hashlib.sha256(o.read_bytes()).hexdigest(),'relativeToStarbase':.4,'odfChanged':False,'guiChanged':False,'applied':False,'runtimeVerified':False},indent=2));print('Prepared miniature DS9 model only; required hardpoints verified')
