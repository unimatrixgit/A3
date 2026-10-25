"""Place ship production inside the existing hull/bay and animate all ESD doors."""
from pathlib import Path
exec(Path('D:/aramada/scripts/build-native-faction-stations.py').read_text().split('for index,(n,a)in enumerate')[0])
stage=repo/'patches/production-interiors-20261025';dest=stage/'overlay';rows=json.loads((stage/'audit.json').read_text());tech={}
for line in(root/'techtree/tech1.tt').read_text(encoding='latin1').splitlines():
 x=line.split('//')[0].split()
 if len(x)>1 and x[0].endswith('.odf'):tech[Path(x[0]).stem.lower()]=int(x[1])
changed={};edits={};report=[];sourceHashes={}
def positions(model):
 world=[];last={};out={}
 for node in model.nodes:
  pi=last.get(node['parent'].lower());mat=(world[pi]if pi is not None else np.eye(4))@matrix(node);world.append(mat);last[node['id'].lower()]=len(world)-1;out[node['id'].lower()]=mat
 return out
for row in rows:
 n=row['unit']
 if tech.get(n,-1)<0 or row['race']=='species8472'or n=='brecycle':continue
 p=yard_unit_properties(n,globals());source=row['model'];model=changed.setdefault(source,copy.deepcopy(native(source)));world=positions(model);hp=p.get('buildhardpoint','').lower();node=next((x for x in model.nodes if x['id'].lower()==hp),None);before=world.get(hp,np.eye(4))[:3,3].copy();pts=visible_points(model);pts=pts[np.isfinite(pts).all(axis=1)];lo=pts.min(0);hi=pts.max(0);inside=bool(node is not None and np.all(before>=lo)and np.all(before<=hi));method='original point already within model bounds'
 if source.startswith('ty26_')and n in d['assets']and d['assets'][n]['kind']=='yard':
  repair=next(x for x in model.nodes if x['id'].lower()=='tyrepair');node['parent']=repair['parent'];node['local_transform']=copy.deepcopy(repair['local_transform']);method='assembly-bay centre'
 elif not inside:
  parent=next(x for x in model.nodes if not x['parent']);target=(lo+hi)/2;inverse=np.linalg.inv(world[parent['id'].lower()]);local=inverse@np.r_[target,1]
  hp='piinside_'+n;model.nodes.append({'id':hp,'parent':parent['id'],'type':'NULL_OR_HARDPOINT','data':None,'local_transform':[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],local[:3].tolist()]});rel=next(x for x in(root/'odf/stations').glob('*.odf')if x.stem.lower()==n).relative_to(root).as_posix();edits[rel]=put((root/rel).read_text(encoding='latin1'),'buildHardpoint','"'+hp+'"');method='new internal production hardpoint'
 after=positions(model)[hp][:3,3];assert np.isfinite(after).all()and np.all(after>=lo-1e-4)and np.all(after<=hi+1e-4),(n,after,lo,hi)
 report.append({'unit':n,'model':source,'method':method,'before':before.tolist(),'after':after.tolist(),'buildHardpoint':hp,'bounds':[lo.tolist(),hi.tolist()]})
# Four gate pairs exist, but the source has tracks for Box01/Box02 only.
model=changed.setdefault('fbase',copy.deepcopy(native('fbase')));nodes={n['id']:n for n in model.nodes};doorNames=['Box'+str(i).zfill(2)for i in range(1,9)];template=model.animation_transforms[0];doorRows=[]
for pair in range(4):
 names=doorNames[pair*2:pair*2+2];coords=[np.asarray(nodes[name]['local_transform'])for name in names];center=(coords[0][3]+coords[1][3])/2;axis=2 if abs(center[0])>abs(center[2])else 0
 for name,start in zip(names,coords):
  v=np.asarray(nodes[name]['data']['vertices']);distance=float(np.ptp(v,axis=0)[axis]+2);sign=-1 if start[3,axis]<center[axis]else 1;keys=[]
  for frame in range(100):t=start.copy();t[3,axis]+=sign*distance*frame/99;keys.append(t.tolist())
  animation=copy.deepcopy(template);animation.update(node_ref=name,keyframe_data=keys);existing=next((x for x in model.animation_transforms if x['node_ref']==name),None)
  if existing is None:model.animation_transforms.append(animation)
  else:existing.update(animation)
  doorRows.append({'node':name,'slideAxis':axis,'slideDistance':sign*distance,'frames':100})
assert len([x for x in model.animation_transforms if x['node_ref']in doorNames])==8
for source,model in changed.items():
 original=native(source)
 if model.to_dict()==original.to_dict():continue
 rel=sods[source].relative_to(root).as_posix();path=dest/rel;path.parent.mkdir(parents=True,exist_ok=True);writer=IO();writer.curr_sod_version=model.version
 with contextlib.redirect_stdout(io.StringIO()):writer.write_file(model,str(path))
 restored=load_model(path);assert len(restored.nodes)==len(model.nodes);assert len(restored.animation_transforms)==len(model.animation_transforms);assert all(np.isfinite(x['local_transform']).all()for x in restored.nodes)
 sourceHashes[rel]=hashlib.sha256((root/rel).read_bytes()).hexdigest()
for rel,t in edits.items():
 path=dest/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));sourceHashes[rel]=hashlib.sha256((root/rel).read_bytes()).hexdigest()
files={p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()};result={'status':'PASS','files':files,'sourceHashes':sourceHashes,'producers':report,'doorTracks':doorRows,'runtimeVerified':False};(stage/'patch.json').write_text(json.dumps(result,indent=2));print(json.dumps({'status':'PASS','auditedProducers':len(report),'changedFiles':len(files),'doorTracks':8,'insideBay':sum(r['method']=='assembly-bay centre'for r in report)}))
