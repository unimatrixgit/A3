"""Verify installed production anchors, door animation tracks and new ship assets."""
from pathlib import Path
exec(Path('D:/aramada/scripts/build-native-faction-stations.py').read_text().split('for index,(n,a)in enumerate')[0])
out=repo/'patches/production-interiors-20261025';rows=json.loads((out/'patch.json').read_text())['producers'];checks=[];errors=[]
def check(ok,label):
 checks.append(label)
 if not ok:errors.append(label)
def worlds(model):
 mats=[];last={};result={}
 for node in model.nodes:
  pi=last.get(node['parent'].lower());world=(mats[pi]if pi is not None else np.eye(4))@matrix(node);mats.append(world);last[node['id'].lower()]=len(mats)-1;result[node['id'].lower()]=world
 return result
for row in rows:
 p=yard_unit_properties(row['unit'],globals());model=native(p.get('basename',row['unit']).lower());w=worlds(model);hp=p.get('buildhardpoint','').lower();check(hp in w,'production point exists '+row['unit'])
 if hp not in w:continue
 points=visible_points(model);points=points[np.isfinite(points).all(axis=1)];pos=w[hp][:3,3];check(np.all(pos>=points.min(0)-.001)and np.all(pos<=points.max(0)+.001),'inside model bounds '+row['unit'])
 if row['method']=='assembly-bay centre':check(np.allclose(pos,w['tyrepair'][:3,3],atol=.001),'production at bay centre '+row['unit'])
base=native('fbase');tracks={x['node_ref']:x for x in base.animation_transforms};check(all('Box'+str(i).zfill(2)in tracks for i in range(1,9)),'all four Spacedock door pairs animated')
opened=copy.deepcopy(base);nodes={n['id']:n for n in opened.nodes}
for key,track in tracks.items():
 if key.startswith('Box'):nodes[key]['local_transform']=track['keyframe_data'][-1]
preview(opened,900).save(out/'spacedock-doors-fixed.png')
for n in ['xhftvarek','xdcfighter']:
 p=yard_unit_properties(n,globals());model=native(p['basename'].lower());nodes={x['id'].lower()for x in model.nodes}
 for key,value in p.items():
  if re.fullmatch('weaponhardpoints[0-9]+',key):
   for hp in re.findall('[A-Za-z0-9_]+',value):check(hp.lower()in nodes,'weapon hardpoint '+n+' '+hp)
 check((root/'bitmaps/AdmiralsLog/ShipImages'/(n+'.bmp')).is_file(),'results portrait '+n)
p=yard_unit_properties('xdcarrier',globals());model=native(p['basename'].lower());w=worlds(model);points=visible_points(model);points=points[np.isfinite(points).all(axis=1)];pos=w[p['buildhardpoint'].lower()][:3,3];check(np.all(pos>=points.min(0))and np.all(pos<=points.max(0)),'carrier launch point inside model');check(p.get('builditem0')=='xdcfighter'and p['classlabel']=='starbase','native carrier production class and fighter menu')
r={'status':'FAIL'if errors else'PASS','checks':len(checks),'errors':errors,'producersAudited':len(rows),'runtimeVerified':False};(out/'installed-verification.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
if errors:raise SystemExit(1)
