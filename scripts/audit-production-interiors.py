"""Inspect live ship production anchors and Federation Spacedock doors."""
from pathlib import Path
exec(Path('D:/aramada/scripts/build-native-faction-stations.py').read_text().split('for index,(n,a)in enumerate')[0])
out=repo/'patches/production-interiors-20261025';out.mkdir(exist_ok=True);scope=globals();idx={p.stem.lower():p for p in(root/'odf').rglob('*.odf')};rows=[]
for n,p in idx.items():
 if '/stations/'not in p.as_posix().lower():continue
 props=yard_unit_properties(n,scope);ships=[]
 for k,v in props.items():
  if re.fullmatch('builditem[0-9]+',k)and v.lower()in idx and '/ships/'in idx[v.lower()].as_posix().lower():ships.append(v)
 if not ships:continue
 source=props.get('basename',n).lower();model=native(source);last={};worlds=[];anchors={}
 for node in model.nodes:
  pi=last.get(node['parent'].lower());world=(worlds[pi]if pi is not None else np.eye(4))@matrix(node);worlds.append(world);last[node['id'].lower()]=len(worlds)-1
  if node['type']=='NULL_OR_HARDPOINT':anchors[node['id']]=world[:3,3].tolist()
 rows.append({'unit':n,'model':source,'class':props.get('classlabel'),'buildHardpoint':props.get('buildhardpoint'),'ships':ships,'anchors':anchors,'race':props.get('race')})
 if n=='fbase':
  details={'version':model.version,'properties':[x for x in dir(model)if not x.startswith('_')],'nodes':[{'id':x['id'],'parent':x['parent'],'type':str(x['type'])}for x in model.nodes]}
  for attr in ['animations','animation_channels','animation_references','anim_channels','anim_refs']:
   if hasattr(model,attr):details[attr]=getattr(model,attr)
  (out/'federation-spacedock-model.json').write_text(json.dumps(details,indent=2,default=str));preview(model,900).save(out/'spacedock-before.png')
(out/'audit.json').write_text(json.dumps(rows,indent=2));print(json.dumps([{'unit':r['unit'],'model':r['model'],'buildHardpoint':r['buildHardpoint'],'ships':len(r['ships'])}for r in rows],indent=2))
