from pathlib import Path
import re,json,datetime,sys,contextlib,io,math
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils')
from sod_io import SodIO
from PIL import Image,ImageDraw
class R(SodIO):
 def read_unknown_legacy_data(self,s):return []if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
root=Path('D:/armadaIII');repo=Path('D:/aramada');backup=Path('D:/Xaramada-Modwork/backups')/('dominion-three-heroes-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));pending={};binary={};records=[];liveidx={p.stem.lower():p for p in(root/'odf').rglob('*.odf')};sprite=(root/'Sprites/gui_global.spr').read_text(encoding='latin1')
def read(rel):return(root/rel).read_text(encoding='latin1')
def put(t,k,v):return re.sub(r'(?mi)^[ \t]*'+k+r'\s*=[^\r\n]*','',t)+'\n'+k+' = '+str(v)+'\n'
def load(p):
 with contextlib.redirect_stdout(io.StringIO()):return R().read_file(str(p))
def mesh_triangles(m):
 nodes={n['id'].lower():n for n in m.nodes};tri=[]
 for n in m.nodes:
  if n['type']!='MESH':continue
  chain=[];c=n
  while c:chain.append(c['local_transform']);c=nodes.get(c.get('parent','').lower())
  verts=[]
  for vertex in n['data']['vertices']:
   v=list(vertex)
   for tr in chain:v=[sum(v[i]*tr[i][j]for i in range(3))+tr[3][j]for j in range(3)]
   verts.append(v)
  for group in n['data']['vertex_lighting_groups']:
   for face in group['faces']:tri.append([verts[p[0]]for p in face])
 return tri
def render_icon(m,size,wire=False):
 triangles=mesh_triangles(m);projected=[]
 for t in triangles:
  # Orthographic model rendering, no changes to source art.
  verts=[(v[0]+v[2]*.32,-v[1]-v[2]*.64,v[2]-v[1])for v in t];projected.append(verts)
 pts=[p for t in projected for p in t];minx=min(p[0]for p in pts);maxx=max(p[0]for p in pts);miny=min(p[1]for p in pts);maxy=max(p[1]for p in pts);scale=(size-8)/max(maxx-minx,maxy-miny);im=Image.new('RGB',(size,size),(5,10,16));d=ImageDraw.Draw(im)
 for t in sorted(projected,key=lambda t:sum(v[2]for v in t)):
  points=[((p[0]-(minx+maxx)/2)*scale+size/2,(p[1]-(miny+maxy)/2)*scale+size/2)for p in t]
  if wire:d.line(points+[points[0]],fill=(60,180,190),width=1)
  else:
   a,b,c=t;light=int(85+45*abs(math.sin(sum(p[2]for p in t)*.1)));d.polygon(points,fill=(light,light+8,min(255,light+20)),outline=(35,55,65))
 if not wire:d.rectangle((0,0,size-1,size-1),outline=(160,115,70),width=2)
 stream=io.BytesIO();im.save(stream,format='TGA');return stream.getvalue()
def alias_ability(alias,source,button,popup,pod):
 global sprite
 t=read('odf/special_weapons/'+source+'.odf')
 for k,v in {'buttonSlot':button,'popupSlot':popup,'hotkeyLabel':'"HOTKEY_F'+str(button)+'"','assimilatable':'"'+pod+'"'}.items():t=put(t,k,v)
 pending['odf/special_weapons/'+alias+'.odf']=t
 m=re.search(r'(?mi)^b_'+source+r'[ \t]+[^\r\n]+',sprite);assert m,(source,'icon');refs=re.findall(r'(?mi)^@reference\s*=\s*(\d+)',sprite[:m.start()]);sprite+='\n@reference='+refs[-1]+'\n@tmaterial=default\n'+re.sub(r'^\S+','b_'+alias,m[0])+'\n'
 return alias,pod
specials={}
odo=Path('D:/Xaramada-Modwork/odo-battleship/payload');laan=Path('D:/Xaramada-Modwork/laaan-cruiser/payload/Dominion Special Forces')
configs=[{'alias':'xhdodo','name':"Odo's Battleship",'source':odo/'dsuper.odf','sod':odo/'dsuper.SOD','health':3500,'regen':15,'energy':1800,'recharge':18,'crew':725,'maxcrew':1000,'officers':12,'dil':440,'metal':190,'time':125,'scale':1.5,'role':'battleship','normal':['zjmphas','zdpulse','zdpulse','jmphot','jmphot'],'abilities':[('xhodobr','gdcteam',1,1,'dompod2'),('xhodosh','domgshieldd',2,2,'dompod1')]},{'alias':'xhdlaan','name':"La'aans Cruiser",'source':laan/'odf/ships/warcruiser.odf','sod':laan/'SOD/warcruiser.sod','health':3000,'regen':15,'energy':1600,'recharge':16,'crew':450,'maxcrew':600,'officers':10,'dil':380,'metal':165,'time':100,'scale':1.6,'role':'cruiser','normal':['zjmphas','zdpulse','zdpulse','jmphot'],'abilities':[('xhlpol','dgpolerond',1,1,'dompod4'),('xhlspy','gdomspy',2,2,'dompod3')]}]
for c in configs:
 n=c['alias'];assert n not in liveidx;m=load(c['sod']);nodes={x['id'].lower():x['id']for x in m.nodes};hps=sorted((h for h in nodes if re.fullmatch(r'hp\d+',h)),key=lambda h:int(h[2:]));assert len(hps)>=7
 t=c['source'].read_text(encoding='latin1');t=re.sub(r'(?mi)^[ \t]*weapon(?:Hardpoints)?\d+\s*=[^\r\n]*','',t)
 values={'unitName':'"'+c['name']+'"','label':'"'+c['name']+'"','tooltip':'"Hero Ship ('+c['name']+')"','verboseTooltip':'"Dominion command hero. Built at the Founders Command Yard; special abilities require Dominion research."','baseName':'"'+n+'"','race':'"dominion"','isHero':1,'shipclass':'"'+c['role']+'"','maxHealth':c['health'],'shieldRate':c['regen'],'shieldProtection':'1.0','maxSpecialEnergy':c['energy'],'specialEnergyRate':c['recharge'],'crewCost':c['crew'],'maximumCrew':c['maxcrew'],'officerCost':c['officers'],'dilithiumCost':c['dil'],'metalCost':c['metal'],'latinumCost':0,'biomatterCost':0,'buildTime':c['time'],'ScaleSOD':c['scale'],'possibleCraftNames':'"'+c['name']+'"','hotkeyLabel':'"HOTKEY_F'+('4'if n=='xhdodo'else'6')+'"'}
 for k in ['shieldGeneratorHitPoints','enginesHitPoints','weaponsHitPoints','lifeSupportHitPoints','sensorsHitPoints']:values[k]=int(c['health']*.2)
 for k,v in values.items():t=put(t,k,v)
 for k in re.findall(r'(?mi)^\s*(\w*TargetHardpoints)\s*=',t):t=put(t,k,' '.join('"'+nodes[h]+'"'for h in hps[:5]))
 banks=list(c['normal'])
 for a,s,b,p,pod in c['abilities']:specials[a]=pod;alias_ability(a,s,b,p,pod);banks.append(a)
 for i,w in enumerate(banks,1):
  assert w in liveidx or w in specials
  hp=hps[(i-1)%len(hps)];t+='\nweapon'+str(i)+' = "'+w+'"\nweaponHardpoints'+str(i)+' = "'+nodes[hp]+'"\n'
 pending['odf/ships/'+n+'.odf']=t;binary['SOD/'+n+'.sod']=c['sod'].read_bytes();binary['Textures/RGB/gb'+n+'.tga']=render_icon(m,64);binary['Textures/RGB/wf'+n+'.tga']=render_icon(m,256,True)
 sprite+='\n@reference=64\n@tmaterial=default\nb_'+n+' gb'+n+' 0 0 64 64\n@reference=256\n'
 for i in range(1,6):sprite+=n+'w'+str(i)+' wf'+n+' 0 0 256 256\n'
 textureSource=odo if n=='xhdodo'else laan/'Textures/RGB';lookup={p.stem.lower():p for p in textureSource.glob('*')if p.suffix.lower()=='.tga'}
 for node in m.nodes:
  if node['type']!='MESH':continue
  tex=node['data']['texture'];assert tex.lower()in lookup,tex;source=lookup[tex.lower()];binary['Textures/RGB/'+source.name]=source.read_bytes();borg=node['data'].get('borgification',{}).get('texture')
  if borg:binary['Textures/RGB/'+borg+'.tga']=lookup.get(borg.lower(),source).read_bytes()
 binary['Credits/'+n+'-Readme'+('.doc'if n=='xhdodo'else'.txt')]=(odo/'Readme.doc'if n=='xhdodo'else laan/'Readme.txt').read_bytes()
 records.append({'unit':n,'name':c['name'],'health':c['health'],'shieldRegen':c['regen'],'energy':c['energy'],'recharge':c['recharge'],'normalBanks':len(c['normal']),'specials':[s[1]for s in c['abilities']]})
# Same Founders hero, separate production alias so either yard can offer it without cross-faction tech requirements.
t=read('odf/ships/xdjacht.odf');t=put(t,'hotkeyLabel','"HOTKEY_F5"');pending['odf/ships/xhdjacht.odf']=t
for old,new in [('b_xdjacht','b_xhdjacht')]+[('xdjachtw'+str(i),'xhdjachtw'+str(i))for i in range(1,6)]:
 m=re.search(r'(?mi)^'+old+r'[ \t]+[^\r\n]+',sprite);assert m;refs=re.findall(r'(?mi)^@reference\s*=\s*(\d+)',sprite[:m.start()]);sprite+='\n@reference='+refs[-1]+'\n@tmaterial=default\n'+re.sub(r'^\S+',new,m[0])+'\n'
rel='odf/stations/dyard3.odf';t=read(rel);items=['xhdhero','dbattle2','xdcarrier','xhdodo','xhdjacht','xhdlaan'];t=re.sub(r'(?mi)^[ \t]*buildItem\d+\s*=[^\r\n]*','',t);t+='\n'+''.join('buildItem'+str(i)+' = "'+n+'"\n'for i,n in enumerate(items));pending[rel]=t;pending['Sprites/gui_global.spr']=sprite
for tree in ['tech1','earlytech','fulltech','nosci','nosuper','nospweap']:
 rel='techtree/'+tree+'.tt';t=read(rel)
 for n in ['xhdodo','xhdjacht','xhdlaan']:assert not re.search(r'(?mi)^'+n+r'\.odf\s',t);t+='\n'+n+'.odf '+('0'if tree=='fulltech'else'1 dyard3.odf')+' // Dominion command hero\n'
 for n,pod in specials.items():t+='\n'+n+'.odf '+('0'if tree=='fulltech'else'-1'if tree=='nospweap'else'1 '+pod+'.odf')+' // Native Dominion hero ability research\n'
 pending[rel]=t
for rel,data in binary.items():
 dest=root/rel
 if dest.exists():assert dest.read_bytes()==data,('asset collision',rel)
 pending[rel]=data
for rel,t in pending.items():
 f=root/rel
 if f.exists():
  b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(f.read_bytes());f.chmod(0o666)
 data=t if isinstance(t,bytes)else t.replace('\r','').replace('\n','\r\n').encode('latin1');f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data);out=repo/'bajor/overlay'/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
report={'backup':str(backup),'heroes':records,'foundersJacht':'xhdjacht shares existing hero stats, Outpost version retained','commandYardMenu':items,'strengthReferences':'Weyoun health3000 regen15; Founders jacht health3000 regen15 normalDPS74. Odo nominalDPS72, Laan62. No combat simulation.','research':specials,'startingFleetsChanged':False,'runtimeVerified':False};(repo/'reports/dominion-three-heroes.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
