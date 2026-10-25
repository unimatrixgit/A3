"""Build complete native stations from faction starbase and original yard components."""
from pathlib import Path
exec(Path('D:/aramada/scripts/build-bajor-redesign-v4.py').read_text().split('for name,d in before.items():')[0])
exec(Path('D:/aramada/scripts/twin-yard-render.py').read_text())
import ast,importlib.util
sp=importlib.util.spec_from_file_location('stationtruss',repo/'scripts/approved-station-geometry.py');truss=importlib.util.module_from_spec(sp);sp.loader.exec_module(truss)
for node in ast.parse((repo/'scripts/stage-approved-visual-refresh.py').read_text()).body:
 if isinstance(node,ast.FunctionDef)and node.name in ['load_model','visible_points']:exec(compile(ast.Module(body=[node],type_ignores=[]),'model-helpers','exec'))
stage=repo/'patches/twin-yards-20261025';O=stage/'overlay';d=json.loads((stage/'design.json').read_text());sods={p.stem.lower():p for p in(root/'SOD').iterdir()if p.suffix.lower()=='.sod'};models={};partsCache={};baseline=d['baseline'];records=[]
bases={'f':'fbase','b':'xvstock_bbase','k':'kbase','r':'rbase','c':'cbase','d':'dbase','bj':'bjbase','br':'brbase','fg':baseline['xfgserv']['properties']['basename'],'bg':baseline['xfgserv']['properties']['basename']}
yards={'f':'fyard','b':'xvstock_byard','k':'kyard','r':'ryard','c':'cyard','d':'dyard','bj':'bjyard','br':'bryard','fg':'xfgmerc','bg':'xfgmerc'}
def native(name):
 if name not in models:models[name]=load_model(sods[name])
 return models[name]
def pieces(name):
 if name in partsCache:return copy.deepcopy(partsCache[name])
 m=native(name);worlds=[];chains=[];last={};parts=[]
 for n in m.nodes:
  pi=last.get(n['parent'].lower());world=(worlds[pi]if pi is not None else np.eye(4))@matrix(n);chain=(chains[pi]if pi is not None else[])+[n['id'].lower()];worlds.append(world);chains.append(chain);last[n['id'].lower()]=len(worlds)-1
  if n['type']!='MESH'or any(x in ['borg','damage','shield','shields']for x in chain):continue
  dat=copy.deepcopy(n['data']);v=np.asarray(dat['vertices']);dat['vertices']=(world@np.c_[v,np.ones(len(v))].T).T[:,:3];parts.append({'data':dat,'materials':copy.deepcopy(m.materials),'chain':chain})
 lods={x for p in parts for x in p['chain']if re.fullmatch('lod[0-9]+',x)}
 if lods:
  best=min(lods,key=lambda x:int(x[3:]));parts=[p for p in parts if best in p['chain']or not any(x in lods for x in p['chain'])]
 points=np.concatenate([p['data']['vertices']for p in parts]);center=(points.max(0)+points.min(0))/2;span=np.ptp(points,axis=0).max()
 for p in parts:p['data']['vertices']=(p['data']['vertices']-center)/span
 partsCache[name]=parts;return copy.deepcopy(parts)
def put(t,k,v):return re.sub(r'(?mi)^[ \t]*'+re.escape(k)+r'[ \t]*=[^\r\n]*','',t).rstrip()+'\n'+k+' = '+str(v)+'\n'
sprite=(root/'Sprites/gui_global.spr').read_text(encoding='latin1');ns={};exec((repo/'scripts/apply-function-badges-scale.py').read_text().split("for row in pack['units']:")[0],ns);symbol=ns['symbol'];font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',23)
hero={'fyard3','xflegacyyard','s31yard','mryfeda','mryfedb','byard3','kyard3','ryard3','cyard3','dyard3','bjyard2'}
for index,(n,a)in enumerate(d['assets'].items(),1):
 print('Native faction station '+str(index)+'/'+str(len(d['assets']))+' '+n,flush=True);code=a['theme'];kind=a['kind'];donor=a['donor'];bp=baseline[donor]['properties'];old=native(bp.get('basename',donor));model=copy.deepcopy(old);scale=float(bp.get('scalesod','1').rstrip('fF;'));allparts=[]
 def add(source,size,pos=(0,0,0),yaw=0,stretch=(1,1,1),cap=False):
  rot=np.array([[math.cos(yaw),0,math.sin(yaw)],[0,1,0],[-math.sin(yaw),0,math.cos(yaw)]])
  for p in pieces(source):
   if cap:
    dat=p['data'];valid=[]
    for g in dat['vertex_lighting_groups']:
     g['faces']=[f for f in g['faces']if all(dat['vertices'][vi][1]>.12 for vi,ui in f)]
     if g['faces']:valid.append(g)
    dat['vertex_lighting_groups']=valid
    if not valid:continue
   p['data']['vertices']=(p['data']['vertices']*np.asarray(stretch)*size)@rot.T+pos;allparts.append(p)
 if not model.materials:model.materials.append(copy.deepcopy(native('fbase').materials[0]))
 central=bases[code];tier=d['yards'][code].index(n)if kind=='yard'else 0
 if kind in ['yard','service']:
  add(central,1.2 if n in hero else .86,(0,.13,0));ysource=yards[code];alt=ysource+'2'
  if tier>0 and alt in sods and code!='b':ysource=alt
  length=1.0+min(tier,3)*.09
  for s in [-1,1]:add(ysource,.95,(s*1.05,-.08,.05),yaw=s*(.06 if tier==1 else .12 if tier>=2 else 0),stretch=(1,1,length))
  if code=='f'and n in hero:add(central,1.1,(0,-.72,0),cap=True)
  if tier>=2:add(central,.24,(0,.7,-.16))
  # Solid structural bridges make the twin wings physically join the central hull.
  frame=truss.Geometry()
  for s in [-1,1]:
   for z in [-.13,.13]:frame.beam((0,-.08,z),(s*.98,-.08,z),.045,'hull')
   frame.beam((s*.12,-.21,0),(s*.9,-.21,0),.06,'hull')
  if code=='f'and n in hero:frame.beam((0,-.7,0),(0,.3,0),.07,'hull')
  reference=pieces(ysource)[0]
  for g in frame.parts:
   dat=copy.deepcopy(reference['data']);vv=g['v'];dat.update(vertices=vv,texture_coordinates=[[.5,.5]for v in vv],vertex_lighting_groups=[{'lighting_material':reference['data']['vertex_lighting_groups'][0]['lighting_material'],'faces':[[[int(i),int(i)]for i in face]for face in g['f']]}]);allparts.append({'data':dat,'materials':reference['materials']})
 elif kind=='research':
  add(central,.62,(0,-.05,0));ref=n if n in sods else bp.get('basename',donor);add(ref,.68,(-.58,.1,0));add(ref,.68,(.58,.1,0),yaw=math.pi)
 else:
  # Central starbase stronghold with four thick bastions and raised firing towers.
  add(central,1.0);bastion=bp.get('basename',donor)
  for i in range(4):ang=i*math.tau/4;add(bastion,.48,(.65*math.cos(ang),-.12,.65*math.sin(ang)),yaw=ang)
  add(central,.3,(0,.64,0))
 pts=np.concatenate([p['data']['vertices']for p in allparts]);center=(pts.max(0)+pts.min(0))/2;span=np.ptp(pts,axis=0).max();oldspan=np.ptp(visible_points(old),axis=0).max()*scale;size=400 if kind in ['yard','service']else oldspan
 for node in model.nodes:
  if node['type']=='MESH':node['type']='NULL_OR_HARDPOINT';node['data']=None
 parent=next(v for v in model.nodes if not v['parent']);inv=np.linalg.inv(matrix(parent));chunk=0
 for part in allparts:
  dat=part['data'];mapping={}
  for material in part['materials']:
   ma=copy.deepcopy(material);oldname=ma['name'];ma['name']='tymat_'+str(len(model.materials));model.materials.append(ma);mapping[oldname]=ma['name']
  tex=dat['texture'].lower();assert tex in texidx,('Missing native diffuse texture',n,tex)
  for group in dat['vertex_lighting_groups']:
   for start in range(0,len(group['faces']),150):
    vv=[];uv=[];ff=[]
    for face in group['faces'][start:start+150]:
     base=len(vv)
     for vi,ui in face:
      world=(dat['vertices'][vi]-center)/span*size/scale;vv.append((inv@np.r_[world,1])[:3].tolist());uv.append(dat['texture_coordinates'][ui])
     ff.append([[base+j,base+j]for j in range(3)])
    out=copy.deepcopy(dat);out.update(vertices=vv,texture_coordinates=uv,vertex_lighting_groups=[{'lighting_material':mapping.get(group['lighting_material'],model.materials[0]['name']),'faces':ff}],texture_material='default',bump_map=1,borgification={'texture':dat['texture']});model.nodes.append({'id':'tymesh_'+str(chunk),'parent':parent['id'],'type':'MESH','local_transform':[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],[0.,0.,0.]],'data':out});chunk+=1
 def anchor(hp,pos):
  existing=next((x for x in model.nodes if x['id'].lower()==hp.lower()),None)
  if existing is None:existing={'id':hp,'type':'NULL_OR_HARDPOINT','data':None};model.nodes.append(existing)
  local=(inv@np.r_[np.asarray(pos)/scale,1])[:3];existing.update(parent=parent['id'],local_transform=inv[:3,:3].T.tolist()+[local.tolist()])
 if kind in ['yard','service']:
  for hp,pos in [('tylaunch',(125,0,156.25)),('tyrepair',(-125,0,25)),('tygun1',(-50,25,0)),('tygun2',(50,25,0)),('tygun3',(0,18.75,47.5))]:anchor(hp,pos)
 alias='ty26_'+n;path=O/'SOD'/(alias+'.sod');path.parent.mkdir(parents=True,exist_ok=True);writer=IO();writer.curr_sod_version=model.version
 with contextlib.redirect_stdout(io.StringIO()):writer.write_file(model,str(path))
 displayScale=scale*.875 if kind=='hwp'and code=='b'else scale
 f=O/(baseline[n]['file']if n in baseline else'odf/stations/'+n+'.odf');sourcefile=f if f.exists()else root/baseline[n]['file'];t=sourcefile.read_text(encoding='latin1');t=put(t,'baseName','"'+alias+'"');t=put(t,'ScaleSOD',format(displayScale,'.12g'))
 if kind=='hwp'and code=='b':
  for key in ['footprintBuffer','northBuffer','southBuffer','eastBuffer','westBuffer']:
   if key.lower()in bp:t=put(t,key,format(float(bp[key.lower()].rstrip('fF;'))*.875,'.12g'))
 if kind in ['yard','service']:
  t=put(t,'buildHardpoint','"tylaunch"');t=put(t,'repairHardpoint','"tyrepair"');t=put(t,'footprintBuffer',25)
  for direction in ['northBuffer','southBuffer','eastBuffer','westBuffer']:
   if direction.lower()in bp:t=put(t,direction,format(float(bp[direction.lower()].rstrip('fF;'))*1.25,'.12g'))
 f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));im=preview(model,256);im.save(stage/(n+'-preview.png'));icon=im.convert('RGBA');color=(90,230,155)if kind=='service'else(245,210,65)if kind=='research'else(245,85,70)if kind=='hwp'else(85,175,255);tint=Image.new('RGBA',(256,256));dr=ImageDraw.Draw(tint)
 for y in range(256):dr.line((0,y,255,y),fill=color+(int(y/255*35),))
 icon=Image.alpha_composite(icon,tint);dr=ImageDraw.Draw(icon);dr.rounded_rectangle((2,2,253,253),radius=12,outline=color+(255,),width=6);icon.alpha_composite(symbol('repair'if kind=='service'else'science'if kind=='research'else'defence'if kind=='hwp'else'yard'),(4,4));dr=ImageDraw.Draw(icon);dr.rectangle((6,207,249,249),fill=(8,14,24,245));title='SERVICE'if kind=='service'else'RESEARCH'if kind=='research'else'FORTRESS'if kind=='hwp'else'TWIN YARD';dr.text((60,214),title,font=font,fill=color+(255,));td=O/'Textures/RGB';td.mkdir(parents=True,exist_ok=True);tex='gb'+alias;wf='wf'+alias;icon.resize((64,64),Image.Resampling.LANCZOS).convert('RGB').save(td/(tex+'.tga'));im.resize((64,64),Image.Resampling.LANCZOS).convert('RGB').save(td/(wf+'.tga'))
 for key in ['b_'+n,'b_'+alias]+[u+'w'+str(j)for u in [n,alias]for j in range(1,6)]:sprite=re.sub(r'(?mi)^'+re.escape(key)+r'[ \t]+[^\r\n]*','',sprite)
 sprite+='\n@reference=64\n@tmaterial=default\nb_'+n+' '+tex+' 0 0 64 64\nb_'+alias+' '+tex+' 0 0 64 64\n'
 for u in [n,alias]:
  for j in range(1,6):sprite+=u+'w'+str(j)+' '+wf+' 0 0 64 64\n'
 records.append({**a,'model':alias,'size':size*(.875 if kind=='hwp'and code=='b'else 1),'scale':displayScale,'centralModel':central,'bays':2 if kind in ['yard','service']else 0,'queueCount':1,'nativePodHardpointsPreserved':kind=='research'})
(O/'Sprites').mkdir(parents=True,exist_ok=True);(O/'Sprites/gui_global.spr').write_bytes(sprite.replace('\r','').replace('\n','\r\n').encode('latin1'));(stage/'artwork.json').write_text(json.dumps(records,indent=2));print('Native faction assets complete: '+str(len(records)))
