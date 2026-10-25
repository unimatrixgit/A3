from pathlib import Path
import json,re,hashlib,datetime,subprocess,shutil,os,math
from collections import Counter
from PIL import Image,ImageDraw,ImageFont
root=Path('D:/armadaIII');repo=Path('D:/aramada');pack=json.loads((repo/'reports/unit-identity-applied.json').read_text());P=json.loads((repo/'reports/function-badges-before.json').read_text());stage=Path('D:/Xaramada-Modwork/function-badges-and-scale-stage');stage.mkdir(exist_ok=True);atlases={};pending={};records=[]
HWP=['fhwp','bhwp','khwp','rhwp','chwp','bjhwp','dturret3'];colors={'dil':(85,235,250),'metal':(210,225,240),'lat':(255,205,70),'bio':(225,135,245),'yard':(85,175,255),'repair':(100,245,170),'science':(255,220,60),'defence':(255,95,75),'construct':(155,210,255),'colony':(110,240,155),'trade':(255,205,90),'base':(150,210,255),'scan':(255,230,100),'combat':(225,235,245),'cargo':(245,210,125)}
def badges(row):
 n=row['unit'];d=P[n];r=row['role'];cl=d.get('classlabel','');b=[]
 if r in ['HERO','MIR']:return[]
 if r=='YARD':
  b=['yard']
  if d.get('repairfacility')=='1' or cl=='shipyard'and d.get('repairfacility')!='0':b.append('repair')
 elif r in ['R&D','TECH']:b=['science']
 elif r=='SCAN':b=['science','scan']
 elif r=='FIX':b=['repair']
 elif r in ['BUILD','T2','T3']:b=['construct']
 elif r=='BASE':b=['base']
 elif r=='COL':b=['colony']
 elif r=='TRADE':b=['trade']
 elif r=='CARGO':b=['cargo']
 elif r=='DIL':b=['dil']
 elif r=='MET':b=['metal']
 elif r=='LAT':b=['lat']
 elif r=='BIO':b=['bio']
 elif r in ['HWP','TORP','BEAM']:b=['defence']
 elif r in ['BB','CR','DD','FF','FTR','ART','SHIP']:b=['combat']
 if not b:return[]
 if cl=='freighter':
  resources=d.get('resourcescanhandle','').lower()
  for word,label in [('dilithium','dil'),('latinum','lat'),('metal','metal'),('biomatter','bio')]:
   if word in resources and label not in b:b.append(label)
 if d.get('repairfacility')=='1'and'repair'not in b:b.append('repair')
 if b[0]=='defence'and any(re.fullmatch('builditem[0-9]+',k)for k in d):b.append('yard')
 if b[0]=='base'and any(re.fullmatch('weapon[0-9]+',k)and P.get(v.lower(),{}).get('special','0')!='1'for k,v in d.items()):b.append('defence')
 if b[0]=='metal'and any(re.fullmatch('weapon[0-9]+',k)and P.get(v.lower(),{}).get('special','0')!='1'for k,v in d.items()):b.append('defence')
 return list(dict.fromkeys(b))[:2]

def symbol(kind):
 # Supersampled pictograms extend the existing build-button system.
 s=4;im=Image.new('RGBA',(22*s,22*s),(0,0,0,0));dr=ImageDraw.Draw(im);c=colors[kind]+(255,);dark=(5,11,20,255)
 def line(points,width=2,fill=c):dr.line([(int(x*s),int(y*s))for x,y in points],fill=fill,width=max(1,int(width*s)),joint='curve')
 def poly(points,fill=c,outline=None,width=1):dr.polygon([(int(x*s),int(y*s))for x,y in points],fill=fill,outline=outline,width=int(width*s))
 def ellipse(box,fill=None,outline=c,width=1):dr.ellipse(tuple(int(x*s)for x in box),fill=fill,outline=outline,width=int(width*s))
 if kind=='dil':
  poly([(11,3),(17,7),(15,16),(10,19),(5,14),(6,7)],outline=(230,255,255,255));line([(11,3),(10,11),(10,19)],1,fill=(20,90,110,255));line([(6,7),(10,11),(17,7)],1,fill=(20,90,110,255))
 elif kind=='metal':
  for x,y in [(3,12),(11,12),(7,5)]:poly([(x,y+3),(x+3,y),(x+7,y),(x+9,y+3),(x+7,y+7),(x+1,y+7)],outline=(80,105,120,255))
 elif kind=='lat':
  for x,y in [(3,12),(12,12),(7,4)]:poly([(x,y+2),(x+3,y),(x+7,y),(x+8,y+6),(x+1,y+6)],outline=(140,90,20,255))
 elif kind=='science':
  for angle in [0,60,120]:
   orbit=Image.new('RGBA',im.size,(0,0,0,0));ImageDraw.Draw(orbit).ellipse((2*s,7*s,20*s,15*s),outline=c,width=1*s);im=Image.alpha_composite(im,orbit.rotate(angle,resample=Image.Resampling.BICUBIC))
  dr=ImageDraw.Draw(im);ellipse((9,9,13,13),fill=(255,245,170,255))
 elif kind in ['repair','construct']:
  line([(6,17),(15,7)],3);poly([(12,3),(12,8),(16,11),(20,9),(20,4),(17,7),(15,6),(15,3)],fill=c);ellipse((3,14,9,20),fill=c);ellipse((5,16,7,18),fill=dark,outline=dark)
  if kind=='construct':line([(5,5),(17,17)],2,fill=(240,245,255,255));poly([(3,3),(7,3),(11,7),(8,10),(4,6)],fill=(240,245,255,255))
 elif kind=='yard':
  line([(4,4),(4,18),(18,18),(18,4)],2);line([(4,7),(8,7)],1);line([(14,7),(18,7)],1);poly([(11,4),(8,11),(11,14),(14,11)],fill=(225,245,255,255));line([(11,14),(11,16)],1)
 elif kind=='defence':
  poly([(4,4),(18,4),(17,13),(11,19),(5,13)],fill=None,outline=c,width=2);line([(11,7),(11,15)],2,fill=(255,235,180,255));line([(7,11),(15,11)],2,fill=(255,235,180,255))
 elif kind=='colony':
  ellipse((3,3,19,19),outline=c);line([(4,11),(18,11)],1);dr.arc((7*s,3*s,15*s,19*s),0,360,fill=c,width=s);line([(11,3),(11,19)],1);poly([(12,6),(18,7),(12,10)],fill=(245,255,240,255))
 elif kind=='base':
  ellipse((3,7,19,15),outline=c,width=2);line([(11,3),(11,19)],2);line([(5,4),(17,18)],1);line([(17,4),(5,18)],1)
 elif kind=='trade':line([(3,7),(18,7)],2);poly([(18,7),(14,4),(14,10)]);line([(19,15),(4,15)],2);poly([(4,15),(8,12),(8,18)])
 elif kind=='scan':
  ellipse((3,3,19,19),outline=c);dr.arc((6*s,6*s,16*s,16*s),180,320,fill=c,width=s);line([(11,11),(17,5)],2);ellipse((9,9,12,12),fill=c)
 elif kind=='bio':
  for yy in [4,8,12,16]:line([(6+(yy//4%2)*2,yy),(16-(yy//4%2)*2,yy)],1)
  line([(6,3),(10,8),(6,13),(10,19)],2);line([(16,3),(12,8),(16,13),(12,19)],2)
 elif kind=='combat':line([(5,17),(17,5)],2);line([(5,5),(17,17)],2);poly([(18,3),(18,8),(14,4)]);poly([(18,19),(14,18),(18,14)])
 elif kind=='cargo':
  for x,y in [(3,11),(12,11),(7,3)]:dr.rectangle((x*s,y*s,(x+7)*s,(y+7)*s),fill=c,outline=dark,width=s)
 return im

for row in pack['units']:
 labels=badges(row)
 if not labels:continue
 tex=row['texture']
 if tex not in atlases:atlases[tex]=Image.open(root/'Textures/RGB'/(tex+'.tga')).convert('RGB')
 x,y,w,h=row['cell'];tile=atlases[tex].crop((x,y,x+w,y+h)).convert('RGBA').resize((256,256),Image.Resampling.NEAREST);dr=ImageDraw.Draw(tile)
 for j,label in enumerate(labels):
  # First badge replaces the old small label; second sits in the opposite corner.
  px=41 if j==0 else 1;py=1;col=colors[label];dr.rounded_rectangle((px*4,py*4,(px+22)*4,(py+22)*4),radius=3*4,fill=(5,11,20,248),outline=col+(255,),width=1*4);tile=Image.alpha_composite(tile,Image.new('RGBA',tile.size))
  icon=symbol(label);tile.alpha_composite(icon,(px*4,py*4));dr=ImageDraw.Draw(tile)
 atlases[tex].paste(tile.resize((64,64),Image.Resampling.LANCZOS).convert('RGB'),(x,y));records.append({'unit':row['unit'],'badges':labels,'texture':tex,'cell':row['cell']})
for n,im in atlases.items():
 out=stage/'Textures/RGB'/(n+'.tga');out.parent.mkdir(parents=True,exist_ok=True);im.save(out);pending[out.relative_to(stage).as_posix()]=out.read_bytes()
# Size edits preserve proportions, economy and combat stats. Only HWP build time also changes.
index={p.stem.lower():p for p in(root/'odf').rglob('*.odf')};scalechanges=[]
def num(v):return float(v.rstrip('fF'))
def put(t,k,v):return re.sub(r'(?mi)^[ \t]*'+re.escape(k)+r'\s*=[^\r\n]*','',t)+'\n'+k+' = '+format(v,'.12g')+'\n'
for n in ['unicomplex']+HWP:
 src=index[n];d=P[n];factor=.65 if n=='unicomplex'else .9;t=src.read_text(encoding='latin1');vals={};before={}
 for key,odfkey in [('scalesod','ScaleSOD'),('footprintbuffer','footprintBuffer')]:
  if key in d:before[odfkey]=num(d[key]);vals[odfkey]=before[odfkey]*factor;t=put(t,odfkey,vals[odfkey])
 if n in HWP:before['buildTime']=num(d['buildtime']);vals['buildTime']=before['buildTime']*.75;t=put(t,'buildTime',vals['buildTime'])
 rel=src.relative_to(root).as_posix();pending[rel]=t.replace('\r','').replace('\n','\r\n').encode('latin1');scalechanges.append({'unit':n,'before':before,'after':vals})
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running; patch stays prepared'
backup=Path('D:/Xaramada-Modwork/backups')/('function-badges-scale-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));written=[]
try:
 for rel,data in pending.items():
  out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
  for label,base in [('live',root),('repository',repo/'bajor/overlay')]:
   dst=base/rel;b=backup/label/rel;existed=dst.exists()
   if existed:b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,b);os.chmod(dst,0o666)
   dst.parent.mkdir(parents=True,exist_ok=True);written.append((dst,b,existed));dst.write_bytes(data);assert dst.read_bytes()==data
except Exception:
 for dst,b,existed in reversed(written):
  if existed:shutil.copy2(b,dst)
  elif dst.exists():dst.unlink()
 raise
stamp=datetime.datetime.now().astimezone().isoformat();r={'applied':True,'appliedAt':stamp,'backup':str(backup),'stage':str(stage),'badges':records,'dualBadgeCount':sum(len(x['badges'])==2 for x in records),'scaleChanges':scalechanges,'files':list(pending),'manifest':[{'file':f,'sha256':hashlib.sha256(v).hexdigest()}for f,v in pending.items()],'heroEmblemsPreserved':True,'portraitResourcesChanged':False,'runtimeVerified':False};(repo/'reports/function-badges-scale.json').write_text(json.dumps(r,indent=2))
chosen=['fyard','byard','8472_fluidicgate','bjyard','fmining','bbase2','dfreight','xfgmine','fresear','rresear','fremmeler','bjrepair','fhwp','bhwp','bjcolony','bjconst'];sheet=Image.new('RGB',(640,240),(8,15,24));draw=ImageDraw.Draw(sheet);ff=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12);units={x['unit']:x for x in pack['units']}
for j,n in enumerate(chosen):
 a=units[n];x,y,w,h=a['cell'];px=(j%8)*80;py=(j//8)*120;sheet.paste(atlases[a['texture']].crop((x,y,x+w,y+h)),(px+8,py+8));draw.text((px+2,py+78),n[:11],font=ff,fill=(225,235,245))
sheet.save(repo/'reports/function-badges-preview.png');p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Applied pictogram build badges to'+str(len(records))+' units, including'+str(r['dualBadgeCount'])+' dual-function pairs. Crystal/ingot/atom/dock/shield/wrench symbols; hero emblems and working portraits preserved. Central Unicomplex size/footprint -35%; all7 HWP size/footprint -10%, build time -25%. Combat stats/costs/crew unchanged. File checks passed; gameplay test pending.';s['updated']=stamp;p.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n['+stamp+'] '+s['current']+' Backup:'+str(backup)+'\n')
print(json.dumps({'badgeUnits':len(records),'dualBadges':r['dualBadgeCount'],'scaleChanges':scalechanges,'backup':str(backup)}))
