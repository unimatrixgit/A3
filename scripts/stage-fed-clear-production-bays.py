"""Stage approved vanilla-derived meshes, preserving installed ODFs and skeletons."""
from pathlib import Path
src=Path('D:/aramada/scripts/preview-vanilla-station-direction.py').read_text()
exec(src.split('rows=[];sources=[]')[0])
import hashlib
stage=repo/'patches/fed-clear-production-bays-20261026';O=stage/'overlay';stage.mkdir(exist_ok=True)
tree=ast.parse(src);loop=next(x for x in tree.body if isinstance(x,ast.For)and isinstance(x.target,ast.Tuple))
body=loop.body;cut=next(i for i,x in enumerate(body)if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='yard'for t in x.targets))
yardCode=compile(ast.Module(body=body[:cut],type_ignores=[]),'approved-yard-preview','exec')
research={'f':'xvstock_fresear','b':'xvstock_bresear','k':'xvstock_kresear','r':'xvstock_rresear','c':'xvstock_cresear','bj':'xvstock_cresear','d':'dresear','br':'brresear','fg':'xfgresearch','bg':'xfgresearch'}
odfs={p.stem.lower():p for p in(root/'odf').rglob('*.odf')}
def props(n):
 t=odfs[n].read_text(encoding='latin1');return {k.lower():v.split('//')[0].strip().strip('"')for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t)}
records=[];checks=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,a in d['assets'].items():
 if a['kind']!='yard' or a['theme']!='f':continue
 theme=a['theme'];code=theme;code='fg'if code=='bg'else code;title=names[code];kind=a['kind'];bp=props(n);alias=bp.get('basename',n);old=native(alias);model=copy.deepcopy(old);scale=float(bp.get('scalesod','1').rstrip('fF;'));oldpts=visible_points(old);size=float(np.ptp(oldpts,axis=0).max());allparts=[]
 if kind in ['yard','service']:
  exec(yardCode,globals());allparts=p[-len(g.parts):];central=source
 else:
  source=research[code];source=source if source in sods else research['d'];role=2 if 'upgrade'in n else 1 if n.endswith('2')or n=='xselaresearch'else 0
  candidate=source.replace('resear','upgrade')if role==2 else source+'2'if role==1 else source
  if candidate in sods:source=candidate
  allparts=change(pieces(source));g=truss.Geometry()
  if code=='bj':
   allparts=change(allparts,1,stretch=(1.08,.82,1.08))
   for side in [-1,1]:g.box((side*.31,.03,0),(.12,.14,.23),yaw=side*.25,taper=.65)
  else:g.cylinder((0,-.26,0),.17,.12,n=8 if code=='b'else 16)
  allparts+=research_surface_parts(g,source,globals());central=source
 points=np.concatenate([p['data']['vertices']for p in allparts]);center=(points.max(0)+points.min(0))/2;span=float(np.ptp(points,axis=0).max());podFittings={}
 if kind=='research':
  fittings,podFittings=research_pod_fittings(old,bp,source,globals(),size);allparts+=fittings
 model.set_version(max(model.version,native(source).version))
 for node in model.nodes:
  if node['type']=='MESH':node['type']='NULL_OR_HARDPOINT';node['data']=None
 parent=next(x for x in model.nodes if not x['parent']);inv=np.linalg.inv(matrix(parent));chunk=0
 for part in allparts:
  dat=part['data'];mapping={}
  for mat in part['materials']:
   m=copy.deepcopy(mat);oldname=m['name'];m['name']='vnmat'+str(len(model.materials));mapping[oldname]=m['name'];model.materials.append(m)
  assert dat['texture'].lower()in texidx,(n,dat['texture'])
  for group in dat['vertex_lighting_groups']:
   for start in range(0,len(group['faces']),150):
    vv=[];uv=[];ff=[]
    for face in group['faces'][start:start+150]:
     base=len(vv)
     for vi,ui in face:
      world=dat['vertices'][vi]if part.get('worldSpace')else(dat['vertices'][vi]-center)/span*size;vv.append((inv@np.r_[world,1])[:3].tolist());uv.append(dat['texture_coordinates'][ui])
     ff.append([[base+j,base+j]for j in range(3)])
    if not ff:continue
    outdat=copy.deepcopy(dat);outdat.update(vertices=vv,texture_coordinates=uv,vertex_lighting_groups=[{'lighting_material':mapping.get(group['lighting_material'],model.materials[0]['name']),'faces':ff}]);outdat.setdefault('texture_material','default');outdat.setdefault('borgification',{'texture':dat['texture']})
    if model.version>1.9101:outdat['bump_map']=1
    assert np.isfinite(vv).all()and np.isfinite(uv).all()
    model.nodes.append({'id':'vnmesh'+str(chunk),'parent':parent['id'],'type':'MESH','local_transform':identity,'data':outdat});chunk+=1
 if kind in ['yard','service']:
  # Native yard origin lies in the assembly opening; no forward spawn offset.
  pos=(np.zeros(3)-center)/span*size
  for hp in ['tylaunch','tyrepair']:
   node=next(x for x in model.nodes if x['id'].lower()==hp);node.update(parent=parent['id'],local_transform=inv[:3,:3].T.tolist()+[(inv@np.r_[pos,1])[:3].tolist()])
 oldids={x['id'].lower()for x in old.nodes};assert oldids.issubset({x['id'].lower()for x in model.nodes})
 path=O/'SOD'/(alias+'.sod');path.parent.mkdir(parents=True,exist_ok=True);writer=IO();writer.curr_sod_version=model.version
 with contextlib.redirect_stdout(io.StringIO()):writer.write_file(model,str(path))
 loaded=load_model(path);assert len(loaded.nodes)==len(model.nodes)
 im=preview(loaded,256);im.save(stage/(n+'-preview.png'));icon=im.convert('RGBA');col=(90,230,155)if kind=='service'else(245,210,65)if kind=='research'else(85,175,255);dr=ImageDraw.Draw(icon)
 for y in range(256):dr.line((0,y,255,y),fill=col+(int(y/255*35),))
 icon=Image.alpha_composite(im.convert('RGBA'),icon);icon.alpha_composite(symbol('repair'if kind=='service'else'science'if kind=='research'else'yard'),(4,4));td=O/'Textures/RGB';td.mkdir(parents=True,exist_ok=True)
 icon.resize((64,64),Image.Resampling.LANCZOS).convert('RGB').save(td/('gb'+alias+'.tga'));im.resize((64,64),Image.Resampling.LANCZOS).convert('RGB').save(td/('wf'+alias+'.tga'))
 records.append({'unit':n,'model':alias,'kind':kind,'theme':theme,'centralModel':source,'size':size*scale,'scale':scale,'podFittings':podFittings,'nativePodHardpointsPreserved':kind=='research','bays':1,'queueCount':1,'architecture':'approved vanilla-derived 20261026'})
 checks.append({'unit':n,'odfHash':sha(odfs[n]),'nodeIdentifiersPreserved':True,'roundTrip':True,'meshes':chunk});print(n+' staged',flush=True)
files={p.relative_to(O).as_posix():sha(p)for p in O.rglob('*')if p.is_file()};sourceHashes={r:sha(root/r)for r in files if(root/r).exists()}
(stage/'artwork.json').write_text(json.dumps(records,indent=2));(stage/'validation.json').write_text(json.dumps({'status':'PASS','units':checks,'odfsChanged':False,'runtimeVerified':False},indent=2));(stage/'patch.json').write_text(json.dumps({'status':'PASS','files':files,'sourceHashes':sourceHashes,'description':'Approved vanilla-derived faction yards and research artwork, with Cardassian-derived Bajoran refits. Stats and technology unchanged.'},indent=2));print('PASS '+str(len(records))+' models; '+str(len(files))+' files')



