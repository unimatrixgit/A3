import pathlib,re,json,sys,contextlib,io,hashlib,numpy as np
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils');from sod_io import SodIO
class IO(SodIO):
 def read_unknown_legacy_data(self,s):return []if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
root=pathlib.Path('D:/armadaIII');repo=pathlib.Path('D:/aramada');stage=pathlib.Path('D:/Xaramada-Modwork/bajor-cardassian-style');idx={f.stem.lower():f for f in (root/'odf').rglob('*.odf')};textures={f.stem.lower()for f in (root/'Textures').rglob('*.tga')};cache={}
def props(n,seen=None):
 if n in cache:return cache[n]
 seen=set()if seen is None else seen
 if n in seen:return{}
 seen.add(n);t=idx[n].read_text(encoding='latin1');v={}
 for inc in re.findall(r'^[ \t]*#include[ \t]+"([^"\r\n]+)"',t,re.M):v.update(props(inc.lower().removesuffix('.odf'),seen.copy()))
 for k,x in re.findall(r'^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t,re.M):v[k.lower()]=x.split('//')[0].strip()
 cache[n]=v;return v
def val(v,k,d=''):return v.get(k,d).strip('"')
def extent(s):
 nodes={n['id']:n for n in s.nodes};memo={}
 def world(n,seen=None):
  if n['id']in memo:return memo[n['id']]
  seen=set()if seen is None else seen
  if n['id']in seen:return np.eye(4)
  seen.add(n['id']);t=np.array(n['local_transform']);a=np.eye(4);a[:3,:3]=t[:3].T;a[:3,3]=t[3];parent=nodes.get(n['parent']);a=world(parent,seen)@a if parent else a;memo[n['id']]=a;return a
 vs=[(world(n)@np.c_[np.asarray(n['data']['vertices']),np.ones(len(n['data']['vertices']))].T).T[:,:3]for n in s.nodes if n['type']=='MESH'and n['data']['vertices']]
 return float(np.ptp(np.concatenate(vs),axis=0).max())
def readmodel(n):
 with contextlib.redirect_stdout(io.StringIO()):return IO().read_file(str(root/'SOD'/(n+'.sod')))
def setv(t,k,v):return re.sub(r'^[ \t]*'+re.escape(k)+r'[ \t]*=[^\r\n]*(?:\r?\n)?','',t,flags=re.M|re.I).rstrip()+'\r\n'+k+' = '+v+'\r\n'
pairs={'bjmining':'cmining','bjyard':'cyard','bjyard2':'cyard2','bjyard3':'cyard2','bjresear':'cresear','bjresear2':'cresear2','bjupgrade':'cupgrade','bjsensor':'csensor','bjorbital':'corbital','bjtrading':'ctrading','bjturret':'cturret','bjturret2':'cturret2','bjsuperlab':'cardassian_super_station'};files=[];models=[];errors=[]
def save(rel,text):
 out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(text.encode('latin1'));files.append({'path':rel,'sourceSha256':hashlib.sha256((root/rel).read_bytes()).hexdigest(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
for target,source in pairs.items():
 v=props(target);native=props(source);model=val(native,'basename',source);s=readmodel(model);old=readmodel(val(v,'basename',target));names={n['id'].lower():n['id']for n in s.nodes};hps=sorted([n for n in names if re.fullmatch('hp[0-9]+',n)],key=lambda n:int(n[2:]));fallback=hps or list(names)
 for n in s.nodes:
  if n['type']=='MESH':
   for tex in [n['data']['texture'],n['data'].get('borgification',{}).get('texture','')]:
    if tex and tex!='_B'and tex.lower()not in textures:errors.append({'unit':target,'missingTexture':tex})
 rel='odf/stations/'+target+'.odf';original=(root/rel).read_text(encoding='latin1');text=setv(original,'baseName','"'+model+'"');scale=extent(old)*float(val(v,'scalesod','1'))/extent(s);text=setv(text,'ScaleSOD',str(round(scale,6)));keys=set(k for k in v if 'hardpoint'in k)|set(k for k in native if 'hardpoint'in k)
 for key in sorted(keys):
  proposed=native.get(key,v.get(key,''));refs=re.findall(r'"([^"\r\n]+)"',proposed);refs=[names.get(h.lower(),names[fallback[i%len(fallback)]])for i,h in enumerate(refs)]
  if not refs:refs=[names[fallback[0]]]
  text=setv(text,key,' '.join('"'+h+'"'for h in refs))
 def gameplay(t):return '\n'.join(l for l in t.splitlines()if not re.match(r'^[ \t]*(?:baseName|ScaleSOD|\w*hardpoints?\d*)[ \t]*=',l,re.I)).strip()
 if gameplay(text)!=gameplay(original):errors.append({'unit':target,'error':'Unexpected nonvisual change'})
 save(rel,text);models.append({'unit':target,'source':source,'model':model,'scale':scale,'nativeSodUnmodified':True,'nativeAnimationsRetained':True,'mappedHardpoints':len(keys)})
# Match the Cardassian core build-menu progression while retaining advanced overflow on Universal.
rel='odf/ships/bjconst.odf';original=(root/rel).read_text(encoding='latin1');items=['bjbase','bjyard','bjsensor','bjturret','bjmining','bjresear','bjresear2','bjyard2','bjturret2','bjorbital','bjtrading','bjupgrade'];olditems=re.findall(r'^[ \t]*buildItem\d+[ \t]*=[ \t]*"([^"]+)"',original,re.M|re.I)
if set(items)!=set(olditems):errors.append({'error':'Constructor building access would change'})
text=re.sub(r'^[ \t]*buildItem\d+[ \t]*=[^\r\n]*(?:\r?\n)?','',original,flags=re.M|re.I).rstrip()+'\r\n\r\n// Bajoran facilities ordered like the Cardassian core construction menu.\r\n'+'\r\n'.join('buildItem'+str(i)+' = "'+n+'"'for i,n in enumerate(items))+'\r\n';save(rel,text)
# Alias each existing native Cardassian icon with its original texture reference size/material.
spr=(root/'Sprites/gui_global.spr').read_text(encoding='latin1');entries={};ref='256';mat='default'
for l in spr.splitlines():
 if l.strip().startswith('@reference='):ref=l.strip().split('=',1)[1]
 elif l.strip().startswith('@tmaterial='):mat=l.strip().split('=',1)[1]
 elif l.strip()and not l.lstrip().startswith(('#','//','@')):
  a=l.strip().split(None,1)
  if len(a)==2:entries[a[0].lower()]=(a[1],ref,mat)
for target,source in pairs.items():
 for a,b in [('b_'+target,'b_'+source)]+[(target+'w'+str(i),source+'w'+str(i))for i in range(1,6)]:
  e=entries.get(b.lower())
  if not e:errors.append({'unit':target,'missingNativeSprite':b});continue
  payload,ref,mat=e;spr=re.sub(r'^[ \t]*'+a+r'[ \t]+[^\r\n]*(?:\r?\n)?','',spr,flags=re.M|re.I).rstrip()+'\r\n@reference='+ref+'\r\n@tmaterial='+mat+'\r\n'+a+' '+payload+'\r\n'
save('Sprites/gui_global.spr',spr)
report={'target':str(root),'stage':str(stage),'files':files,'models':models,'constructorItems':items,'errors':errors,'ds9Preserved':True,'nativeBinaryModelsAndTexturesUnmodified':True,'harvesterConfigurationAndFreighterUntouched':True,'aiAudioTechStatsPreserved':True,'sourceExamples':['https://www.startrek.com/news/first-look-official-starships-collections-deep-space-9','https://www.startrek.com/news/designing-the-first-cardassian-warship'],'applied':False,'runtimeVerified':False};(repo/'reports/bajoran-cardassian-style.json').write_text(json.dumps(report,indent=2));print(json.dumps({'files':len(files),'nativeBuildingModels':len(models),'errors':errors}));sys.exit(bool(errors))
