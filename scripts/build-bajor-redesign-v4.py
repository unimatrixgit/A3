from pathlib import Path
exec(Path('D:/aramada/scripts/install-dominion-three-heroes.py').read_text().split('specials={}')[0])
import copy,numpy as np,hashlib
from PIL import ImageFont
class IO(R):
 def write_anim_reference(self,a,s):
  self.write_uint8(a['type'],s);self.write_string(a['node'],s);self.write_string(a['anim'],s);self.write_float(a['playback_offset'],s)
 def write_unknown_legacy_data(self,d,s):
  if self.curr_sod_version<=1.7:super().write_unknown_legacy_data(d,s)
stage=Path('D:/Xaramada-Modwork/bajor-redesign-v4');stage.mkdir(parents=True,exist_ok=True);before=json.loads((repo/'reports/bajor-redesign-v4-before.json').read_text());donors=json.loads((repo/'reports/bajor-v4-donors.json').read_text());pending={};records=[];cache={}
def matrix(n):
 a=np.eye(4);t=np.array(n['local_transform']);a[:3,:3]=t[:3].T;a[:3,3]=t[3];return a

def components(name):
 if name in cache:return copy.deepcopy(cache[name])
 m=load(root/'SOD'/(name+'.sod'));nodes={n['id'].lower():n for n in m.nodes};memo={}
 def world(n):
  k=n['id'].lower()
  if k in memo:return memo[k]
  a=matrix(n);p=nodes.get(n['parent'].lower());a=world(p)@a if p else a;memo[k]=a;return a
 def chain(n):
  out=[]
  while n and n['id'].lower()not in out:out.append(n['id'].lower());n=nodes.get(n['parent'].lower())
  return out
 visible=[n for n in m.nodes if n['type']=='MESH'and len(n['data']['vertices'])and not any(s in ['borg','damage','shields','shield']for s in chain(n))];lods=[s for n in visible for s in chain(n)if re.fullmatch(r'lod\d+',s)];best=min(lods,key=lambda s:int(s[3:]))if lods else None
 if best:visible=[n for n in visible if best in chain(n)or not any(re.fullmatch(r'lod\d+',s)for s in chain(n))]
 result=[]
 for n in visible:
  data=copy.deepcopy(n['data']);vs=np.array(data['vertices']);data['vertices']=((world(n)@np.c_[vs,np.ones(len(vs))].T).T[:,:3]).tolist();result.append(data)
 assert result,name
 pts=np.concatenate([d['vertices']for d in result]);center=(pts.max(0)+pts.min(0))/2;span=np.ptp(pts,axis=0).max()
 for d in result:d['vertices']=((np.array(d['vertices'])-center)/span).tolist()
 cache[name]=result;return copy.deepcopy(result)
def donor(n):return donors[n].get('basename',n)
def assembly(name):
 ship='/ships/'in before[name]['file'].replace('\\','/').lower();parts=[]
 def add(source,size=1,pos=(0,0,0),stretch=(1,1,1),yaw=0,panels=False):
  a=math.radians(yaw);rot=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
  for d in components(source):
   if panels and d['texture'].lower() not in ['bavarms','baveng','bavphas']:continue
   d['vertices']=((np.array(d['vertices'])*np.array(stretch)*size)@rot.T+pos).tolist();parts.append(d)
 if ship:
  if name in ['bjraider','bjscout']:add('af_bajraider',1);add(donor('cscout'),.22,(0,-.08,-.18),stretch=(.65,.7,1))
  elif name=='bjinterceptor':add('af_bajdestroy',1,stretch=(1.05,.8,.9));add(donor('cscout'),.3,(0,.08,-.1))
  elif name in ['bjfreight','bjcargo','bjtransport','bjcolony','bjconst','xbjuconst','bjrepair']:
   add('af_bajfreight',1,stretch=(.9,1,1.1));type='cconst'if name in ['bjconst','xbjuconst','bjrepair']else'ccargo'if name=='bjcargo'else'ccolony'if name=='bjcolony'else'cfreight'
   for s in [-1,1]:add(donor(type),.34,(s*.16,-.03,-.12),stretch=(.7,1,1))
   if name=='xbjuconst':add(donor('csensor'),.23,(0,.22,0))
  elif name=='bjlightship':
   # Existing sail geometry is retained, supplemented by a detailed Cardassian utility core.
   add(before[name]['basename'],1);add(donor('cscout'),.25,(0,0,0),stretch=(.5,.6,1.2))
  else:
   heavy=name in ['bjbattle','bjsuper','bjnerys'];add('af_bajdestroy',1,stretch=(1.15 if heavy else 1,.9,1.05));add(donor('cbattle2'if heavy else'ccruise1'),.6 if heavy else .42,(0,-.08,-.14),stretch=(.8,1,1))
   for s in [-1,1]:add(donor('cfrigate'),.24 if heavy else .18,(s*.37,.015,-.18),yaw=s*8)
   if name in ['bjartillery','bjtorpedo']:add(donor('cdestroy'),.6,(0,.1,.16),stretch=(.35,.6,1.4))
   if name=='bjspecial':add(donor('csensor'),.3,(0,.18,-.1))
   if name in ['bjsuper','bjnerys']:add(donor('csensor'),.22,(0,.2,0))
 else:
  if name=='bjbase':add('fds9',1);core=.34;radius=.28;ornament='af_bajdestroy'
  elif name=='xbjoutpost':add('af_bajbase',1);core=.23;radius=.2;ornament=donor('cscout')
  elif name.startswith('bjpod'):
   add(donor('carpod1'),.8);add('af_bajdestroy',.42,(0,.08,0),stretch=(1,.5,.8));return parts
  else:
   mapping={'bjyard':'cyard','bjyard2':'cyard2','bjyard3':'cyard2','bjresear':'cresear','bjresear2':'cresear2','bjupgrade':'cupgrade','bjsensor':'csensor','bjsuperlab':'cresear2','bjmining':'cmining','bjorbital':'corbital','bjtrading':'ctrading','bjturret':'cturret','bjturret2':'cturret2','bjhwp':'cbase'}
   add(donor(mapping[name]),1);core=.25 if 'yard'in name else .3;radius=.24 if 'yard'not in name else .32;ornament='af_bajdestroy'
  # Bajoran wing assemblies become armor bastions or spaced docking shoulders.
  angles=[90,270]if 'yard'in name else[0,120,240]
  for a in angles:
   rad=math.radians(a);add(ornament,core,(math.sin(rad)*radius,.025,math.cos(rad)*radius),stretch=(1,.65,1),yaw=a,panels=ornament=='af_bajdestroy')
  if name in ['bjyard3','bjsuperlab']:add(donor('csensor'),.25,(0,.2,0))
 return parts
texidx={p.stem.lower():p for p in(root/'Textures/RGB').glob('*.tga')};texturecache={}
def preview(m,size=400):
 pts=[];triangles=[];nodes={n['id']:n for n in m.nodes}
 def world(n,seen=None):
  seen=set()if seen is None else seen
  if n['id']in seen:return np.eye(4)
  seen.add(n['id']);p=nodes.get(n['parent']);return (world(p,seen) if p else np.eye(4))@matrix(n)
 for n in m.nodes:
  if n['type']!='MESH':continue
  d=n['data'];vs=np.array(d['vertices']);vs=(world(n)@np.c_[vs,np.ones(len(vs))].T).T[:,:3];tex=d['texture'].lower();im=texturecache.get(tex)
  if im is None:
   im=Image.open(texidx[tex]).convert('RGB') if tex in texidx else Image.new('RGB',(1,1),(125,130,140));texturecache[tex]=im
  uv=d['texture_coordinates']
  for g in d['vertex_lighting_groups']:
   for face in g['faces']:
    t=vs[[v[0]for v in face]];screen=np.array([(v[0]+v[2]*.4,-v[1]-v[2]*.62,v[2]-v[1]*1.6)for v in t]);points=screen[:,:2];pts.extend(points);u,v=np.mean([uv[f[1]]for f in face],axis=0);color=np.array(im.getpixel((int(u*im.width)%im.width,int(v*im.height)%im.height)));normal=np.cross(t[1]-t[0],t[2]-t[0]);normal=normal/(np.linalg.norm(normal)+1e-8);light=.35+.65*abs(normal@np.array([.3,.8,.5]));triangles.append((float(screen[:,2].mean()),points,im,np.array([uv[f[1]]for f in face]),light))
 pts=np.array(pts);lo=pts.min(0);hi=pts.max(0);center=(lo+hi)/2;scale=(size-40)/max(hi-lo);canvas=Image.new('RGB',(size,size),(10,15,22));draw=ImageDraw.Draw(canvas)
 for dep,tri,texture,uv,light in sorted(triangles,key=lambda x:x[0]):
  p=(tri-center)*scale+size/2;low=np.maximum(np.floor(p.min(0)).astype(int),0);high=np.minimum(np.ceil(p.max(0)).astype(int)+1,size);w,h=high-low
  if w<=0 or h<=0:continue
  xy=p-low;mat=np.c_[xy,np.ones(3)]
  if abs(np.linalg.det(mat))<.01:continue
  dest=uv*np.array(texture.size);coeff=np.linalg.solve(mat,dest);tile=texture.transform((int(w),int(h)),Image.Transform.AFFINE,(coeff[0,0],coeff[1,0],coeff[2,0],coeff[0,1],coeff[1,1],coeff[2,1]),resample=Image.Resampling.BILINEAR)
  from PIL import ImageEnhance
  tile=ImageEnhance.Brightness(tile).enhance(light);mask=Image.new('L',(int(w),int(h)),0);ImageDraw.Draw(mask).polygon([tuple(q)for q in xy],fill=255);canvas.paste(tile,tuple(low),mask)
 return canvas
for name,d in before.items():
 old=load(root/'SOD'/(d.get('basename',name)+'.sod'));parts=assembly(name);model=copy.deepcopy(old)
 # Existing skeleton and animations remain in place; only visible geometry is replaced.
 for n in model.nodes:
  if n['type']=='MESH':n['type']='NULL_OR_HARDPOINT';n['data']=None
 parent=next(n for n in model.nodes if not n['parent']);parentInv=np.linalg.inv(matrix(parent))
 allp=np.concatenate([p['vertices']for p in parts]);lo=allp.min(0);hi=allp.max(0);center=(lo+hi)/2;partsSpan=max(hi-lo)
 oldpts=[p for tri in mesh_triangles(old)for p in tri];oldpts=np.array(oldpts);oldspan=np.ptp(oldpts,axis=0).max();oldcenter=(oldpts.max(0)+oldpts.min(0))/2
 for i,part in enumerate(parts):
  worldvs=(np.array(part['vertices'])-center)/partsSpan*oldspan+oldcenter;part['vertices']=((parentInv@np.c_[worldvs,np.ones(len(worldvs))].T).T[:,:3]).tolist();part.setdefault('bump_map',0);part.setdefault('texture_material','default');part.setdefault('borgification',{'texture':part['texture']+'_B'});part.setdefault('cull_type',0)
  if part['texture'].lower()not in texidx:raise ValueError(('missing texture',name,part['texture']))
  borg=part.get('borgification',{}).get('texture')
  if borg and borg.lower()not in texidx:part['borgification']['texture']=part['texture']
  model.nodes.append({'type':'MESH','id':'bv4_'+str(i),'parent':parent['id'],'local_transform':[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],[0.,0.,0.]],'data':part})
 alias='bv4_'+name;rel='SOD/'+alias+'.sod';out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True)
 writer=IO();writer.curr_sod_version=model.version
 with contextlib.redirect_stdout(io.StringIO()):writer.write_file(model,str(out))
 reload=load(out);assert len(reload.nodes)==len(model.nodes);assert len(reload._animation_transforms)==len(old._animation_transforms)
 odf=Path(d['file']);relodf=str(odf.relative_to(root));t=put(odf.read_text(encoding='latin1'),'baseName','"'+alias+'"');pending[relodf]=t
 # Render the complete new textured model for matching GUI buttons.
 im=preview(model,320);thumb=im.resize((64,64),Image.Resampling.LANCZOS);thumbpath=stage/'Textures/RGB'/('gb'+alias+'.tga');thumbpath.parent.mkdir(parents=True,exist_ok=True);thumb.save(thumbpath)
 wfpath=stage/'Textures/RGB'/('wf'+alias+'.tga');im.resize((256,256),Image.Resampling.LANCZOS).save(wfpath)
 for key in ['b_'+name]+[name+'w'+str(i)for i in range(1,6)]:sprite=re.sub(r'(?mi)^'+key+r'[ \t]+[^\r\n]*','',sprite)
 sprite+='\n@reference=64\n@tmaterial=default\nb_'+name+' gb'+alias+' 0 0 64 64\n@reference=256\n'
 for i in range(1,6):sprite+=name+'w'+str(i)+' wf'+alias+' 0 0 256 256\n'
 if name in ['bjinterceptor','bjassault','bjbattle','bjnerys','bjfreight','bjconst','bjyard2','bjresear2','bjbase','bjorbital','bjhwp','xbjoutpost']:
  im.save(stage/(name+'-preview.png'))
 records.append({'unit':name,'name':d['unitname'],'parts':len(parts),'model':alias,'oldModel':d.get('basename',name),'sourceODFSha256':hashlib.sha256(odf.read_bytes()).hexdigest(),'animationsPreserved':len(old._animation_transforms),'sourcePath':relodf});print(name,len(parts),flush=True)
pending['Sprites/gui_global.spr']=sprite
for rel,t in pending.items():out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'))
(stage/'manifest.json').write_text(json.dumps({'units':records,'applied':False,'runtimeVerified':False,'sourceSpriteSha256':hashlib.sha256((root/'Sprites/gui_global.spr').read_bytes()).hexdigest()},indent=2))
selected=['bjinterceptor','bjassault','bjbattle','bjfreight','bjconst','bjnerys','bjbase','bjyard2','bjresear2','bjorbital','bjhwp','xbjoutpost'];sheet=Image.new('RGB',(1200,1460),(10,15,22));draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19);title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',28);draw.text((25,15),'BAJORAN MILITIA — CUSTOM REDESIGN',font=title,fill=(222,183,118));draw.text((25,52),'Bajoran hulls • Cardassian machinery • actual staged game models',font=font,fill=(165,180,193))
for i,n in enumerate(selected):x=(i%3)*400;y=100+(i//3)*340;im=Image.open(stage/(n+'-preview.png')).resize((320,300));sheet.paste(im,(x+40,y));draw.text((x+20,y+302),before[n]['unitname'][:36],font=font,fill=(222,183,118))
sheet.save(stage/'Bajoran-redesign-preview.png');print('STAGED',len(records),'units; preview',stage/'Bajoran-redesign-preview.png')





