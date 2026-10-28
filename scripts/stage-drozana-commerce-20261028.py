"""Stage Drozana-inspired commerce and Borg-only assimilated freighter foundry."""
from pathlib import Path
import re,json,sys,math,copy,contextlib,io,importlib.util,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
repo=Path('D:/aramada');root=Path('D:/armadaIII');stage=repo/'patches/drozana-commerce-20261028';O=stage/'overlay';O.mkdir(parents=True,exist_ok=True)
exec((repo/'scripts/audit-borg-sequence-20261028.py').read_text(encoding='utf-8-sig').split('reports=[]')[0])
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils');from sod_io import SodIO
class IO(SodIO):
 def read_unknown_legacy_data(self,s):return []if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
 def write_unknown_legacy_data(self,d,s):
  if self.curr_sod_version<=1.7:super().write_unknown_legacy_data(d,s)
 def write_anim_reference(self,a,s):
  self.write_uint8(a['type'],s);self.write_string(a['node'],s);self.write_string(a['anim'],s);self.write_float(a['playback_offset'],s)
spec=importlib.util.spec_from_file_location('geometry',repo/'scripts/approved-station-geometry.py');geometry=importlib.util.module_from_spec(spec);spec.loader.exec_module(geometry)
textures={p.stem.lower():p for p in(root/'Textures').rglob('*.tga')};models={};records=[]
def load(name):
 with contextlib.redirect_stdout(io.StringIO()):return IO().read_file(str(root/'SOD'/(name+'.sod')))
def worlds(m):
 out=[];last={};data={};chains={}
 for n in m.nodes:
  t=np.array(n['local_transform']);a=np.eye(4);a[:3,:3]=t[:3].T;a[:3,3]=t[3];i=last.get(n['parent'].lower());a=(out[i]if i is not None else np.eye(4))@a;chain=(chains.get(i,[])if i is not None else[])+[n['id'].lower()];chains[len(out)]=chain;out.append(a);last[n['id'].lower()]=len(out)-1;data[id(n)]=(a,chain)
 return data
def visible(m):
 w=worlds(m);out=[];lods={x for a,c in w.values()for x in c if re.fullmatch('lod[0-9]+',x)};best=min(lods,key=lambda x:int(x[3:]))if lods else None
 for n in m.nodes:
  if n['type']=='MESH'and not any(x in ['borg','damage','shield','shields']or(re.fullmatch('lod[0-9]+',x)and x!=best)for x in w[id(n)][1]):
   v=np.asarray(n['data']['vertices']);out.append((n,(w[id(n)][0]@np.c_[v,np.ones(len(v))].T).T[:,:3]))
 return out
def put(t,k,v):
 pat=r'(?mi)^[ \t]*'+k+r'[ \t]*=[^\r\n]*';line=k+' = '+str(v)
 return re.sub(pat,lambda m:line,t)if re.search(pat,t)else t.rstrip()+'\n'+line+'\n'
def save(rel,t):
 p=O/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'))
def anchor(m,name,pos):
 parent=next(n for n in m.nodes if not n['parent']);inv=np.linalg.inv(worlds(m)[id(parent)][0]);local=(inv@np.r_[pos,1])[:3]
 m.nodes.append({'id':name,'parent':parent['id'],'type':'NULL_OR_HARDPOINT','local_transform':inv[:3,:3].T.tolist()+[local.tolist()],'data':None})
def append_geometry(m,g,donor,prefix):
 native=load(donor);reference=max(visible(native),key=lambda p:len(p[1]))[0]['data'];material=copy.deepcopy(native.materials[0]if native.materials else m.materials[0]);material['name']=prefix+'material';m.materials.append(material)
 parent=next(n for n in m.nodes if not n['parent']);inv=np.linalg.inv(worlds(m)[id(parent)][0]);templates=[]
 for group in reference['vertex_lighting_groups']:
  for face in group['faces']:templates.append([reference['texture_coordinates'][ui]for vi,ui in face])
 assert templates and reference['texture'].lower()in textures
 for partno,part in enumerate(g.parts):
  for start in range(0,len(part['f']),120):
   vv=[];uv=[];ff=[]
   for fi,face in enumerate(part['f'][start:start+120]):
    v=np.asarray(part['v'])[list(face)];v=(inv@np.c_[v,np.ones(3)].T).T[:,:3];at=len(vv);vv.extend(v.tolist());uv.extend(templates[(start+fi)%len(templates)]);ff.append([[at+j,at+j]for j in range(3)])
   d=copy.deepcopy(reference);d.update(vertices=vv,texture_coordinates=uv,texture_material='opaque',bump_map=1,borgification={'texture':reference['texture']},vertex_lighting_groups=[{'lighting_material':material['name'],'faces':ff}]);m.nodes.append({'id':prefix+str(partno)+'_'+str(start),'parent':parent['id'],'type':'MESH','local_transform':[[1,0,0],[0,1,0],[0,0,1],[0,0,0]],'data':d})
def export(name,m):
 p=O/'SOD'/(name+'.sod');p.parent.mkdir(parents=True,exist_ok=True);w=IO();w.curr_sod_version=m.version
 with contextlib.redirect_stdout(io.StringIO()):w.write_file(m,str(p));check=IO().read_file(str(p))
 assert len(check.nodes)==len(m.nodes);models[name]=m
# K7-family central spindle, three radial booms and tiered outboard commerce modules.
for name,borg in [('xfdrozana',False),('xbdrozana',True)]:
 m=load('xvstock_ftrading')
 for n in m.nodes:
  if n['type']=='MESH':n['type']='NULL_OR_HARDPOINT';n['data']=None
 g=geometry.Geometry();g.cylinder((0,0,0),47,70,n=24,top=.8);g.cylinder((0,48,0),34,28,n=24,top=.5);g.cylinder((0,83,0),8,45,n=12,top=.2);g.cylinder((0,-65,0),22,75,n=16,top=1.5)
 for i in range(3):
  a=i*math.tau/3;end=np.array([145*math.cos(a),-9,145*math.sin(a)]);g.beam((0,-7,0),end,19)
  for y,r,h in [(-25,42,18),(-5,53,22),(16,44,20),(36,25,20)]:g.cylinder(end+[0,y,0],r,h,n=24,top=.78)
  g.cylinder(end+[0,58,0],7,30,n=10,top=.2)
 if borg:
  for a in np.linspace(0,math.tau,6,endpoint=False):g.box((45*math.cos(a),12,45*math.sin(a)),(23,30,23));g.beam((0,50,0),(85*math.cos(a),-5,85*math.sin(a)),8)
 append_geometry(m,g,'xvstock_bbase'if borg else'xvstock_fbase',name)
 for hp,pos in [('dzlaunch',(0,0,235)),('dzbeam1',(-35,20,0)),('dzbeam2',(35,20,0)),('dzcargo',(0,-25,190))]:anchor(m,hp,pos)
 export(name,m)
 t=idx['xbgmerc'if borg else'ftrading'].read_text(encoding='latin1');t=re.sub(r'(?mi)^\s*(?:weapon(?:Hardpoints)?\d+|buildItem\d+)[ \t]*=[^\r\n]*','',t)
 values={'unitName':'"Assimilated Drozana Foundry"'if borg else'"Drozana Commerce Exchange"','tooltip':'"Assimilated Drozana Foundry"'if borg else'"Drozana Commerce Exchange"','race':'"borg"'if borg else'"ferengi"','baseName':'"'+name+'"','ScaleSOD':1,'footprintBuffer':35,'classLabel':'"shipyard"'if borg else'"trading_station"','builder_ship':1 if borg else 0,'repairFacility':0,'decommissionFacility':0,'maxHealth':2400 if borg else 1800,'shieldRate':24 if borg else 18,'crewCost':200 if borg else 100,'maximumCrew':600 if borg else 300,'officerCost':8 if borg else 6,'buildTime':75 if borg else 60,'dilithiumCost':650 if borg else 0,'metalCost':500 if borg else 0,'latinumCost':0 if borg else 700,'buildHardpoint':'"dzlaunch"','cargoTransferRate':50,'percentTradeProfit':15,'alwaysRecomputeRallyPoint':0,'verboseTooltip':'"Borg-only foundry. Produces assimilated combat freighters from nine faction hulls."'if borg else'"Ferengi-operated Drozana-inspired trade hub. Standard cargo handling; doubled trade cargo value."'}
 for k,v in values.items():t=put(t,k,v)
 if borg:
  for i in [1,2]:t=put(t,'weapon'+str(i),'"bt3phas"');t=put(t,'weaponHardpoints'+str(i),'"dzbeam'+str(i)+'"')
 save(Path('odf/stations')/(name+'.odf'),t)
# Assimilated combat vessels, never cargo/mining AI.
ships={'f':'ffreight','k':'kfreight','r':'rfreight','c':'cfreight','d':'dfreight','b':'bfreight','bj':'bjfreight','br':'brfreight','fg':'xfgmine'}
names={'f':'Federation','k':'Klingon','r':'Romulan','c':'Cardassian','d':'Dominion','b':'Borg','bj':'Bajoran','br':'Breen','fg':'Ferengi'}
for code,donor in ships.items():
 name='xdz'+code;d=cache[donor];m=load(d.get('basename',donor));points=np.concatenate([v for n,v in visible(m)]);lo=points.min(0);hi=points.max(0);size=hi-lo;mid=(lo+hi)/2;g=geometry.Geometry()
 for side in [-1,1]:
  pos=mid+np.array([side*size[0]*.26,size[1]*.31,0]);g.box(pos,(max(size[0]*.19,2),max(size[1]*.3,2),max(size[2]*.5,2)));g.beam(pos-[0,0,size[2]*.36],pos+[0,0,size[2]*.36],max(size.max()*.025,.8))
 append_geometry(m,g,'xvstock_bbase','assimarmor')
 for hp,pos in [('dzbeam1',mid+[-size[0]*.3,0,size[2]*.25]),('dzbeam2',mid+[size[0]*.3,0,size[2]*.25]),('dztorp',mid+[0,0,size[2]*.48])]:anchor(m,hp,pos)
 export(name,m)
 health=max(1000,round(float(d.get('maxhealth','500').rstrip('fF'))*1.75));crew=max(150,min(500,int(float(d.get('crewcost','100')))*2));t='#include "battle.odf"\n';values={'unitName':'"Assimilated '+names[code]+' Freighter"','tooltip':'"Assimilated '+names[code]+' Freighter"','verboseTooltip':'"Borg combat conversion: two beams, torpedo, blue Auto-Assimilator, Transwarp and Regeneration. Existing Borg ability research applies."','race':'"borg"','baseName':'"'+name+'"','ScaleSOD':d.get('scalesod','1'),'physicsFile':'"'+d.get('physicsfile','sfreightphys.odf')+'"','maxHealth':health,'shieldRate':health/100,'maxSpecialEnergy':3000,'specialEnergyRate':85,'crewCost':crew,'maximumCrew':max(500,crew),'officerCost':6,'dilithiumCost':450,'metalCost':250,'latinumCost':0,'buildTime':55,'classLabel':'"craft"','aiName':'"CraftProcess"','freighter':0,'cargo_ship':0,'canAttack':1,'combat':1,'alert':1}
 for k,v in values.items():t=put(t,k,v)
 for i,w in enumerate(['bt3phas','bt3phas','bc2phot','gborgbor','gtwarpd','gregen'],1):t=put(t,'weapon'+str(i),'"'+w+'"');t=put(t,'weaponHardpoints'+str(i),'"'+('dzbeam1'if i in [1,4,5,6]else'dzbeam2'if i==2 else'dztorp')+'"')
 save(Path('odf/ships')/(name+'.odf'),t);records.append({'unit':name,'source':donor,'faction':names[code],'specialEnergy':3000,'regeneration':85,'weapons':['bt3phas','bt3phas','bc2phot','gborgbor','gtwarpd','gregen']})
# Nine entries fit one native production menu.
p=O/'odf/stations/xbdrozana.odf';t=p.read_text(encoding='latin1')
for i,row in enumerate(records):t=put(t,'buildItem'+str(i),'"'+row['unit']+'"')
save(p.relative_to(O),t)
for builder,station in [('xfgconst','xfdrozana'),('xbgconst','xbdrozana')]:
 t=idx[builder].read_text(encoding='latin1');slots=[int(k[9:])for k in cache[builder]if re.fullmatch('builditem[0-9]+',k)];slot=max(slots,default=-1)+1;assert slot<13;save(idx[builder].relative_to(root),put(t,'buildItem'+str(slot),'"'+station+'"'))
# Twice native cargo hold: 500 -> 1000. No unsupported ship transfer-rate key.
merchant=idx['xfgtrade'];save(merchant.relative_to(root),put(merchant.read_text(encoding='latin1'),'m_maxResource',1000))
# Uniform approved 2x cargo value, preserving station tax and handling rates.
for p in(root/'odf/stations').glob('*.odf'):
 t=p.read_text(encoding='latin1')
 if not re.search(r'(?mi)^cargoValue\d+\s*=',t):continue
 t=re.sub(r'(?mi)^(cargoValue\d+\s*=\s*)([\d.]+)',lambda m:m[1]+format(float(m[2])*2,'.10g'),t);save(p.relative_to(root),t)
for mode in ['tech1','earlytech','nosci','nosuper','nospweap','fulltech','freetech']:
 rel=Path('techtree')/(mode+'.tt');t=(root/rel).read_text(encoding='latin1');free=mode in ['fulltech','freetech'];t+='\n// Drozana commerce and Borg-only combat freighter foundry\n'
 for name,deps in [('xfdrozana',['xfgmerc']),('xbdrozana',['xbgmerc','byard2'])]+[(r['unit'],['xbdrozana'])for r in records]:
  assert not re.search(r'(?mi)^'+name+r'\.odf\s',t);t+=name+'.odf '+('0'if free else str(len(deps))+' '+' '.join(n+'.odf'for n in deps))+'\n'
 save(rel,t)
# Simple model-derived textured silhouettes, with high-contrast Borg/commerce badges.
def render(m):
 parts=visible(m);allv=np.concatenate([v for n,v in parts]);proj=lambda v:np.c_[v[:,0]-.65*v[:,2],-.72*v[:,1]+.28*(v[:,0]+v[:,2])];xy=proj(allv);center=(xy.max(0)+xy.min(0))/2;scale=108/max(np.ptp(xy,axis=0));im=Image.new('RGB',(128,128),(8,14,19));draw=ImageDraw.Draw(im);faces=[]
 for n,v in parts:
  d=n['data'];uv=np.asarray(d['texture_coordinates']);tex=Image.open(textures[d['texture'].lower()]).convert('RGB');a=np.asarray(tex);points=(proj(v)-center)*scale+64
  for group in d['vertex_lighting_groups']:
   for face in group['faces']:
    ids=[x[0]for x in face];coord=uv[[x[1]for x in face]].mean(0);col=a[int(np.clip(coord[1],0,.999)*(a.shape[0]-1)),int(np.clip(coord[0],0,.999)*(a.shape[1]-1))];faces.append((float(v[ids].mean(0)@[.5,1,.4]),points[ids].tolist(),tuple(int(x)for x in col)))
 for depth,points,col in sorted(faces,key=lambda x:x[0]):draw.polygon([tuple(x)for x in points],fill=col)
 return im
sprite=(root/'Sprites/gui_global.spr').read_text(encoding='latin1');gallery=Image.new('RGB',(512,384),(8,14,19));font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
for i,(name,m)in enumerate(models.items()):
 im=render(m);dr=ImageDraw.Draw(im);borg=name!='xfdrozana';dr.rectangle((2,2,125,125),outline=(60,245,105)if borg else(245,185,70),width=3);dr.rectangle((4,106,123,124),fill=(8,14,19));dr.text((7,108),name,font=font,fill=(210,245,220));gallery.paste(im,((i%4)*128,(i//4)*128));texture='gb'+name;p=O/'Textures/RGB'/(texture+'.tga');p.parent.mkdir(parents=True,exist_ok=True);im.resize((64,64),Image.Resampling.LANCZOS).save(p);sprite+='\n@reference=64\n@tmaterial=default\nb_'+name+' '+texture+' 0 0 64 64\n'
 for j in range(1,6):sprite+=name+'w'+str(j)+' '+texture+' 0 0 64 64\n'
save(Path('Sprites/gui_global.spr'),sprite);gallery.save(stage/'preview.png')
files={p.relative_to(O).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in O.rglob('*')if p.is_file()};sourceHashes={n:hashlib.sha256((root/n).read_bytes()).hexdigest()for n in files if(root/n).exists()}
report={'status':'STAGED_NOT_INSTALLED','ships':records,'files':files,'sourceHashes':sourceHashes,'ferengiCapacity':{'native':500,'new':1000},'cargoValueMultiplier':2,'loadUnloadSpeed':'Pending native per-ship implementation; station rates unchanged as explicitly requested.','stationDesignReference':'Drozana: former Federation/K7-family station operated by Ferengi; original inspired geometry, no extracted STO assets.','sources':['https://sto.fandom.com/wiki/Drozana_Station','https://www.playstartrekonline.com/en/news/article/11084713'],'energyFormula':'3 abilities x 1000 = 3000; sustain budget (50/s blue beam + 80/30s regeneration + 1000/60s transwarp) x1.2 rounded up to5 =85/s.','runtimeVerified':False};(stage/'manifest.json').write_text(json.dumps(report,indent=2));print(json.dumps({'stagedFiles':len(files),'combatFreighters':len(records),'stations':2,'speedPending':True}))
