"""Check exported research models against their original material tables."""
from pathlib import Path
exec(Path('D:/aramada/scripts/build-native-faction-stations.py').read_text().split('for index,(n,a)in enumerate')[0])
art=json.loads((stage/'artwork.json').read_text());rows=[];errors=[]
def material_signature(m):return json.dumps({k:v for k,v in m.items()if k!='name'},sort_keys=True,default=str)
for row in art:
 if row['kind']!='research':continue
 source=native(row['centralModel']);donor=native(baseline[row['donor']]['properties'].get('basename',row['donor']));allowed={material_signature(m)for model in[source,donor]for m in model.materials};model=load_model(O/'SOD'/(row['model']+'.sod'));bad=[i for i,m in enumerate(model.materials)if material_signature(m)not in allowed]
 if bad:
  example=model.materials[bad[0]];originals=[m for origin in[source,donor]for m in origin.materials];closest=min(originals,key=lambda m:sum(m.get(k)!=v for k,v in example.items()if k!='name'));diff={k:[closest.get(k),v]for k,v in example.items()if k!='name'and closest.get(k)!=v}
  errors.append({'unit':row['unit'],'changedMaterials':bad,'exampleDifference':diff})
 textures={p['data']['texture'].lower()for p in pieces(row['centralModel'])}
 for node in model.nodes:
  if node['type']=='MESH'and node['data']['texture'].lower()not in textures:errors.append({'unit':row['unit'],'unexpectedTexture':node['data']['texture']})
 rows.append({'unit':row['unit'],'source':row['centralModel'],'originalMaterialValuesPreserved':not bad,'textures':sorted(textures)})
report={'status':'FAIL'if errors else'PASS','stations':len(rows),'results':rows,'errors':errors,'applied':False};(repo/'patches/faction-research-preview/material-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps({'status':report['status'],'stations':len(rows),'errors':errors}))
if errors:raise SystemExit(1)
