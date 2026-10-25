"""Build native SOD models and matching icon/portrait assets for the mining yards."""
from pathlib import Path
exec(Path('D:/aramada/scripts/build-bajor-redesign-v4.py').read_text().split('for name,d in before.items():')[0])
import ast,importlib.util,shutil
source=(repo/'scripts/stage-approved-visual-refresh.py').read_text();tree=ast.parse(source)
for node in tree.body:
 if isinstance(node,ast.FunctionDef)and node.name in ['load_model','visible_points','construct_model']:exec(compile(ast.Module(body=[node],type_ignores=[]),str(repo/'scripts/stage-approved-visual-refresh.py'),'exec'))
sp=importlib.util.spec_from_file_location('base_geometry',repo/'scripts/approved-station-geometry.py');B=importlib.util.module_from_spec(sp);sp.loader.exec_module(B)
stage=repo/'patches/mining-yards-20261025';overlay=stage/'overlay';report=json.loads((stage/'gameplay.json').read_text());P=json.loads((repo/'reports/mining-yard-before.json').read_text())
for d in P.values():d['file']=str(root/d['file'])
tiles={'federation':0,'borg':1,'klingon':2,'romulan':3,'cardassian':4,'dominion':5,'bajoran':6,'breen':7,'ferengi':8,'species8472':9}
for i in range(16):texidx['vr26t'+str(i).zfill(2)]=root/'Textures/RGB'/('vr26t'+str(i).zfill(2)+'.tga')
sprite=(overlay/'Sprites/gui_global.spr').read_text(encoding='latin1')
ns={};exec((repo/'scripts/apply-function-badges-scale.py').read_text().split("for row in pack['units']:")[0],ns);symbol=ns['symbol']
font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',24)

class Factory:
 def yard(self,race,tier,service):
  global geometry
  if service:
   g=B.Geometry();g.cylinder((0,.2,-.25),.74,.32,n=24);g.sphere((0,.46,-.25),(.66,.28,.62));g.cylinder((0,.77,-.25),.2,.25,n=16)
   g.torus((0,.2,-.05),1.15,.2,n=28,start=.08*math.pi,end=.92*math.pi,stretch=(1,.8,1))
   for s in [-1,1]:
    g.sphere((s*.92,.14,-.1),(.38,.26,.55));g.beam((s*.46,.1,-.25),(s*.96,.1,.65),.16);g.box((s*.75,-.05,.68),(.24,.18,1.1),taper=.7);g.beam((s*.75,.08,.2),(s*.75,.08,1.1),.04,'glow')
  else:
   g=B.yard(race,1,True)
   # A short, open assembly lane instead of the normal warship-yard silhouette.
   for part in g.parts:part['v'][:,2]*=.82
   if race=='federation':g.cylinder((0,.47,-.65),.58,.15,n=28);g.cylinder((0,.64,-.65),.25,.2,n=16)
   elif race=='borg':
    for x in [-.75,-.25,.25,.75]:g.box((x,.55,-.72),(.27,.35,.3));g.box((x,.78,-.72),(.15,.06,.15),'glow')
    g.box((.66,.85,-.5),(.32,.75,.35))
   elif race=='klingon':
    for s in [-1,1]:g.box((s*.88,.6,-.55),(.2,.85,.4),yaw=s*.28,taper=.05)
   elif race=='romulan':g.torus((0,.6,-.4),1.05,.08,n=28,start=.06*math.pi,end=.94*math.pi,stretch=(1,.6,.65))
   elif race=='cardassian':
    for s in [-1,1]:g.beam((s*.95,.35,.2),(0,1.1,-.7),.15);g.box((s*.65,.2,-.65),(.3,.35,.5),taper=.6)
   elif race=='dominion':
    for s in [-1,1]:g.sphere((s*.63,.5,-.65),(.45,.25,.58));g.sphere((s*.63,.69,-.65),(.17,.07,.25),'glow')
   elif race=='bajoran':g.torus((0,.55,-.25),.95,.07,n=26,start=.04*math.pi,end=.96*math.pi,stretch=(1,.7,.85));g.cylinder((0,.78,-.7),.09,.55,n=12)
   elif race=='breen':g.box((.7,.7,-.6),(.3,.85,.4));g.box((-.75,.45,-.5),(.45,.4,.55),yaw=.2)
   elif race=='species8472':g.sphere((0,.65,-.65),(.45,.5,.35));g.sphere((0,.82,-.6),(.2,.2,.2),'glow')
   for s in [-1,1]:
    # Resource containers and cranes distinguish the new civilian yards.
    for z in [-.35,.05]:g.box((s*1.05,-.05,z),(.18,.22,.25),'pipes')
    g.beam((s*.9,.35,.6),(s*.9,.65,.6),.055,'dark');g.beam((s*.9,.65,.6),(s*.55,.65,.6),.045,'dark')
  geometry=g;return g
G=Factory();records=[]
targets=[(r['yard'],r['race'],r['donor'],False)for r in report['yards']]+[('xfgserv','ferengi','xfgserv',True),('xbgserv','ferengi','xbgserv',True)]
for number,(n,race,donor,service)in enumerate(targets,1):
 print('Model '+str(number)+'/'+str(len(targets))+': '+n,flush=True)
 # Keep constructor launch/repair graph; replace visible geometry only.
 model,alias=construct_model(n,{'kind':'yard','race':race,'tier':1,'donor':donor})
 oldfile=overlay/'SOD'/(alias+'.sod');newalias='my26_'+n;dest=overlay/'SOD'/(newalias+'.sod');oldfile.replace(dest)
 odf=overlay/'odf/stations'/(n+'.odf');t=odf.read_text(encoding='latin1')
 t=put(t,'baseName','"'+newalias+'"')
 if not service:
  t=put(t,'buildHardpoint','"'+P[donor].get('buildhardpoint','build')+'"');t=put(t,'repairHardpoint','"'+P[donor].get('repairhardpoint','repair')+'"')
  # Consistent compact civilian size, preserving proportions.
  pts=visible_points(model);scale=105/np.ptp(pts,axis=0).max();t=put(t,'ScaleSOD',format(scale,'.10g'));t=put(t,'footprintBuffer',70)
  # Put production/repair sockets in the open dock rather than inside the new hull.
  parent=next(z for z in model.nodes if not z['parent']);inv=np.linalg.inv(matrix(parent));center=(pts.max(0)+pts.min(0))/2
  for hp,pos in [(P[donor].get('buildhardpoint','build'),(0,-8,34)),(P[donor].get('repairhardpoint','repair'),(0,-8,15))]:
   node=next((z for z in model.nodes if z['id'].lower()==hp.lower()),None)
   if node is None:node={'id':hp,'parent':parent['id'],'type':'NULL_OR_HARDPOINT','local_transform':[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],[0.,0.,0.]],'data':None};model.nodes.append(node)
   node['parent']=parent['id'];node['local_transform'][3]=(inv@np.r_[center+np.array(pos)/scale,1])[:3].tolist()
  writer=IO();writer.curr_sod_version=model.version
  with contextlib.redirect_stdout(io.StringIO()):writer.write_file(model,str(dest))
 odf.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'))
 check=load_model(dest)
 if check.version>1.9101:assert all(z['data'].get('bump_map')==1 for z in check.nodes if z['type']=='MESH')
 image=preview(check,256);image.save(stage/(n+'-preview.png'));portrait=image.resize((64,64),Image.Resampling.LANCZOS).convert('RGB');icon=image.convert('RGBA')
 # Match the existing blue yard category, with separate mining and repair badges.
 tint=Image.new('RGBA',(256,256),(0,0,0,0));dr=ImageDraw.Draw(tint)
 for y in range(256):dr.line((0,y,255,y),fill=(70,160,250,int(y/255*32)))
 icon=Image.alpha_composite(icon,tint);dr=ImageDraw.Draw(icon);dr.rectangle((1,1,254,254),outline=(85,175,255,255),width=5)
 for label,x in [('yard',4),('repair',164)]:
  dr.rounded_rectangle((x,4,x+88,92),radius=10,fill=(5,11,20,245),outline=ns['colors'][label]+(255,),width=4);icon.alpha_composite(symbol(label),(x,4));dr=ImageDraw.Draw(icon)
 dr.rectangle((5,194,250,250),fill=(6,25,20,245));icon.alpha_composite(symbol('bio'if race=='species8472'else'dil').resize((48,48)),(8,196));dr=ImageDraw.Draw(icon);dr.text((64,206),'MINING'if not service else'SERVICE',font=font,fill=(110,245,175))
 tex='gb'+newalias;wf='wf'+newalias;texdir=overlay/'Textures/RGB';texdir.mkdir(parents=True,exist_ok=True);icon.resize((64,64),Image.Resampling.LANCZOS).convert('RGB').save(texdir/(tex+'.tga'));portrait.save(texdir/(wf+'.tga'))
 for key in ['b_'+n,'b_'+newalias]+[p+'w'+str(i)for p in [n,newalias]for i in range(1,6)]:sprite=re.sub(r'(?mi)^'+re.escape(key)+r'[ \t]+[^\r\n]*','',sprite)
 sprite+='\n@reference=64\n@tmaterial=default\nb_'+n+' '+tex+' 0 0 64 64\nb_'+newalias+' '+tex+' 0 0 64 64\n'
 for p in [n,newalias]:
  for i in range(1,6):sprite+=p+'w'+str(i)+' '+wf+' 0 0 64 64\n'
 records.append({'unit':n,'model':newalias,'race':race,'serviceStarbase':service,'sourceModel':P[donor].get('basename',donor)})

# Federation's independent mining contracts need two persistent research pods.
# Add an actual sixth socket rather than replacing the first research pod.
research=load_model(root/'SOD'/(P['fresear2']['basename']+'.sod'));anchor=next(z for z in research.nodes if z['id'].lower()=='mirrorpod');new=copy.deepcopy(anchor);new['id']='myminingpod';position=new['local_transform'][3];position[0]=-position[0]if abs(position[0])>5 else position[0]+35;research.nodes.append(new)
researchalias='my26_fresear2';writer=IO();writer.curr_sod_version=research.version
with contextlib.redirect_stdout(io.StringIO()):writer.write_file(research,str(overlay/'SOD'/(researchalias+'.sod')))
researchfile=overlay/'odf/stations/fresear2.odf';t=put(researchfile.read_text(encoding='latin1'),'baseName','"'+researchalias+'"');researchfile.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'))
for newkey,oldkey in [('b_'+researchalias,'b_fresear2')]+[(researchalias+'w'+str(i),'fresear2w'+str(i))for i in range(1,6)]:
 m=re.search(r'(?mi)^'+re.escape(oldkey)+r'[ \t]+[^\r\n]+',sprite);assert m,oldkey;ref=re.findall(r'(?mi)^@reference[ \t]*=[ \t]*(\d+)',sprite[:m.start()])[-1];sprite+='\n@reference='+ref+'\n@tmaterial=default\n'+re.sub(r'^\S+',newkey,m[0])+'\n'

# Upgrade glyph follows the existing code-drawn icon system; the production queue
# continues using each miner's complete RGB portrait, never a badge-only mask.
upgradeicon=Image.new('RGB',(64,64),(8,25,35));d=ImageDraw.Draw(upgradeicon);d.rounded_rectangle((1,1,62,62),radius=8,outline=(90,210,245),width=3);d.polygon([(32,8),(52,30),(41,30),(41,53),(23,53),(23,30),(12,30)],fill=(105,245,175));upgradeicon.save(overlay/'Textures/RGB/gbmyupgrade.tga')
(overlay/'Sprites/gui_global.spr').write_bytes(sprite.replace('\r','').replace('\n','\r\n').encode('latin1'))
sheet=Image.new('RGB',(1280,70+3*300),(9,16,24));d=ImageDraw.Draw(sheet);d.text((20,18),'MINING YARDS — ACTUAL STAGED GAME MODELS',font=font,fill=(220,225,235))
for i,r in enumerate(records):
 x=(i%4)*320;y=70+(i//4)*300;sheet.paste(Image.open(stage/(r['unit']+'-preview.png')),(x+32,y));d.text((x+10,y+260),r['race']+' | '+r['unit'],font=font,fill=(185,210,225))
sheet.save(stage/'models-preview.png');(stage/'artwork.json').write_text(json.dumps(records,indent=2))
print('Built',len(records),'models, build icons and status/queue portraits.')
