from pathlib import Path
exec(Path('D:/aramada/scripts/build-bajor-redesign-v4.py').read_text().split('for name,d in before.items():')[0])
from PIL import ImageFont
from collections import Counter,defaultdict
P=json.loads((repo/'reports/icon-refresh-before.json').read_text());stage=Path('D:/Xaramada-Modwork/unit-identity-stage');stage.mkdir(parents=True,exist_ok=True);sprite=(root/'Sprites/gui_global.spr').read_text(encoding='latin1');sourcehash=hashlib.sha256((root/'Sprites/gui_global.spr').read_bytes()).hexdigest();sodidx={p.stem.lower():p for p in(root/'SOD').glob('*')if p.suffix.lower()=='.sod'}
units={n:d for n,d in P.items() if any(x in d['file'].replace('\\','/').lower()for x in ['/ships/','/stations/']) and d.get('unitname') and d.get('race','').lower() in ['federation','borg','klingon','romulan','cardassian','dominion','bajoran','ferengi','breen','species8472'] and d.get('classlabel') not in ['planet','scrap','planet_shield','upgrade']};records=[];fallback=[];renders={};files=[]
styles={'federation':('Starfleet',(100,180,255),['Venture','Horizon','Pioneer','Endeavour','Meridian','Frontier','Discovery','Sentinel']),'borg':('Collective',(70,235,135),['Nexus','Matrix','Directive','Convergence','Continuum','Unification','Adjunct','Vinculum']),'klingon':('Klingon',(240,90,65),["Kahless","Kor","Koloth","Kang","Martok","Gowron","Kurn","Mogh"]),'romulan':('Romulan',(100,220,165),['ChR','Raptor','Dderidex','Tal Shiar','Rihannsu','Dhael','Vreenak','Talon']),'cardassian':('Cardassian',(220,170,100),['Obsidian','Detapa','Legate','Tain','Central Command','Gul','Union','Terok']),'dominion':('Dominion',(190,135,245),['Founder','Vanguard','First','Vorta','Jem Hadar','Unity','Gamma','Victory']),'bajoran':('Bajoran',(230,180,100),['Dahkur','Rakantha','Kendra','Dakhur','Nerrak','Jalanda','Hathon','Prophets']),'ferengi':('Ferengi',(245,205,75),['Profit','Acquisition','Dividend','Margin','Contract','Liquidator','Vault','Monopoly']),'breen':('Breen',(135,220,235),['Thot','Icebound','Glacial','Confederacy','Cryonic','Winter','Coldfront','Permafrost']),'species8472':('Fluidic',(225,145,210),['Nucleic','Chimeric','Synaptic','Primal','Apex','Adaptive','Brood','Symbiotic']),'norace':('Independent',(175,185,200),['Wayfarer','Frontier','Nomad','Outrider']),'alien':('Alien',(175,185,200),['Ancient','Unknown','Exotic','Relic'])}
font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',38);small=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',24)

def role(n,d):
 cl=d.get('classlabel','').lower();name=d['unitname'].lower();station='/stations/'in d['file'].replace('\\','/').lower()
 if d.get('ishero')=='1':return 'HERO'
 if n.startswith('mrc'):return 'MIR'
 if cl in ['constructionrig','evolver']:return 'T3'if'temporal'in name or'universal'in name else'T2'if'advanced'in name else'BUILD'
 if cl=='colony':return 'COL'
 if cl=='repairship':return 'FIX'
 if 'trad'in name and not station:return 'TRADE'
 if cl=='cargo_ship':return 'LAT'
 if cl=='freighter' and ('latinum' in name or 'lat' in n and n.startswith('xfg')):return 'LAT'
 if cl=='freighter':return 'BIO'if d.get('race')=='species8472'else'DIL'
 if station:
  if n in ['bbase2'] or 'orbital'in n or ('metal'in name and 'research'not in name):return 'MET'
  if 'mining'in name or'refinery'in name or n.endswith('mining'):return 'DIL'
  if 'heavy weapons platform'in name or n in ['fhwp','khwp','rhwp','chwp','dturret3','bjhwp','bhwp']:return 'HWP'
  if 'torpedo'in name:return 'TORP'
  if 'turret'in name or'phaser platform'in name:return 'BEAM'
  if cl=='starbase' and d.get('is_starbase')=='1':return 'BASE'
  if cl=='shipyard':return 'YARD'if any(re.fullmatch('builditem[0-9]+',k)for k in d)else'FIX'
  if cl=='pod':return 'TECH'
  if cl=='research' or 'research'in name or'upgrade'in name:return 'R&D'
  if 'sensor'in name:return 'SCAN'
  if 'trading'in name:return 'TRADE'
  return 'STN'
 typ=d.get('shipclass','').lower()
 for word,label in [('battleship','BB'),('cruiser','CR'),('destroyer','DD'),('frigate','FF'),('scout','SC'),('fighter','FTR'),('transport','CARGO'),('artillery','ART')]:
  if word in typ or word in name:return label
 return 'SHIP'

def render(model):
 if model in renders:return renders[model].copy()
 path=sodidx.get(model)
 if not path:raise ValueError('Missing model '+model)
 try:m=load(path)
 except Exception:
  with contextlib.redirect_stdout(io.StringIO()):m=SodIO().read_file(str(path))
 nodes={z['id'].lower():z for z in m.nodes};worlds={}
 def world(z):
  key=z['id'].lower()
  if key in worlds:return worlds[key]
  parent=nodes.get(z['parent'].lower());worlds[key]=np.eye(4);worlds[key]=(world(parent)if parent and parent is not z else np.eye(4))@matrix(z);return worlds[key]
 def chain(z):
  out=[]
  while z and z['id'].lower()not in out:out.append(z['id'].lower());z=nodes.get(z['parent'].lower())
  return out
 meshes=[z for z in m.nodes if z['type']=='MESH'and len(z['data']['vertices'])and not any(x in ['borg','damage','shields','shield']for x in chain(z))]
 lods=[x for z in meshes for x in chain(z)if re.fullmatch('lod[0-9]+',x)];best=min(lods,key=lambda x:int(x[3:]))if lods else None
 if best:meshes=[z for z in meshes if best in chain(z)or not any(re.fullmatch('lod[0-9]+',x)for x in chain(z))]
 triangles=[];colors=[]
 for z in meshes:
  d=z['data'];v=np.array(d['vertices']);v=(world(z)@np.c_[v,np.ones(len(v))].T).T[:,:3];faces=[f for g in d['vertex_lighting_groups']for f in g['faces']]
  if not faces:continue
  fi=np.array([[a[0]for a in f]for f in faces]);ui=np.array([[a[1]for a in f]for f in faces]);tri=v[fi];uv=np.nan_to_num(np.array(d['texture_coordinates'])[ui].mean(1));tex=d['texture'].lower()
  if tex not in texturecache:texturecache[tex]=Image.open(texidx[tex]).convert('RGB')if tex in texidx else Image.new('RGB',(1,1),(135,145,155))
  texture=np.asarray(texturecache[tex]);h,w=texture.shape[:2];col=texture[(uv[:,1]*h).astype(int)%h,(uv[:,0]*w).astype(int)%w].astype(float);normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normal/=np.linalg.norm(normal,axis=1)[:,None]+1e-8;light=.48+.52*np.abs(normal@np.array([.3,.8,.5]));triangles.append(tri);colors.append(np.clip(col*light[:,None],0,255).astype('uint8'))
 if not triangles:raise ValueError('No visible model meshes')
 tri=np.concatenate(triangles);col=np.concatenate(colors);project=np.stack([tri[:,:,0]+tri[:,:,2]*.42,-tri[:,:,1]-tri[:,:,2]*.65],axis=2);lo=project.min((0,1));hi=project.max((0,1));project=(project-(lo+hi)/2)*(255/max(hi-lo))+np.array([152,139]);depth=(tri[:,:,2]-tri[:,:,1]*1.6).mean(1);im=Image.new('RGB',(320,320),(9,16,25));dr=ImageDraw.Draw(im)
 for j in np.argsort(depth):dr.polygon([tuple(p)for p in project[j]],fill=tuple(col[j]))
 renders[model]=im;return im.copy()

def cropkey(key):
 match=re.search(r'(?mi)^'+re.escape(key)+r'[ \t]+([^\r\n]+)',sprite)
 if not match:raise ValueError('No sprite '+key)
 a=match[1].split();ref=int(re.findall(r'(?mi)^@reference\s*=\s*(\d+)',sprite[:match.start()])[-1]);im=Image.open(texidx[a[0].lower()]).convert('RGB');x,y,w,h=[float(x)*im.width/ref for x in a[1:5]];return im.crop((int(x),int(y),int(x+w),int(y+h)))

def emblem(race):
 try:return cropkey(race+'_icon').resize((72,72))
 except Exception:pass
 im=Image.new('RGB',(72,72),(10,16,24));dr=ImageDraw.Draw(im);c=styles.get(race,styles['norace'])[1]
 if race=='bajoran':
  dr.ellipse((18,5,55,57),outline=c,width=5);dr.arc((28,5,65,57),85,275,fill=(10,16,24),width=8);dr.polygon([(37,29),(27,68),(51,48)],fill=c)
 elif race=='dominion':
  for y in [10,24,38]:dr.arc((7,y,65,y+26),180,360,fill=c,width=5)
  dr.ellipse((31,40,41,50),fill=c);dr.polygon([(36,48),(20,66),(52,66)],outline=c,width=4)
 elif race=='ferengi':
  dr.ellipse((21,10,52,62),outline=c,width=5);dr.arc((3,5,37,66),75,285,fill=c,width=5);dr.arc((36,5,69,66),255,105,fill=c,width=5)
 else:dr.polygon([(14,9),(58,9),(64,42),(36,66),(8,42)],outline=c,width=5);dr.line((17,30,55,30),fill=c,width=5)
 return im
used=Counter();atlas=None;atlasnames=[]
def status(message,done):
 f=repo/'status.json';s=json.loads(f.read_text(encoding='utf-8-sig'));s['current']=message;s['updated']=datetime.datetime.now().astimezone().isoformat();s['features']=[x for x in s.get('features',[])if x.get('title')!='Ship and station identity refresh']+[{'title':'Ship and station identity refresh','note':message,'steps':[{'label':str(i+1),'done':i<done}for i in range(10)]}];f.write_text(json.dumps(s,indent=2),encoding='utf-8')
 with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n['+s['updated']+'] '+message+'\n')
status('Staging model-based ship/station icons, role badges, hero faction emblems and faction-specific names/tooltips. Live game unchanged.',0)
for i,(n,d)in enumerate(sorted(units.items())):
 race=d.get('race','norace').lower();prefix,color,words=styles.get(race,styles['norace']);r=role(n,d);old=d['unitname'];old=re.sub(r'\s+',' ',old).strip();old=old.replace('USS ','')if race=='bajoran'else old
 name=old if old.lower().startswith((prefix.lower(),race.lower()))or d.get('ishero')=='1'else prefix+' '+old
 if n.startswith('mrc')and'Mirror'not in name:name='Mirror '+name
 base=name;used[base.lower()]+=1
 if used[base.lower()]>1:
  j=used[base.lower()]-2;name=base+' - '+words[j%len(words)]+(' '+str(j//len(words)+1)if j>=len(words)else'')
 model=d.get('basename',n).lower();mode='model'
 try:im=render(model)
 except Exception as e:
  mode='existing-artwork';fallback.append({'unit':n,'model':model,'reason':str(e)})
  try:im=cropkey('b_'+n).resize((320,320))
  except Exception:
   try:im=cropkey('b_'+model).resize((320,320))
   except Exception:im=Image.new('RGB',(320,320),(9,16,25));ImageDraw.Draw(im).text((40,140),prefix,font=font,fill=color);mode='missing-model-placeholder'
 dr=ImageDraw.Draw(im);dr.rectangle((1,1,318,318),outline=color,width=5);dr.rounded_rectangle((231,8,310,87),9,fill=(7,12,20),outline=color,width=4)
 if r in ['HERO','MIR']:im.paste(emblem(race),(235,12))
 elif r in ['DIL','BIO']:dr.polygon([(270,19),(292,35),(285,67),(268,78),(249,57),(251,32)],fill=color,outline=(240,250,255),width=3)
 elif r=='MET':
  for x,y in [(244,47),(271,47),(258,23)]:dr.polygon([(x,y+10),(x+10,y),(x+27,y),(x+32,y+10),(x+28,y+23),(x+2,y+23)],fill=color,outline=(60,80,90),width=2)
 elif r=='COL':dr.ellipse((244,19,300,75),outline=color,width=4);dr.line((248,47,297,47),fill=color,width=3);dr.polygon([(254,67),(272,48),(291,67)],fill=(235,245,250))
 elif r=='BASE':
  dr.ellipse((242,32,301,62),outline=color,width=6);dr.line((271,18,271,77),fill=color,width=6);dr.line((250,18,291,77),fill=color,width=4);dr.line((291,18,250,77),fill=color,width=4)
 else:
  box=dr.textbbox((0,0),r,font=small);dr.text((271-(box[2]-box[0])/2,32),r,font=small,fill=color)
 dr.rectangle((0,267,319,319),fill=(7,12,20));box=dr.textbbox((0,0),r,font=font);dr.text(((320-box[2])/2,266),r,font=font,fill=color)
 thumb=im.resize((64,64),Image.Resampling.LANCZOS);page=i//64;cell=i%64;texture='xuiatlas'+str(page).zfill(2)
 if cell==0:
  if atlas is not None:atlas.save(stage/'Textures/RGB'/(atlasnames[-1]+'.tga'))
  atlas=Image.new('RGB',(512,512),(7,12,20));atlasnames.append(texture);(stage/'Textures/RGB').mkdir(parents=True,exist_ok=True)
 x=(cell%8)*64;y=(cell//8)*64;atlas.paste(thumb,(x,y));sprite=re.sub(r'(?mi)^b_'+re.escape(n)+r'[ \t]+[^\r\n]*','',sprite);sprite+='\n@reference=512\n@tmaterial=default\nb_'+n+' '+texture+' '+str(x)+' '+str(y)+' 64 64\n'
 normal=[];special=[]
 for k,v in sorted(d.items()):
  if not re.fullmatch('weapon[0-9]+',k):continue
  w=P.get(v.lower(),{});title=w.get('wpnname',v)
  if w.get('special')=='1':special.append(title)
  else:normal.append(title)
 purposes={'DIL':'Extracts dilithium and supports the faction economy.','MET':'Processes orbital metal resources.','BIO':'Collects biomatter to sustain living fleets.','LAT':'Harvests latinum for purchases and trade.','TRADE':'Carries trade cargo between eligible trading stations.','COL':'Establishes colonies on suitable unclaimed planets.','BUILD':'Builds the basic structures in its construction menu.','T2':'Builds advanced structures in its construction menu.','T3':'Builds strategic structures in its construction menu.','FIX':'Repairs friendly vessels using its native repair systems.','BASE':'Anchors the fleet and produces the units shown in its build menu.','YARD':'Constructs the vessels available in its production menu.','TECH':'Unlocks its assigned research upgrade.','R&D':'Develops the technologies listed in its research menu.','HWP':'Heavy defensive station guarding nearby approaches.','TORP':'Defensive platform armed with torpedo weapons.','BEAM':'Defensive platform armed with beam weapons.','SCAN':'Provides local sensor coverage.','HERO':'Hero vessel with its own command abilities.','MIR':'Controllable Mirror Universe counterpart, built through normal production.'}
 desc=purposes.get(r,'Serves as a '+d.get('shipclass','fleet combatant').replace('"','')+'.'if'/ships/'in d['file'].replace('\\','/').lower()else'Supports the operations available through its station controls.')
 if normal:desc+=' Armament: '+str(len(normal))+' standard weapon banks.'
 if special:desc+=' Abilities: '+', '.join(dict.fromkeys(special))+'.'
 if d.get('maxspecialenergy')and special:desc+=' Special energy: '+d['maxspecialenergy']+'.'
 desc=prefix+' service. '+desc
 t=Path(d['file']).read_text(encoding='latin1')
 for k,v in [('unitName',name),('tooltip',name),('verboseTooltip',desc)]:t=put(t,k,'"'+v.replace('"',"'")+'"')
 rel=Path(d['file']).relative_to(root).as_posix();out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1',errors='replace'));files.append(rel)
 records.append({'unit':n,'race':race,'oldName':d['unitname'],'name':name,'description':desc,'role':r,'model':model,'artwork':mode,'texture':texture,'cell':[x,y,64,64],'odf':rel})
 (stage/'preview').mkdir(exist_ok=True)
 if i%9==0 or r=='HERO':thumb.save(stage/'preview'/(n+'.png'))
 if(i+1)%50==0:status('Staging icons and faction tooltips: '+str(i+1)+' / '+str(len(units))+' units. Live game unchanged.',int((i+1)*9/len(units)));print(str(i+1)+' / '+str(len(units)),flush=True)
atlas.save(stage/'Textures/RGB'/(atlasnames[-1]+'.tga'));files+=['Textures/RGB/'+n+'.tga'for n in atlasnames];out=stage/'Sprites/gui_global.spr';out.parent.mkdir(exist_ok=True);out.write_bytes(sprite.replace('\r','').replace('\n','\r\n').encode('latin1'));files+=['Sprites/gui_global.spr']
manifest={'stage':str(stage),'applied':False,'sourceSpriteSha256':sourcehash,'units':records,'fallbacks':fallback,'files':files,'sourceODFHashes':{v['odf']:hashlib.sha256((root/v['odf']).read_bytes()).hexdigest()for v in records},'runtimeVerified':False};(stage/'manifest.json').write_text(json.dumps(manifest,indent=2));(repo/'reports/unit-identity-staged.json').write_text(json.dumps(manifest,indent=2))
# Contact sheet includes each race and role plus named heroes.
selected=[]
for race in styles:
 group=[r for r in records if r['race']==race];selected+=group[:2]+[r for r in group if r['role']in ['DIL','MET','COL','BASE','HERO']][:6]
selected=selected[:96];sheet=Image.new('RGB',(960,((len(selected)+7)//8)*104),(9,16,25));dr=ImageDraw.Draw(sheet);ff=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',11)
for j,r in enumerate(selected):
 im=Image.open(stage/'Textures/RGB'/(r['texture']+'.tga'));x,y,w,h=r['cell'];thumb=im.crop((x,y,x+w,y+h)).resize((80,80));px=(j%8)*120;py=(j//8)*104;sheet.paste(thumb,(px+20,py));dr.text((px+2,py+81),r['unit'][:18],font=ff,fill=(220,230,240))
sheet.save(stage/'unit-icons-preview.png');status('Icon and tooltip pack staged: '+str(len(records))+' units, '+str(len(atlasnames))+' atlases. Game files unchanged; awaiting user review/closed game.',10);print('STAGED '+str(len(records))+' units; '+str(len(fallback))+' render fallbacks. '+str(stage),flush=True)
