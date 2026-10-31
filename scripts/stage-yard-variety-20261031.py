from pathlib import Path
import sys,re,json,copy,contextlib,io,math,hashlib,datetime,subprocess
import numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils')
from sod_io import SodIO
class IO(SodIO):
 def read_unknown_legacy_data(self,s):return []if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
 def write_unknown_legacy_data(self,d,s):
  if self.curr_sod_version<=1.7:super().write_unknown_legacy_data(d,s)
 def write_anim_reference(self,a,s):
  self.write_uint8(a['type'],s);self.write_string(a['node'],s);self.write_string(a['anim'],s);self.write_float(a['playback_offset'],s)
root=Path('D:/armadaIII');repo=Path('D:/aramada');stage=repo/'patches/yard-variety-20261031';overlay=stage/'overlay';overlay.mkdir(parents=True,exist_ok=True)
exec((repo/'scripts/audit-borg-sequence-20261028.py').read_text(encoding='utf-8-sig').split('reports=[]')[0])
texidx={p.stem.lower():p for p in(root/'Textures').rglob('*')if p.suffix.lower()in['.tga','.bmp']};texturecache={}
sods={p.stem.lower():p for p in(root/'SOD').glob('*')if p.suffix.lower()=='.sod'};native={p.stem.lower():p for p in Path('D:/Xaramada/SOD').glob('*')if p.suffix.lower()=='.sod'}
def load(p):
 with contextlib.redirect_stdout(io.StringIO()):return IO().read_file(str(p))
def matrix(n):
 a=np.eye(4);t=np.array(n['local_transform']);a[:3,:3]=t[:3].T;a[:3,3]=t[3];return a
exec((repo/'scripts/twin-yard-render.py').read_text())
partcache={}
def parts(name):
 if name in partcache:return copy.deepcopy(partcache[name])
 m=load(native.get(name,sods.get(name)));nodes={n['id'].lower():n for n in m.nodes};memo={}
 def chain(n):
  c=[]
  while n and n['id'].lower()not in c:c.append(n['id'].lower());n=nodes.get(n['parent'].lower())
  return c
 worlds={};byid={}
 for node in m.nodes:
  w=byid.get(node['parent'].lower(),np.eye(4))@matrix(node);worlds[id(node)]=w;byid[node['id'].lower()]=w
 def world(n):return worlds[id(n)]
 visible=[n for n in m.nodes if n['type']=='MESH'and len(n['data']['vertices'])and not any(x in ['borg','damage','shields','shield']for x in chain(n))]
 lods=[x for n in visible for x in chain(n)if re.fullmatch(r'lod\d+',x)];best=min(lods,key=lambda x:int(x[3:]))if lods else None
 if best:visible=[n for n in visible if best in chain(n)or not any(re.fullmatch(r'lod\d+',x)for x in chain(n))]
 result=[]
 for n in visible:
  d=copy.deepcopy(n['data']);v=np.asarray(d['vertices']);d['vertices']=((world(n)@np.c_[v,np.ones(len(v))].T).T[:,:3]);result.append(d)
 assert result,name
 v=np.concatenate([d['vertices']for d in result]);center=(v.max(0)+v.min(0))/2;span=np.ptp(v,axis=0).max()
 for d in result:d['vertices']=(d['vertices']-center)/span
 partcache[name]=(result,m.materials);return copy.deepcopy(partcache[name])
design=json.loads((repo/'patches/twin-yards-20261025/design.json').read_text());records=[];previews=[]
for name,a in design['assets'].items():
 if a['kind']!='yard':continue
 d=cache[name];old=load(sods[d.get('basename',name).lower()]);model=copy.deepcopy(old);code=a['theme'];tier=design['yards'][code].index(name)if a['kind']=='yard'else -1
 prefix={'bj':'c','fg':'r','bg':'b','br':'br'}.get(code,code);base=prefix+'yard';advanced=prefix+'yard2';command=prefix+'base'
 if code=='bj':command='bjbase'
 assembled=[];materials=[]
 def add(src,size,pos=(0,0,0),stretch=(1,1,1),yaw=0):
  pp,mm=parts(src);materials.extend(mm);ang=math.radians(yaw);rot=np.array([[math.cos(ang),0,math.sin(ang)],[0,1,0],[-math.sin(ang),0,math.cos(ang)]])
  for p in pp:p['vertices']=(p['vertices']*np.array(stretch)*size)@rot.T+np.array(pos);assembled.append(p)
 if tier==0:add(base,1)
 elif tier==1:add(advanced,1,stretch=(1.15,1,.85));add(prefix+'resear',.22,(0,.35,-.25))
 elif tier==2:add(advanced,1.2);add(command,.48,(0,.45,-.22),stretch=(1,.75,1))
 elif tier==3:
  add(base,.68,(-.42,0,0),yaw=90);add(advanced,.68,(.42,0,0),yaw=-90);add(command,.4,(0,.25,-.25))
 elif tier==4:add(advanced,1,stretch=(.8,1.3,1.15),yaw=90);add(prefix+'resear2',.35,(0,.4,0))
 elif tier>=5:
  for side in [-1,1]:add(base,.65,(side*.4,0,side*.12),yaw=side*30)
  add(command,.5,(0,.35,0),yaw=45 if tier==6 else 0)
  if tier==6:add(advanced,.5,(0,-.1,-.4),yaw=90)
 else:add(base,.95,stretch=(.8,.8,1.2));add(prefix+'resear',.36,(.28,.25,-.3))
 # Ferengi use their own saucer hull as a command module; assimilated version retains Borg materials.
 if code=='fg':add('xfgdaim',.35,(0,.35,0),stretch=(1,.5,1))
 for n in model.nodes:
  if n['type']=='MESH':n['type']='NULL_OR_HARDPOINT';n['data']=None
 parent=next(n for n in model.nodes if not n['parent']);inv=np.linalg.inv(matrix(parent))
 # Retain the previous full visual envelope and every original functional hardpoint.
 oldworld=[];worlds={}
 for n in old.nodes:
  w=worlds.get(n['parent'].lower(),np.eye(4))@matrix(n);worlds[n['id'].lower()]=w
  if n['type']=='MESH':
   v=np.array(n['data']['vertices']);oldworld.extend(((w@np.c_[v,np.ones(len(v))].T).T[:,:3]).tolist())
 ov=np.array(oldworld);center=(ov.max(0)+ov.min(0))/2;span=np.ptp(ov,axis=0).max();v=np.concatenate([p['vertices']for p in assembled]);mid=(v.max(0)+v.min(0))/2;factor=span/np.ptp(v,axis=0).max()
 known={m['name']for m in model.materials}
 for m in materials:
  if m['name']not in known:model.materials.append(copy.deepcopy(m));known.add(m['name'])
 for i,p in enumerate(assembled):
  v=(p['vertices']-mid)*factor+center;p['vertices']=((inv@np.c_[v,np.ones(len(v))].T).T[:,:3]).tolist();tex=p['texture'].lower();assert tex in texidx,(name,tex)
  p.setdefault('borgification',{'texture':p['texture']});p.setdefault('bump_map',0);p.setdefault('cull_type',0)
  borg=p.get('borgification',{}).get('texture','').lower()
  if borg and borg not in texidx:p['borgification']['texture']=p['texture']
  model.nodes.append({'type':'MESH','id':'yv31_'+str(i),'parent':parent['id'],'local_transform':[[1.,0,0],[0,1.,0],[0,0,1.],[0,0,0]],'data':p})
 alias='yv31_'+name;rel=Path('SOD')/(alias+'.sod');out=overlay/rel;out.parent.mkdir(parents=True,exist_ok=True)
 writer=IO();writer.curr_sod_version=model.version
 with contextlib.redirect_stdout(io.StringIO()):writer.write_file(model,str(out))
 check=load(out);assert len(check.nodes)==len(model.nodes);assert len(check._animation_transforms)==len(old._animation_transforms)
 for oldn,newn in zip(old.nodes,check.nodes):assert oldn['id']==newn['id']and oldn['local_transform']==newn['local_transform']
 odfrel=idx[name].relative_to(root);s=idx[name].read_text(encoding='latin1');s=re.sub(r'(?mi)^\s*baseName\s*=[^\r\n]*','',s).rstrip()+'\r\nbaseName = "'+alias+'"\r\n';op=overlay/odfrel;op.parent.mkdir(parents=True,exist_ok=True);op.write_bytes(s.encode('latin1'))
 records.append({'unit':name,'model':rel.as_posix(),'odf':odfrel.as_posix(),'tier':tier,'meshes':len(assembled),'oldOdfSha256':hashlib.sha256(idx[name].read_bytes()).hexdigest()})
 if code=='f'or tier in [0,2]or(code in ['fg','bg','bj']):
  im=preview(check,240);previews.append((name,im))
 print('Validated',name,flush=True)
cols=5;sheet=Image.new('RGB',(cols*240,math.ceil(len(previews)/cols)*270),(12,17,25));dr=ImageDraw.Draw(sheet)
for i,(n,im)in enumerate(previews):x=i%cols*240;y=i//cols*270;sheet.paste(im,(x,y));dr.text((x+10,y+243),n,fill='white')
sheet.save(stage/'preview.png');(stage/'manifest.json').write_text(json.dumps({'units':records,'runtimeVerified':False,'scope':'Native faction yard hull variety; original functional skeletons, animation count and gameplay stats preserved. Only baseName changes in ODFs.'},indent=2)+'\n')
print('Ready',len(records))

