from pathlib import Path
import re,json,copy,hashlib,datetime,subprocess,contextlib,io,sys,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
repo=Path('D:/aramada');root=Path('D:/armadaIII');external=Path('D:/Xaramada-Modwork/armadafiles-yard-replacements');stage=repo/'patches/armadafiles-yards-20261031';overlay=stage/'overlay';overlay.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils');from sod_io import SodIO
class IO(SodIO):
 def read_unknown_legacy_data(self,s):return []if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
 def write_unknown_legacy_data(self,d,s):
  if self.curr_sod_version<=1.7:super().write_unknown_legacy_data(d,s)
 def write_anim_reference(self,a,s):
  self.write_uint8(a['type'],s);self.write_string(a['node'],s);self.write_string(a['anim'],s);self.write_float(a['playback_offset'],s)
def load(p):
 with contextlib.redirect_stdout(io.StringIO()):return IO().read_file(str(p))
def matrix(n):
 a=np.eye(4);t=np.asarray(n['local_transform']);a[:3,:3]=t[:3].T;a[:3,3]=t[3];return a
exec((repo/'scripts/audit-borg-sequence-20261028.py').read_text(encoding='utf-8-sig').split('reports=[]')[0])
exec((repo/'scripts/twin-yard-render.py').read_text());texidx={p.stem.lower():p for p in(root/'Textures').rglob('*')if p.suffix.lower()in['.tga','.bmp']};texturecache={};sods={p.stem.lower():p for p in(root/'SOD').glob('*')if p.suffix.lower()=='.sod'}
base=external/'extracted';packages={p.name:p for p in base.iterdir()if p.is_dir()};packagefiles={n:[p for p in folder.rglob('*')if p.is_file()]for n,folder in packages.items()}
def source(pack,model):
 return next(p for p in packagefiles[pack]if p.suffix.lower()=='.sod'and p.stem.lower()==model.lower()and('A1'not in p.parts))
BI='borg-incursion-2';SP='space-dock';FAD='federation-advanced-yard-10';NE='nemesis-yard';SF='san-francisco-shipyard';AN='antaries-shipyard';FN='federation-nemesis-style-yard-10';BO='borg-station-pack';KL='klingon-stationpack-2';KO='klingon-shipyards';RO='romulanstationpack-10';CA='cardassian-advanced-yard';MO='monak-shipyard';BR='dominion-ultimate-12-the-breen';FE='ferengi-salvage-team';SX='species-8472-pack-07-research-stations-and-fluidic-gate-10'
choices={'federation':[(SF,'sanfranyard'),(FAD,'fyard2'),(NE,'fmyard'),(AN,'fyard2'),(FN,'fyard3'),(SP,'fdock2'),(SP,'fdock3')], 'borg':[(BO,'byard'),(BO,'byard2'),(BI,'byard3')],'klingon':[(KL,'kyard'),(KO,'kyard2'),(KO,'kyard')],'romulan':[(BI,'ryard3'),(RO,'ryard2'),(BI,'ryard3')],'cardassian':[(BI,'cyard'),(CA,'cyard2'),(MO,'cyard4')],'dominion':[(BI,'domyard')],'bajoran':[(MO,'cyard4'),(CA,'cyard2'),(BI,'cobyard')],'breen':[(BR,'bryard'),(BR,'bryard2')],'ferengi':[(FE,'fgyard'),(FE,'fgyard2')],'species8472':[(BI,'714syard'),(SX,'8472_fluidicgate')]}
order=json.loads((repo/'patches/twin-yards-20261025/design.json').read_text())['yards'];ordered={n:i for v in order.values()for i,n in enumerate(v)}
font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',13);sprite=(root/'Sprites/gui_global.spr').read_text(encoding='latin1');spritehash=hashlib.sha256((root/'Sprites/gui_global.spr').read_bytes()).hexdigest();records=[];previews=[];texturemap={}
def world_nodes(m):
 worlds={};byid={}
 for node in m.nodes:
  w=byid.get(node['parent'].lower(),np.eye(4))@matrix(node);worlds[id(node)]=w;byid[node['id'].lower()]=w
 return worlds,byid
def bounds(m):
 worlds,_=world_nodes(m);arr=[]
 for n in m.nodes:
  if n['type']=='MESH'and len(n['data']['vertices']):
   v=np.asarray(n['data']['vertices']);arr.append((worlds[id(n)]@np.c_[v,np.ones(len(v))].T).T[:,:3])
 assert arr
 v=np.concatenate(arr);return(v.min(0),v.max(0))
def texture(pack,name):
 key=(pack,name.lower())
 if key in texturemap:return texturemap[key]
 candidates=[p for p in packagefiles[pack]if p.stem.lower()==name.lower()and p.suffix.lower()=='.tga'and not any(x in str(p).lower()for x in ['admirals','shipimages'])]
 live=[p for p in(root/'Textures/RGB').glob('*')if p.stem.lower()==name.lower()and p.suffix.lower()=='.tga']
 src=candidates[0]if candidates else live[0]if live else None;assert src,('Missing hull TGA; do not substitute a thumbnail',pack,name)
 data=src.read_bytes();alias='ay31t'+hashlib.sha256(data).hexdigest()[:12];rel=Path('Textures/RGB')/(alias+src.suffix.lower());out=overlay/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);texidx[alias]=out;texturemap[key]=(alias,rel.as_posix());return texturemap[key]
targets=[]
for n,d in cache.items():
 if idx[n].parent.name.lower()!='stations' or d.get('classlabel','').lower()!='shipyard':continue
 if n.startswith('xvstock')or n.startswith('xyr_')or n in ['fremmeler','mysyard']:continue
 if('yard'in n or n.startswith('mry')or n in ['8472_fluidicgate','xfgmerc','xfgserv','xbgmerc','xbgserv']):targets.append(n)
for n in sorted(targets):
 d=cache[n];race=d.get('race','').lower();assert race in choices,(n,race);tier=ordered.get(n,2 if n.startswith('mry')else(1 if n.endswith('2')or n=='8472_fluidicgate'else 2 if n.endswith('3')else 0));options=choices[race];pack,modelname=options[tier%len(options)];src=source(pack,modelname);m=load(src);old=load(sods[d.get('basename',n).lower()]);lo,hi=bounds(m);olo,ohi=bounds(old);span=max(hi-lo);oldspan=max(ohi-olo);scale=float(d.get('scalesod','1').rstrip('fF'))*oldspan/span;assert scale>0
 # Each yard uses exactly one downloaded model. No additional hulls are added.
 for node in m.nodes:
  if node['type']=='MESH':
   q=node['data'];q['texture']=texture(pack,q['texture'])[0]
   if q.get('borgification',{}).get('texture'):
    try:q['borgification']['texture']=texture(pack,q['borgification']['texture'])[0]
    except AssertionError:q['borgification']['texture']=q['texture']
 # Native model skeleton and animations retained; provide aliases for current gameplay hardpoints.
 worlds,byid=world_nodes(m);nodes={v['id'].lower():v for v in m.nodes};parent=next(v for v in m.nodes if not v['parent']);pinv=np.linalg.inv(byid[parent['id'].lower()]);ow,oid=world_nodes(old);oldnodes={v['id'].lower():v for v in old.nodes}
 candidates=[p for p in packagefiles[pack]if p.suffix.lower()=='.odf'and p.stem.lower()==modelname.lower()];donor={}
 if candidates:
  for k,v in re.findall(r'(?mi)^\s*(\w+)\s*=\s*([^\r\n]*)',candidates[0].read_text(encoding='latin1')):donor[k.lower()]=v.split('//')[0].strip().strip('"')
 needed={v.lower()for k,value in d.items()if k in ['buildhardpoint','repairhardpoint']or re.fullmatch('weaponhardpoints[0-9]+',k)for v in re.findall(r'[\w]+',value)}
 anchors=[]
 for hp in sorted(needed):
  if hp in nodes:continue
  role='build'if hp==d.get('buildhardpoint','').lower()else'repair'if hp==d.get('repairhardpoint','').lower()else'weapon'
  nativehp=donor.get(role+'hardpoint',role).lower();nativehp=next((h for h in [nativehp,role,role+'01']if h in byid),None)if role!='weapon'else None
  if nativehp:pos=byid[nativehp][:3,3]
  elif role in ['build','repair']:pos=(lo+hi)/2;pos=pos.copy();pos[2]=(hi[2]+span*.15)if role=='build'else(lo[2]-span*.15)
  elif hp in oldnodes:pos=(ow[id(oldnodes[hp])][:3,3]-(olo+ohi)/2)*(span/oldspan)+(lo+hi)/2
  else:pos=(lo+hi)/2
  local=(pinv@np.r_[pos,1])[:3];m.nodes.append({'type':'NULL_OR_HARDPOINT','id':hp,'parent':parent['id'],'local_transform':[[1.,0,0],[0,1.,0],[0,0,1.],local.tolist()],'data':None});anchors.append(hp)
 alias='ay31_'+n;rel=Path('SOD')/(alias+'.sod');out=overlay/rel;out.parent.mkdir(parents=True,exist_ok=True);writer=IO();writer.curr_sod_version=m.version
 with contextlib.redirect_stdout(io.StringIO()):writer.write_file(m,str(out))
 check=load(out);assert len(check.nodes)==len(m.nodes)and len(check._animation_transforms)==len(m._animation_transforms)
 assert needed<={v['id'].lower()for v in check.nodes},(n,needed)
 text=idx[n].read_text(encoding='latin1')
 for key,val in [('baseName','"'+alias+'"'),('ScaleSOD',format(scale,'.12g'))]:text=re.sub(r'(?mi)^\s*'+key+r'\s*=[^\r\n]*','',text).rstrip()+'\r\n'+key+' = '+val+'\r\n'
 odfrel=idx[n].relative_to(root);odfout=overlay/odfrel;odfout.parent.mkdir(parents=True,exist_ok=True);odfout.write_bytes(text.encode('latin1'))
 im=preview(check,200);small=im.resize((64,64),Image.Resampling.LANCZOS);icon=small.copy();dr=ImageDraw.Draw(icon);dr.rectangle((0,0,63,63),outline=(110,175,210),width=2);dr.text((51,46),str(min(tier+1,9)),font=font,fill='white')
 for tex,img in [('gb'+alias,icon),('wf'+alias,small)]:
  p=overlay/'Textures/RGB'/(tex+'.tga');p.parent.mkdir(parents=True,exist_ok=True);img.convert('RGB').save(p)
 keys=['b_'+n,'b_'+alias]+[u+'w'+str(i)for u in[n,alias]for i in range(1,6)]
 for key in keys:sprite=re.sub(r'(?mi)^'+re.escape(key)+r'[ \t]+[^\r\n]*','',sprite)
 sprite+='\n@reference=64\n@tmaterial=default\nb_'+n+' gb'+alias+' 0 0 64 64\nb_'+alias+' gb'+alias+' 0 0 64 64\n'
 for u in[n,alias]:
  for j in range(1,6):sprite+=u+'w'+str(j)+' wf'+alias+' 0 0 64 64\n'
 records.append({'unit':n,'race':race,'package':pack,'sourceModel':str(src),'model':rel.as_posix(),'odf':odfrel.as_posix(),'oldOdfSha256':hashlib.sha256(idx[n].read_bytes()).hexdigest(),'scale':scale,'addedHardpointAliases':anchors,'spriteAliases':keys});previews.append((n,im));print('Validated',n,pack,flush=True)
p=overlay/'Sprites/gui_global.spr';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(sprite.replace('\r','').replace('\n','\r\n').encode('latin1'))
cols=6;sheet=Image.new('RGB',(cols*200,math.ceil(len(previews)/cols)*230),(10,15,24));dr=ImageDraw.Draw(sheet)
for i,(n,im)in enumerate(previews):x=i%cols*200;y=i//cols*230;sheet.paste(im,(x,y));dr.text((x+10,y+202),n,fill='white')
sheet.save(stage/'preview.png');(stage/'manifest.json').write_text(json.dumps({'units':records,'textureDefinitions':[{'package':k[0],'original':k[1],'renamed':v[0],'file':v[1]}for k,v in texturemap.items()],'sourceSpriteSha256':spritehash,'runtimeVerified':False,'repairDocksPreserved':True,'geometry':'Exactly one downloaded model per yard; no merged hulls. Only texture names and required hardpoint aliases changed in models.'},indent=2)+'\n');print('READY',len(records))

