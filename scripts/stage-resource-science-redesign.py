"""Stage the upgraded resource / research family and matching Borg utility structures."""
from pathlib import Path
exec(Path('D:/aramada/scripts/build-bajor-redesign-v4.py').read_text().split('for name,d in before.items():')[0])
import ast,importlib.util,shutil
from PIL import ImageFont
source=(repo/'scripts/stage-approved-visual-refresh.py').read_text();tree=ast.parse(source)
for node in tree.body:
 if isinstance(node,ast.FunctionDef)and node.name in ['load_model','visible_points','construct_model']:exec(compile(ast.Module(body=[node],type_ignores=[]),str(repo/'scripts/stage-approved-visual-refresh.py'),'exec'))
sp=importlib.util.spec_from_file_location('newfamilies',repo/'scripts/resource-science-geometry.py');D=importlib.util.module_from_spec(sp);sp.loader.exec_module(D)
P=json.loads((repo/'reports/resource-science-all-before.json').read_text());selected=json.loads((repo/'reports/dil-research-redesign-before.json').read_text());stage=Path('D:/Xaramada-Modwork/resource-science-redesign-stage');overlay=stage/'overlay';overlay.mkdir(parents=True,exist_ok=True);pending={};sourcehashes={};records=[];sprite=(root/'Sprites/gui_global.spr').read_text(encoding='latin1')
tiles={'federation':0,'borg':1,'klingon':2,'romulan':3,'cardassian':4,'dominion':5,'bajoran':6,'breen':7,'ferengi':8,'species8472':9}
atlas=Image.open(repo/'artwork/iconian-battle-array/v1/faction-materials-source.png').convert('RGB').resize((1024,1024),Image.Resampling.LANCZOS)
for i in range(16):
 dest=overlay/'Textures/RGB'/('vr26t'+str(i).zfill(2)+'.tga');dest.parent.mkdir(parents=True,exist_ok=True);atlas.crop(((i%4)*256,(i//4)*256,(i%4+1)*256,(i//4+1)*256)).save(dest);texidx[dest.stem]=dest
def settext(rel,t):
 if(root/rel).exists():sourcehashes[rel]=hashlib.sha256((root/rel).read_bytes()).hexdigest()
 pending[rel]=t
def emit(s):
 print(s,flush=True);status=json.loads((repo/'status.json').read_text(encoding='utf-8-sig'));status['current']=s+' Preparing separately; live game unchanged.';(repo/'status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
 with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n[Resource / science staging] '+s+'\n')
def podnames(d):return list(dict.fromkeys(re.findall(r'[A-Za-z0-9_]+',d.get('podhardpoints',''))))
class Factory:
 def yard(self,race,tier,service):
  global geometry
  k=active['kind'];ports=len(active['pods'])
  geometry=D.freighter(race,tier)if k=='freighter'else D.refinery(race)if k=='refinery'else D.assimilation('producer'if active['unit']=='xbassimst'else'tech'if active['unit']=='btechass'else'turret',ports)if k=='assimilation'else D.recycler()if k=='recycler'else D.repair_drone()if k=='repair'else D.research(race,ports,tier)
  return geometry
G=Factory();targets={}
for n,d in selected.items():
 if d.get('race')not in tiles:continue
 race='ferengi'if n.startswith(('xfg','xbg'))else d['race'];kind='freighter'if d['classlabel']=='freighter'else'refinery'if d['classlabel']=='mining'else'research';tier=3 if n.endswith('3')or'upgrade'in n or'omega'in n else 2 if n.endswith('2')or'advanced'in n else 1
 targets[n]={'unit':n,'kind':kind,'race':race,'tier':tier,'pods':podnames(d)}
for n,k in [('bassturr','assimilation'),('btechass','assimilation'),('xbassimst','assimilation'),('brecycle','recycler'),('xbrepair','repair')]:targets[n]={'unit':n,'kind':k,'race':'borg','tier':2,'pods':podnames(P[n])}
ns={};exec((repo/'scripts/apply-function-badges-scale.py').read_text().split("for row in pack['units']:")[0],ns);symbol=ns['symbol'];font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',24)
for number,(n,active)in enumerate(sorted(targets.items()),1):
 emit('Preparing upgraded resource / science model '+str(number)+'/'+str(len(targets))+': '+n)
 d=P[n];c={'kind':'yard','race':active['race'],'tier':active['tier'],'donor':n};m,oldalias=construct_model(n,c)
 # Source graph and native node names are preserved; place each research socket on its visible mount.
 podmoves=[];parent=next(z for z in m.nodes if not z['parent']);rootinv=np.linalg.inv(matrix(parent));oldmodel=load_model(root/'SOD'/(d.get('basename',n)+'.sod'));op=visible_points(oldmodel);oldspan=np.ptp(op,axis=0).max();oldcenter=(op.max(0)+op.min(0))/2;points=np.concatenate([p['v']for p in geometry.parts]);center=(points.max(0)+points.min(0))/2;span=np.ptp(points,axis=0).max()
 def local(v):return(rootinv@np.r_[(np.array(v)-center)/span*oldspan+oldcenter,1])[:3].tolist()
 node_by_name={z['id'].lower():z for z in m.nodes}
 for hp,pos in zip(active['pods'],getattr(geometry,'mounts',[])):
  anchor=node_by_name.get(hp.lower())
  if anchor is None:anchor={'id':hp,'parent':parent['id'],'type':'NULL_OR_HARDPOINT','local_transform':[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],[0.,0.,0.]],'data':None};m.nodes.append(anchor)
  anchor['parent']=parent['id'];anchor['local_transform'][3]=local(np.array(pos)+[0,.1,0]);podmoves.append({'node':hp,'position':anchor['local_transform'][3]})
 if n=='xbassimst':
  anchor=node_by_name.get(d.get('buildhardpoint','build').lower());assert anchor
  anchor['parent']=parent['id'];anchor['local_transform'][3]=local(geometry.build)
 # Supply any legacy ODF hardpoint references missing in the original model.
 text=Path(d['file']).read_text(encoding='latin1');present={z['id'].lower()for z in m.nodes};added=[]
 for k,values in re.findall(r'(?mi)^[ \t]*([A-Za-z0-9_]*Hardpoints?|weaponHardpoints[0-9]+)[ \t]*=[ \t]*([^\r\n]*)',text):
  for hp in re.findall(r'"([A-Za-z0-9_]+)"',values):
   if hp.lower()in present:continue
   m.nodes.append({'id':hp,'parent':parent['id'],'type':'NULL_OR_HARDPOINT','local_transform':[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],[0.,0.,0.]],'data':None});present.add(hp.lower());added.append(hp)
 alias='dr26_'+n;dest=overlay/'SOD'/(alias+'.sod');dest.parent.mkdir(parents=True,exist_ok=True);writer=IO();writer.curr_sod_version=m.version
 with contextlib.redirect_stdout(io.StringIO()):writer.write_file(m,str(dest))
 m=load_model(dest);(overlay/'SOD'/(oldalias+'.sod')).unlink();assert len(podmoves)==len(active['pods'])
 rel=Path(d['file']).relative_to(root).as_posix();settext(rel,put(text,'baseName','"'+alias+'"'));im=preview(m,256);im.save(stage/(n+'-preview.png'))
 labels=['science']if active['kind']=='research'else['repair']if active['kind']=='repair'else['metal','repair']if active['kind']=='recycler'else['science','defence']if n=='btechass'else['defence','yard']if n=='xbassimst'else['defence']if active['kind']=='assimilation'else['bio']if active['race']=='species8472'else['dil']
 color=(245,210,60)if'science'in labels else(240,90,70)if'defence'in labels else(90,220,135);icon=im.convert('RGBA');dr=ImageDraw.Draw(icon);dr.rectangle((2,2,253,253),outline=color+(255,),width=5)
 for i,label in enumerate(labels[:2]):x=164 if i==0 else 4;dr.rounded_rectangle((x,4,x+88,92),radius=10,fill=(5,11,20,248),outline=ns['colors'][label]+(255,),width=4);icon.alpha_composite(symbol(label),(x,4));dr=ImageDraw.Draw(icon)
 tex='gb'+alias;portrait='wf'+alias;icon.resize((64,64),Image.Resampling.LANCZOS).convert('RGB').save(overlay/'Textures/RGB'/(tex+'.tga'));im.resize((64,64),Image.Resampling.LANCZOS).convert('RGB').save(overlay/'Textures/RGB'/(portrait+'.tga'))
 for key in ['b_'+n,'b_'+alias]+[p+'w'+str(i)for p in [n,alias]for i in range(1,6)]:sprite=re.sub(r'(?mi)^'+re.escape(key)+r'[ \t]+[^\r\n]*','',sprite)
 sprite+='\n@reference=64\n@tmaterial=default\nb_'+n+' '+tex+' 0 0 64 64\nb_'+alias+' '+tex+' 0 0 64 64\n'
 for p in [n,alias]:
  for i in range(1,6):sprite+=p+'w'+str(i)+' '+portrait+' 0 0 64 64\n'
 records.append({**active,'model':alias,'sourceModel':d.get('basename',n),'podMounts':podmoves,'legacyAnchorsAdded':added,'badges':labels,'animationChannels':len(m.animation_transforms),'productionNode':d.get('buildhardpoint')if n=='xbassimst'else None})
settext('Sprites/gui_global.spr',sprite)
for rel,t in pending.items():dest=overlay/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'))
for category,kinds in [('freighters',['freighter']),('refineries',['refinery']),('research',['research']),('borg-utility',['assimilation','recycler','repair'])]:
 rows=[r for r in records if r['kind']in kinds];sheet=Image.new('RGB',(1280,70+((len(rows)+3)//4)*295),(9,16,24));dr=ImageDraw.Draw(sheet);dr.text((20,18),category.upper()+' — ACTUAL STAGED MODELS',font=font,fill=(225,205,155))
 for i,r in enumerate(rows):x=(i%4)*320;y=70+(i//4)*295;sheet.paste(Image.open(stage/(r['unit']+'-preview.png')),(x+32,y));dr.text((x+12,y+260),r['unit']+' | '+str(len(r['pods']))+' pods'if r['pods']else r['unit'],font=font,fill=(205,215,225))
 sheet.save(stage/(category+'-preview.png'))
files={p.relative_to(overlay).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in overlay.rglob('*')if p.is_file()};report={'status':'STAGED - NOT APPLIED','stage':str(stage),'files':files,'sourceHashes':sourcehashes,'units':records,'gameplayFieldsChanged':False,'startingFleetsChanged':False,'runtimeVerified':False};(stage/'manifest.json').write_text(json.dumps(report,indent=2));(repo/'reports/resource-science-redesign-staged.json').write_text(json.dumps(report,indent=2));emit('Upgraded resource / research and Borg utility designs staged: '+str(len(records))+' models; all pod mounts included. Validation pending.')
