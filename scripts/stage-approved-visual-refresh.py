"""Stage approved faction artwork; no writes to the running installation."""
from pathlib import Path
exec(Path('D:/aramada/scripts/build-bajor-redesign-v4.py').read_text().split('for name,d in before.items():')[0])
import importlib.util,shutil
from PIL import ImageFont
sp=importlib.util.spec_from_file_location('geom',repo/'scripts/approved-station-geometry.py');G=importlib.util.module_from_spec(sp);sp.loader.exec_module(G)
P=json.loads((repo/'reports/visual-refresh-before.json').read_text());stage=Path('D:/Xaramada-Modwork/approved-visual-refresh-stage');overlay=stage/'overlay';overlay.mkdir(parents=True,exist_ok=True)
pending={};sourcehashes={};records=[];gameplay=[];targets={};sprite=(root/'Sprites/gui_global.spr').read_text(encoding='latin1')
atlas=Image.open(repo/'artwork/iconian-battle-array/v1/faction-materials-source.png').convert('RGB').resize((1024,1024),Image.Resampling.LANCZOS)
tiles={'federation':0,'borg':1,'klingon':2,'romulan':3,'cardassian':4,'dominion':5,'bajoran':6,'breen':7,'ferengi':8,'species8472':9}
for c in range(16):
 out=overlay/'Textures/RGB'/('vr26t'+str(c).zfill(2)+'.tga');out.parent.mkdir(parents=True,exist_ok=True);atlas.crop(((c%4)*256,(c//4)*256,(c%4+1)*256,(c//4+1)*256)).save(out);texidx[out.stem.lower()]=out
def emit(message):
 print(message,flush=True);s=json.loads((repo/'status.json').read_text(encoding='utf-8-sig'));s['current']=message+' Live artwork unchanged; model fix remains applied.';(repo/'status.json').write_text(json.dumps(s,indent=2),encoding='utf-8')
 with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n[Visual staging] '+message+'\n')
def q(v):return '"'+v+'"'
def source_text(n):
 rel=Path(P[n]['file']).relative_to(root).as_posix();return pending.get(rel,Path(P[n]['file']).read_text(encoding='latin1'))
def settext(rel,t):
 if(root/rel).exists():sourcehashes[rel]=hashlib.sha256((root/rel).read_bytes()).hexdigest()
 pending[rel]=t
def menu(t,items):
 assert len(items)<=14
 t=re.sub(r'(?mi)^[ \t]*buildItem\d+\s*=[^\r\n]*','',t)
 return t+'\n'+''.join('buildItem'+str(i)+' = '+q(n)+'\n'for i,n in enumerate(items))
def add(n,kind,race=None,tier=1,donor=None):targets[n]={'kind':kind,'race':race or P[n]['race'],'tier':tier,'donor':donor or n}

# Active production yards; preserve special-purpose facilities' shapes and animations.
yards=json.loads((repo/'reports/yard-consolidation.json').read_text())['rosters']
for n in yards:
 if n=='fbyard':continue
 race='ferengi'if n.startswith(('xfg','xbg'))else P[n]['race'];tier=3 if n.endswith('3')or n.startswith('mry')or n in ['s31yard','xflegacyyard','xhs_yard3']else 2 if n.endswith('2')else 1
 kind='reskin'if n in ['brecycle','fremmeler','cardassian_super_station','ksuperbl','rsuperbl','zsuperbl','xbassimst']else'yard'
 add(n,kind,race,tier)
for n in ['forbital','bbase2','borbital','korbital','rorbital','corbital','dorbital','bjorbital','brorbital','xfgmetal2','xfgmetal3','xbgmetal2','xbgmetal3']:
 add(n,'orbital','ferengi'if n.startswith(('xfg','xbg'))else P[n]['race'],2 if n.endswith('metal3')else 1)
for n in ['fhwp','bhwp','khwp','rhwp','chwp','bjhwp','dturret3']:add(n,'reskin')
for n,d in P.items():
 if d.get('classlabel')=='constructionrig'or'constructor'in d.get('unitname','').lower():
  if d.get('race')not in tiles:continue
  race='ferengi'if n.startswith(('xfg','xbg','xu3fer'))else d['race'];tier=3 if any(s in d.get('unitname','').lower()for s in ['temporal','universal'])else 2 if'advanced'in d.get('unitname','').lower()else 1
  add(n,'constructor',race,tier)
for n in ['xfgresearch','xbgresearch']:add(n,'research','ferengi')
for n,d in P.items():
 if d.get('classlabel')=='pod'and(n.startswith(('xfg','xbg'))or n=='mrpfer'):add(n,'reskin','ferengi')

# Two balanced Ferengi constructors: industry versus starbases / array.
for prefix,race in [('xfg','ferengi'),('xbg','borg')]:
 first=prefix+'const';second=prefix+'const2';ref=prefix+'dref';base=P[first];t=source_text(first)
 economy=[prefix+'merc',prefix+'serv',prefix+'research',prefix+'metal2',prefix+'metal3',ref]
 t=menu(t,economy);t=put(t,'unitName',q('Ferengi Basic Constructor'));t=put(t,'tooltip',q('Ferengi Basic Constructor'));t=put(t,'verboseTooltip',q('Ferengi Basic Constructor\\nMining, research and contract yards\\nEvery venture begins with a sound investment.'))
 settext(Path(base['file']).relative_to(root).as_posix(),t);add(first,'constructor','ferengi',1)
 u=menu(source_text(first),['bbase','fbase','kbase','rbase','cbase','dbase','brbase','bjbase','fgiaarray'if prefix=='xfg'else'bgiaarray'])
 for k,v in {'unitName':q('Ferengi Advanced Constructor'),'tooltip':q('Ferengi Advanced Constructor'),'buildTime':55,'latinumCost':700 if prefix=='xfg'else 0,'dilithiumCost':420 if prefix=='xbg'else 0,'metalCost':280 if prefix=='xbg'else 0,'verboseTooltip':q('Ferengi Advanced Constructor\\nStarbases and Iconian Battle Array\\nA profitable foothold in every quadrant.')}.items():u=put(u,k,v)
 P[second]={**base,'file':str(root/'odf/ships'/(second+'.odf')),'unitname':'Ferengi Advanced Constructor'};settext('odf/ships/'+second+'.odf',u);add(second,'constructor','ferengi',2,first)
 serv=prefix+'serv';items=[v for k,v in sorted(P[serv].items(),key=lambda kv:int(kv[0][9:])if re.fullmatch('builditem[0-9]+',kv[0])else-1)if re.fullmatch('builditem[0-9]+',k)]
 if first not in items:items.append(first)
 items.append(second);settext(Path(P[serv]['file']).relative_to(root).as_posix(),menu(source_text(serv),items))
 # New refinery inherits a working native MiningStation and uses the existing tiered miners.
 f=source_text('fmining');P[ref]={**P['fmining'],'file':str(root/'odf/stations'/(ref+'.odf')),'race':race,'unitname':'Ferengi Dilithium Exchange'}
 vals={'unitName':q('Ferengi Dilithium Exchange'),'tooltip':q('Ferengi Dilithium Exchange'),'race':q(race),'freighterName':q(prefix+'dil2'),'resourcesCanHandle':q('dilithium'),'latinumCost':400 if prefix=='xfg'else 0,'dilithiumCost':240 if prefix=='xbg'else 0,'metalCost':160 if prefix=='xbg'else 0,'biomatterCost':0,'crewCost':100,'maximumCrew':200,'buildTime':60,'verboseTooltip':q('Ferengi Dilithium Exchange\\nDilithium unloading and processing\\nRefined crystals turn opportunity into profit.')}
 for k,v in vals.items():f=put(f,k,v)
 settext('odf/stations/'+ref+'.odf',f);add(ref,'dilref','ferengi',1,'fmining')
 gameplay.append({'type':'Ferengi constructor split','primary':first,'primaryMenu':economy,'secondary':second,'secondaryCost':{'latinum':700}if race=='ferengi'else{'dilithium':420,'metal':280},'newRefinery':ref})
# Borg-priced array avoids selling Latinum-only production to Borg players.
t=source_text('fgiaarray');P['bgiaarray']={**P['fgiaarray'],'file':str(root/'odf/stations/bgiaarray.odf'),'race':'borg'}
t=put(t,'race',q('borg'));t=put(t,'freighterName',q('xbgdil2'));t=menu(t,['xbgconst','xbgconst2','xbgdil2','xbgdil3']);settext('odf/stations/bgiaarray.odf',t)
# Native mining beam is always slot one. Append the requested combat banks only.
for n in ['xfgmetal2','xfgmetal3','xbgmetal2','xbgmetal3']:
 t=source_text(n);assert P[n]['weapon1'].lower()=='gorbitalbeam'
 for i,w in [(2,'xfgcruisb'),(3,'xfgcruisb'),(4,'xfgcruist')]:t=put(t,'weapon'+str(i),q(w));t=put(t,'weaponHardpoints'+str(i),q('vrgun'+str(i)))
 settext(Path(P[n]['file']).relative_to(root).as_posix(),t);gameplay.append({'type':'Ferengi orbital armament','unit':n,'miningBeamUnchanged':True,'beams':2,'photons':1})

def load_model(path):
 try:return load(path)
 except Exception:
  with contextlib.redirect_stdout(io.StringIO()):return SodIO().read_file(str(path))
def visible_points(model):
 # Some valid legacy models reuse the ID 'borg' for a parent and its mesh.
 # Resolve parents in file order rather than making a cyclic last-ID dictionary.
 worlds=[];chains=[];last={};points=[]
 for n in model.nodes:
  parent=last.get(n['parent'].lower());world=(worlds[parent]if parent is not None else np.eye(4))@matrix(n);chain=(chains[parent]if parent is not None else[])+[n['id'].lower()];worlds.append(world);chains.append(chain);last[n['id'].lower()]=len(worlds)-1
  if n['type']=='MESH'and not any(s in ['borg','damage','shield','shields']for s in chain):
   vs=np.asarray(n['data']['vertices']);points.extend((world@np.c_[vs,np.ones(len(vs))].T).T[:,:3])
 assert points,'No primary hull geometry';return np.asarray(points)
def construct_model(n,c):
 d=P[c['donor']];old=load_model(root/'SOD'/(d.get('basename',c['donor'])+'.sod'));m=copy.deepcopy(old);race=c['race'];tile=tiles[race];kind=c['kind']
 if kind=='reskin':
  for node in m.nodes:
   if node['type']!='MESH':continue
   p=node['data'];p['texture']='vr26t'+str(tile).zfill(2);p['borgification']={'texture':p['texture']};p['bump_map']=1;p['texture_material']='default';p['texture_coordinates']=np.clip(np.array(p['texture_coordinates']),0,1).tolist()
 else:
  g=G.orbital(race,c['tier'])if kind=='orbital'else G.yard(race,c['tier'],'serv'in n)if kind=='yard'else G.constructor(race,c['tier'])if kind=='constructor'else G.ferengi_station('research'if kind=='research'else'dilref')
  for node in m.nodes:
   if node['type']=='MESH':node['type']='NULL_OR_HARDPOINT';node['data']=None
  parent=next(z for z in m.nodes if not z['parent']);inv=np.linalg.inv(matrix(parent));op=visible_points(old);oldspan=np.ptp(op,axis=0).max();oldcenter=(op.max(0)+op.min(0))/2;pts=np.concatenate([p['v']for p in g.parts]);center=(pts.max(0)+pts.min(0))/2;span=np.ptp(pts,axis=0).max()
  def loc(v):return(inv@np.r_[(np.array(v)-center)/span*oldspan+oldcenter,1])[:3].tolist()
  light=13 if race in ['borg','romulan']else 14 if race in ['dominion','species8472']else 15 if race in ['klingon','cardassian','bajoran','ferengi']else 12
  for mat in ['hull','dark','pipes','glow']:
   donor_material=old.materials[0]if old.materials else load(root/'SOD/xbtarray.sod').materials[0]
   material=copy.deepcopy(donor_material);material['name']='vr_'+mat;material['ambient_color']=[.6]*3;material['diffuse_color']=[1.]*3;material['self_illumination_enabled']=mat=='glow';m.materials.append(material)
   cell={'hull':tile,'dark':10,'pipes':11,'glow':light}[mat];triangles=[]
   for p in g.parts:
    if p['mat']!=mat:continue
    for face in p['f']:
     tri=p['v'][list(face)];axis=np.abs(np.cross(tri[1]-tri[0],tri[2]-tri[0])).argmax();axes=[k for k in range(3)if k!=axis];lo=p['v'][:,axes].min(0);delta=np.ptp(p['v'][:,axes],axis=0);delta[delta<1e-6]=1;uv=(tri[:,axes]-lo)/delta*.86+.07;triangles.append((tri,uv))
   for start in range(0,len(triangles),150):
    vv=[];uvs=[];ff=[]
    for tri,uv in triangles[start:start+150]:
     j=len(vv);vv.extend(loc(v)for v in tri);uvs.extend(uv.tolist());ff.append([[j+k,j+k]for k in range(3)])
    tex='vr26t'+str(cell).zfill(2);data={'texture_material':'default','bump_map':1,'texture':tex,'borgification':{'texture':tex},'vertices':vv,'texture_coordinates':uvs,'vertex_lighting_groups':[{'lighting_material':'vr_'+mat,'faces':ff}],'cull_type':0}
    m.nodes.append({'id':'vr_'+mat+'_'+str(start//150),'parent':parent['id'],'type':'MESH','local_transform':[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],[0.,0.,0.]],'data':data})
  if n.startswith(('xfgmetal','xbgmetal')):
   for i,pos in [(2,(-.6,.2,0)),(3,(.6,.2,0)),(4,(0,.2,.6))]:m.nodes.append({'id':'vrgun'+str(i),'parent':parent['id'],'type':'NULL_OR_HARDPOINT','local_transform':[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],loc(pos)],'data':None})
 alias='vr26_'+n;out=overlay/'SOD'/(alias+'.sod');out.parent.mkdir(parents=True,exist_ok=True);w=IO();w.curr_sod_version=m.version
 with contextlib.redirect_stdout(io.StringIO()):w.write_file(m,str(out))
 check=load_model(out);assert len(check.animation_transforms)==len(old.animation_transforms);assert {x['id']for x in old.nodes}.issubset({x['id']for x in check.nodes})
 return check,alias

# Reuse established badge glyphs; new icons are rendered directly from actual staged models.
ns={};exec((repo/'scripts/apply-function-badges-scale.py').read_text().split("for row in pack['units']:")[0],ns);symbol=ns['symbol'];font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',34)
for index,(n,c)in enumerate(sorted(targets.items())):
 emit('Staging faction artwork '+str(index+1)+'/'+str(len(targets))+': '+n)
 m,alias=construct_model(n,c);odf=Path(P[n]['file']);rel=odf.relative_to(root).as_posix();t=pending.get(rel,odf.read_text(encoding='latin1')if odf.exists()else'');t=put(t,'baseName',q(alias));settext(rel,t)
 im=preview(m,256);im.save(stage/(n+'-preview.png'));thumb=im.convert('RGBA');kind=c['kind']
 role='HWP'if n in ['fhwp','bhwp','khwp','rhwp','chwp','bjhwp','dturret3']else'MET'if kind=='orbital'else'YARD'if kind=='yard'else'BUILD'if kind=='constructor'else'R&D'if kind=='research'or P[n].get('classlabel')=='pod'else'DIL'if kind=='dilref'else'YARD'
 labels=['defence']if role=='HWP'else['metal']if role=='MET'else['construct']if role=='BUILD'else['science']if role=='R&D'else['dil']if role=='DIL'else['yard']+(['repair']if P[n].get('repairfacility')!='0'and P[n].get('classlabel')=='shipyard'else[])
 if n.startswith(('xfgmetal','xbgmetal')):labels.append('defence')
 color=(235,85,70)if role=='HWP'else(80,175,250)if role=='YARD'else(80,220,130)if role in ['MET','DIL']else(245,210,60)if role=='R&D'else(145,200,245)
 # Gentle category tint, retaining the source model underneath.
 tint=Image.new('RGBA',thumb.size,(0,0,0,0));td=ImageDraw.Draw(tint)
 for y in range(256):td.line((0,y,255,y),fill=color+(int(max(0,y-110)/145*35),))
 thumb=Image.alpha_composite(thumb,tint);dr=ImageDraw.Draw(thumb);dr.rectangle((2,2,253,253),outline=color+(255,),width=5)
 for j,label in enumerate(labels[:2]):x=164 if j==0 else 4;dr.rounded_rectangle((x,4,x+88,92),radius=10,fill=(5,11,20,245),outline=ns['colors'][label]+(255,),width=4);thumb.alpha_composite(symbol(label),(x,4));dr=ImageDraw.Draw(thumb)
 if role=='HWP':dr.rectangle((4,191,251,250),fill=(45,8,10,245));dr.text((71,195),'HWP',font=font,fill=(255,225,180,255));dr.line((20,232,235,232),fill=(250,90,60,255),width=3)
 tex='gb'+alias;thumb.resize((64,64),Image.Resampling.LANCZOS).convert('RGB').save(overlay/'Textures/RGB'/(tex+'.tga'));wf='wf'+alias;im.resize((64,64),Image.Resampling.LANCZOS).convert('RGB').save(overlay/'Textures/RGB'/(wf+'.tga'))
 keys=['b_'+n,'b_'+alias]+[p+'w'+str(i)for p in [n,alias]for i in range(1,6)]
 for key in keys:sprite=re.sub(r'(?mi)^'+re.escape(key)+r'[ \t]+[^\r\n]*','',sprite)
 sprite+='\n@reference=64\n@tmaterial=default\nb_'+n+' '+tex+' 0 0 64 64\nb_'+alias+' '+tex+' 0 0 64 64\n'
 for p in [n,alias]:
  for i in range(1,6):sprite+=p+'w'+str(i)+' '+wf+' 0 0 64 64\n'
 records.append({'unit':n,'kind':kind,'theme':c['race'],'tier':c['tier'],'model':alias,'sourceModel':P[c['donor']].get('basename',c['donor']),'sourceUnit':c['donor'],'badges':labels,'animationChannels':len(m.animation_transforms)})
# The Borg-priced Ferengi array shares the tested Ferengi model and icon.
for oldkey,newkey in [('b_fgiaarray','b_bgiaarray')]+[('fgiaarrayw'+str(i),'bgiaarrayw'+str(i))for i in range(1,6)]:
 match=re.search(r'(?mi)^'+oldkey+r'[ \t]+[^\r\n]*',sprite);assert match;ref=re.findall(r'(?mi)^@reference\s*=\s*(\d+)',sprite[:match.start()])[-1];sprite+='\n@reference='+ref+'\n@tmaterial=default\n'+re.sub(r'^\S+',newkey,match[0])+'\n'
settext('Sprites/gui_global.spr',sprite)
for tree in ['tech1','earlytech','fulltech','nosci','nosuper','nospweap']:
 rel='techtree/'+tree+'.tt';t=(root/rel).read_text(encoding='latin1')
 t=re.sub(r'(?mi)^fgiaarray\.odf\s+[^\r\n]*','fgiaarray.odf '+('0'if tree=='fulltech'else'1 xfgconst2.odf')+' // Ferengi advanced construction',t)
 for n,b in [('xfgconst2','xfgserv'),('xbgconst2','xbgserv'),('xfgdref','xfgconst'),('xbgdref','xbgconst'),('bgiaarray','xbgconst2')]:t+='\n'+n+'.odf '+('0'if tree=='fulltech'else'1 '+b+'.odf')+' // Ferengi industry and expansion\n'
 settext(rel,t)
for aip in(root/'AI/AIPs').glob('*.aip'):
 t=aip.read_text(encoding='latin1');changed=False
 for prefix in ['xfg','xbg']:
  if not re.search(r'"'+prefix+'serv"',t):continue
  pattern=r'(?m)^([^\r\n]*"'+prefix+r'serv"[^\r\n]*)$'
  extra='\n    "'+prefix+'const2", 1, 0, -1, 0,\n    "'+prefix+'dref", 1, 0, -1, 0, // Ferengi dilithium exchange'
  t=re.sub(pattern,lambda m:m[1]+extra,t,count=1);changed=True
 if changed:settext(aip.relative_to(root).as_posix(),t)
for rel,t in pending.items():dest=overlay/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'))
for category,predicate in [('constructors',lambda r:r['kind']=='constructor'),('orbitals',lambda r:r['kind']=='orbital'),('yards',lambda r:r['kind']=='yard'),('ferengi',lambda r:r['theme']=='ferengi'),('hwp',lambda r:r['unit']in ['fhwp','bhwp','khwp','rhwp','chwp','bjhwp','dturret3'])]:
 rows=[r for r in records if predicate(r)];height=70+((len(rows)+3)//4)*295;sheet=Image.new('RGB',(1280,height),(9,16,24));dr=ImageDraw.Draw(sheet);f=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',20);dr.text((20,18),category.upper()+' — ACTUAL STAGED MODELS',font=f,fill=(225,205,155))
 for i,r in enumerate(rows):x=(i%4)*320;y=70+(i//4)*295;sheet.paste(Image.open(stage/(r['unit']+'-preview.png')),(x+32,y));dr.text((x+15,y+259),r['unit']+' | '+r['theme'],font=f,fill=(205,215,225))
 sheet.save(stage/(category+'-preview.png'))
files={p.relative_to(overlay).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in overlay.rglob('*')if p.is_file()};report={'status':'STAGED - NOT APPLIED','stage':str(stage),'files':files,'sourceHashes':sourcehashes,'units':records,'gameplayChanges':gameplay,'newUnits':['xfgconst2','xbgconst2','xfgdref','xbgdref','bgiaarray'],'startingFleetsChanged':False,'runtimeVerified':False}
(stage/'manifest.json').write_text(json.dumps(report,indent=2));(repo/'reports/approved-visual-refresh-staged.json').write_text(json.dumps(report,indent=2));emit('Remaining artwork staged: '+str(len(records))+' models. Static validation pending.')
