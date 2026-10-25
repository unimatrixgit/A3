"""Complete tier icon badges and dependency-ordered AI support in the staged patch."""
from pathlib import Path
import json,re,hashlib
from PIL import Image,ImageDraw,ImageFont
root=Path('D:/armadaIII');repo=Path('D:/aramada');stage=repo/'patches/mining-yards-20261025';O=stage/'overlay'
report=json.loads((stage/'gameplay.json').read_text());idx={p.stem.lower():p for p in(root/'odf').rglob('*.odf')};idx.update({p.stem.lower():p for p in(O/'odf').rglob('*.odf')})
def props(n,seen=None):
 seen=set()if seen is None else seen
 if n in seen:return{}
 seen.add(n);t=idx[n].read_text(encoding='latin1');d={}
 for inc in re.findall(r'(?mi)^[ \t]*#include[ \t]+"([^"]+)"',t):d.update(props(Path(inc).stem.lower(),seen))
 for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t):d[k.lower()]=v.split('//')[0].strip().strip('"')
 return d
P={n:props(n)for n in idx}
def put(t,k,v):return re.sub(r'(?mi)^[ \t]*'+re.escape(k)+r'[ \t]*=[^\r\n]*','',t).rstrip()+'\n'+k+' = '+str(v)+'\n'
def save(rel,t):
 dest=O/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'))

# Dedicated Ferengi resource variants use the same tier capacity multipliers.
for prefix in ['xfg','xbg']:
 for resource,key,base in [('dil','maxDilithium',300)]+([('lat','maxLatinum',150)]if prefix=='xfg'else[]):
  for suffix,mult in [('2',1.5),('3',2)]:
   n=prefix+resource+suffix;rel=idx[n].relative_to(O).as_posix()if idx[n].is_relative_to(O)else idx[n].relative_to(root).as_posix()
   save(rel,put(idx[n].read_text(encoding='latin1'),key,round(base*mult)))

sprite=(O/'Sprites/gui_global.spr').read_text(encoding='latin1');texidx={p.stem.lower():p for p in(root/'Textures').rglob('*.tga')};texidx.update({p.stem.lower():p for p in(O/'Textures').rglob('*.tga')})
font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',15)
def icon(key):
 m=re.search(r'(?mi)^'+re.escape(key)+r'[ \t]+([^\r\n]+)',sprite);assert m,key
 ref=int(re.findall(r'(?mi)^@reference[ \t]*=[ \t]*(\d+)',sprite[:m.start()])[-1]);parts=m[1].split();im=Image.open(texidx[parts[0].lower()]).convert('RGB');x,y,w,h=[float(v)*im.width/ref for v in parts[1:5]]
 return im.crop((round(x),round(y),round(x+w),round(y+h))).resize((64,64),Image.Resampling.LANCZOS)
minerlevels={n:(i+1)for r in report['yards']for i,n in enumerate(r['miners'])}
for n in ['xfgmine','xbgmine','xfgdil2','xfgdil3','xbgdil2','xbgdil3','xfglat2','xfglat3','xfgmnr1','xfgmnr2','xbgmnr1','xbgmnr2']:
 minerlevels[n]=3 if n.endswith(('3','mnr2'))else 2 if n.endswith(('2','mnr1'))else 1
minerlevels['xdominer']=1
for i,(n,level)in enumerate(minerlevels.items()):
 im=icon('b_'+n);d=ImageDraw.Draw(im);text=['I','II','III'][level-1];d.rounded_rectangle((39,43,63,63),radius=4,fill=(7,30,23),outline=(110,245,175),width=2);d.text((44 if level<3 else 41,44),text,font=font,fill=(235,255,235));texture='gbmyminer'+str(i).zfill(2);im.save(O/'Textures/RGB'/(texture+'.tga'))
 sprite=re.sub(r'(?mi)^b_'+re.escape(n)+r'[ \t]+[^\r\n]*','',sprite);sprite+='\n@reference=64\n@tmaterial=default\nb_'+n+' '+texture+' 0 0 64 64\n'
save('Sprites/gui_global.spr',sprite)

# Production graph includes secondary pod slots; AI never requests a tier before its
# research, yard and available builder have appeared in that same faction's plan.
tech={}
for line in(O/'techtree/tech1.tt').read_text(encoding='latin1').splitlines():
 a=line.split('//')[0].split()
 if len(a)>=2 and a[0].lower().endswith('.odf'):tech[Path(a[0]).stem.lower()]=(int(a[1]),[Path(x).stem.lower()for x in a[2:2+max(0,int(a[1]))]])
producers={}
for n,d in P.items():
 for k,v in d.items():
  if re.fullmatch(r'(?:secondary)?builditem\d+',k):producers.setdefault(v.lower(),[]).append(n)
rowpat=re.compile(r'(?m)^[ \t]*"([^"]+)"[ \t]*,[^\r\n]*')
for cfg in report['yards']:
 for file in(O/'AI/AIPs').glob(cfg['race']+'_*list.aip'):
  text=file.read_text(encoding='latin1');matches=list(rowpat.finditer(text));available={m[1].lower()for m in matches};plan=[];trail=[]
  def ensure(n,stack=()):
   if n in available:return
   assert n not in stack,('AI production cycle',file.name,n,stack)
   assert n in tech and tech[n][0]>=0,(file.name,n,'disabled technology')
   for dep in tech[n][1]:ensure(dep,stack+(n,))
   candidates=sorted(producers.get(n,[]),key=lambda x:(x not in available,P[x].get('race')!=cfg['race'],x))
   if not any(x in available for x in candidates):
    possible=[x for x in candidates if P[x].get('race')in[cfg['race'],'ferengi']and x not in stack and x!=n]
    assert possible,(file.name,n,'no producer',candidates)
    # Prefer the native constructor; do not recurse through a foreign starbase.
    possible.sort(key=lambda x:(not(P[x].get('classlabel')=='constructionrig'and P[x].get('race')==cfg['race']),x))
    solved=False;errors=[]
    for producer in possible:
     saved=set(available);length=len(plan)
     try:ensure(producer,stack+(n,));solved=True;break
     except AssertionError as e:available.clear();available.update(saved);del plan[length:];errors.append(str(e))
    assert solved,(file.name,n,'no reachable producer',errors)
   plan.append(n);available.add(n)
  for n in cfg['miners'][1:]:ensure(n)
  # Existing plans already include many research rows. Append only absent support.
  last=matches[-1];block=''.join('\n    "'+n+'", 1, 0, -1, 0, // mining research / production support'for n in plan)
  text=text[:last.end()]+block+text[last.end():];save(file.relative_to(O).as_posix(),text)
  rows=list(rowpat.finditer(text));names=[m[1].lower()for m in rows]
  for tier,n in enumerate(cfg['miners']):
   assert n in names,(file,n)
   pos=names.index(n);assert cfg['yard']in names[:pos],(file,n,'yard order')
   if tier:assert cfg['pods'][tier-1]in names[:pos],(file,n,'research order')
  trail.append({'file':file.name,'addedSupport':plan})
  for r in report['ai']:
   if r['file']==file.name:r['addedSupport']=plan;r['tieredMiners']=cfg['miners'][1:]
(stage/'gameplay.json').write_text(json.dumps(report,indent=2));(repo/'reports/mining-yards-prepared.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'tierIcons':len(minerlevels),'AIplans':len(report['ai']),'nativeYards':len(report['yards'])}))
