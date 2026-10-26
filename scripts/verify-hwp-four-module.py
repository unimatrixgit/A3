"""Verify geometry, original functionality and the 16 distinct emitter positions."""
from pathlib import Path
exec(Path('D:/aramada/scripts/preview-vanilla-station-direction.py').read_text().split('rows=[];sources=[]')[0])
import hashlib
st=repo/'patches/hwp-four-module-20261026';O=st/'overlay';art=json.loads((st/'artwork.json').read_text());idx={p.stem.lower():p for p in(root/'odf').rglob('*.odf')};checks=[];gallery=[]
def props(p):return {k.lower():v.split('//')[0].strip().strip('"')for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',p.read_text(encoding='latin1'))}
def worlds(model):
 result={};last={};ww=[]
 for node in model.nodes:
  i=last.get(node['parent'].lower());world=(ww[i]if i is not None else np.eye(4))@matrix(node);ww.append(world);last[node['id'].lower()]=len(ww)-1;result[node['id'].lower()]=world
 return result
for row in art:
 n=row['unit'];before=props(idx[n]);after=props(O/idx[n].relative_to(root));changed={k for k in before.keys()|after.keys()if before.get(k)!=after.get(k)};assert changed=={'weaponhardpoints'+str(i)for i in range(1,17)},(n,changed)
 model=load_model(O/'SOD'/(row['model']+'.sod'));original=native(row['model']);w=worlds(model);oldw=worlds(original)
 for node in original.nodes:
  if node['type']!='MESH':assert np.allclose(w[node['id'].lower()],oldw[node['id'].lower()],atol=1e-4),(n,node['id'])
 ports=[]
 for bank in row['weaponMounts']:
  i=bank['slot'];hp='hwpbank'+str(i);assert after['weaponhardpoints'+str(i)]==hp;assert before['weapon'+str(i)]==after['weapon'+str(i)];bank['weapon']=after['weapon'+str(i)];ports.append(w[hp][:3,3])
 assert len(ports)==16 and len({tuple(np.round(v,4))for v in ports})==16
 originalSpan=np.ptp(visible_points(original),axis=0).max();newSpan=np.ptp(visible_points(model),axis=0).max();assert abs(newSpan/originalSpan-1)<1e-5,(n,originalSpan,newSpan)
 for node in model.nodes:
  if node['type']!='MESH':continue
  dat=node['data'];assert len(dat['vertices'])<=450 and np.isfinite(dat['vertices']).all()and np.isfinite(dat['texture_coordinates']).all();assert dat['texture'].lower()in texidx
 for prefix in ['gb','wf']:
  im=Image.open(O/'Textures/RGB'/(prefix+row['model']+'.tga'));assert im.size==(64,64)and im.mode=='RGB'
 row.update(bays=0,queueCount=0);checks.append({'unit':n,'unchangedStatsAndFunctions':True,'legacyAnchorsPreserved':True,'uniqueWeaponMounts':16,'sizePreserved':True})
 if row['theme']!='bg':
  im=preview(model,700);ImageDraw.Draw(im).text((12,12),names[row['theme']]+' HWP - 16 banks',font=font,fill=(235,240,250));im.save(st/(n+'-full.png'));gallery.append(im)
sheet=Image.new('RGB',(2100,2100),(10,15,22))
for i,im in enumerate(gallery):sheet.paste(im,((i%3)*700,(i//3)*700))
sheet.save(st/'all-hwp-fortresses.png');(st/'artwork.json').write_text(json.dumps(art,indent=2));(st/'verification.json').write_text(json.dumps({'status':'PASS','models':checks,'factionDesigns':len(gallery),'runtimeVerified':False},indent=2));print('PASS: 10 models, 160 mounts, unchanged stats/functions/size and legacy anchors')
