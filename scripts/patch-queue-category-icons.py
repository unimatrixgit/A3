from pathlib import Path
import json,re,hashlib,datetime,shutil,os,subprocess
from PIL import Image,ImageDraw,ImageFont
repo=Path('D:/aramada');root=Path('D:/armadaIII');identity=json.loads((repo/'reports/unit-identity-applied.json').read_text());stage=Path('D:/Xaramada-Modwork/queue-category-icons-stage');stage.mkdir(exist_ok=True);sprite=(root/'Sprites/gui_global.spr').read_text(encoding='latin1');oldSpriteHash=hashlib.sha256((root/'Sprites/gui_global.spr').read_bytes()).hexdigest();atlas={};pending={};cats={};rows=[];font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',13)
colors={'yard':(55,145,255),'mining':(55,220,95),'defence':(255,65,55),'technology':(250,215,45)}
def category(row):
 r=row['role']
 if r=='YARD':return 'yard'
 if r in ['DIL','MET','BIO','LAT']:return 'mining'
 if r in ['HWP','TORP','BEAM']:return 'defence'
 if r in ['TECH','R&D','SCAN']:return 'technology'
 return None
for row in identity['units']:
 name=row['texture']
 if name not in atlas:atlas[name]=Image.open(root/'Textures/RGB'/(name+'.tga')).convert('RGB')
 x,y,w,h=row['cell'];im=atlas[name].crop((x,y,x+w,y+h)).convert('RGBA');cat=category(row)
 if cat:
  col=colors[cat];over=Image.new('RGBA',(64,64),(0,0,0,0));dr=ImageDraw.Draw(over)
  # Restrained top-left tint; the model and top-right role/faction badge remain legible.
  for yy in range(19):
   for xx in range(46):
    alpha=int(120*(1-yy/19)*(1-xx/46));dr.point((xx,yy),fill=col+(alpha,))
  im=Image.alpha_composite(im,over);ImageDraw.Draw(im).rectangle((0,0,63,63),outline=col+(255,),width=2)
 if row['role']=='HWP':
  dr=ImageDraw.Draw(im);red=(255,65,55,255);dr.rectangle((1,1,62,62),outline=red,width=3);dr.line((4,6,18,6),fill=(255,230,125),width=2);dr.line((4,6,4,20),fill=(255,230,125),width=2);dr.line((45,6,59,6),fill=(255,230,125),width=2);dr.line((59,6,59,20),fill=(255,230,125),width=2);dr.rectangle((2,47,61,61),fill=(65,8,12,255));box=dr.textbbox((0,0),'HWP',font=font);dr.text(((64-(box[2]-box[0]))/2,46),'HWP',font=font,fill=(255,245,210,255),stroke_width=1,stroke_fill=(60,0,0,255))
 atlas[name].paste(im.convert('RGB'),(x,y));cats[row['unit']]=cat;rows.append({**row,'categoryOverlay':cat})
for n,im in atlas.items():
 out=stage/'Textures/RGB'/(n+'.tga');out.parent.mkdir(parents=True,exist_ok=True);im.save(out);pending[out.relative_to(stage).as_posix()]=out.read_bytes()
# Queue image uses the same five-part wireframe resource as the status pane.
# Five transparent spatial masks reconstruct the exact icon and retain per-system tint layers.
ships=[r for r in rows if '/ships/'in r['odf'].lower()];queue=[];sheets=[];qa=None;cellcount=0;aliasmap={};unitidx={p.stem.lower():p for p in(root/'odf').rglob('*.odf')}
def add(key,tex,x,y):
 global sprite
 sprite=re.sub(r'(?mi)^'+re.escape(key)+r'[ \t]+[^\r\n]*','',sprite);sprite+='\n@reference=512\n@tmaterial=default\n'+key+' '+tex+' '+str(x)+' '+str(y)+' 64 64\n'
for r in ships:
 n=r['unit'];text=unitidx[n].read_text(encoding='latin1');matches=re.findall(r'(?mi)^\s*baseName\s*=\s*"([^"]+)"',text);model=matches[-1].lower()if matches else r['model'];x,y,w,h=r['cell'];im=atlas[r['texture']].crop((x,y,x+w,y+h)).convert('RGBA');keys=[]
 for j in range(5):
  page=cellcount//64;cell=cellcount%64;tex='xqicons'+str(page).zfill(2)
  if cell==0:
   if qa is not None:sheets.append((prevtex,qa))
   qa=Image.new('RGBA',(512,512),(0,0,0,0));prevtex=tex
  layer=Image.new('RGBA',(64,64),(0,0,0,0));a=round(j*64/5);b=round((j+1)*64/5);layer.paste(im.crop((a,0,b,64)),(a,0));xx=(cell%8)*64;yy=(cell//8)*64;qa.paste(layer,(xx,yy));cellcount+=1
  for alias in set([n,model]):
   key=alias+'w'+str(j+1)
   # Shared models already have identical role/faction icons or unique model aliases.
   if key in aliasmap:continue
   add(key,tex,xx,yy);aliasmap[key]=(tex,xx,yy);keys.append(key)
 queue.append({'unit':n,'model':model,'wireframeAliases':keys})
if qa is not None:sheets.append((prevtex,qa))
for n,im in sheets:
 out=stage/'Textures/RGB'/(n+'.tga');im.save(out);pending[out.relative_to(stage).as_posix()]=out.read_bytes()
out=stage/'Sprites/gui_global.spr';out.parent.mkdir(exist_ok=True);data=sprite.replace('\r','').replace('\n','\r\n').encode('latin1');out.write_bytes(data);pending['Sprites/gui_global.spr']=data
# Validate layered icon reconstruction and every ship's five mapped sprites.
for r in ships:
 for i in range(1,6):assert r['unit']+'w'+str(i)in aliasmap
for r in ships[::30]:
 layers=Image.new('RGBA',(64,64),(0,0,0,0))
 for j in range(1,6):
  t,x,y=aliasmap[r['unit']+'w'+str(j)];src=dict(sheets)[t].crop((x,y,x+64,y+64));layers=Image.alpha_composite(layers,src)
 x,y,w,h=r['cell'];assert layers.convert('RGB').tobytes()==atlas[r['texture']].crop((x,y,x+w,y+h)).tobytes(),r['unit']
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running; patch remains staged'
assert hashlib.sha256((root/'Sprites/gui_global.spr').read_bytes()).hexdigest()==oldSpriteHash,'GUI changed during preparation'
backup=Path('D:/Xaramada-Modwork/backups')/('queue-category-icons-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));written=[]
try:
 for rel,data in pending.items():
  for label,base in [('live',root),('repository',repo/'bajor/overlay')]:
   dst=base/rel;b=backup/label/rel;existed=dst.exists()
   if existed:b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,b);os.chmod(dst,0o666)
   dst.parent.mkdir(parents=True,exist_ok=True);written.append((dst,b,existed));dst.write_bytes(data);assert dst.read_bytes()==data
except Exception:
 for dst,b,existed in reversed(written):
  if existed:shutil.copy2(b,dst)
  elif dst.exists():dst.unlink()
 raise
stamp=datetime.datetime.now().astimezone().isoformat();r={'applied':True,'appliedAt':stamp,'stage':str(stage),'backup':str(backup),'shipQueueIcons':len(ships),'wireframeMappings':len(aliasmap),'queueAtlases':len(sheets),'hwpEnhanced':[x['unit']for x in rows if x['role']=='HWP'],'categoryColors':colors,'categoryUnits':{c:[n for n,v in cats.items()if v==c]for c in colors},'files':list(pending),'manifest':[{'file':f,'sha256':hashlib.sha256(v).hexdigest()}for f,v in pending.items()],'gameplayAndODFsChanged':False,'runtimeVerified':False,'sharedDisplayNote':'Stock queue and ship status share five-part wireframes; new spatial masks preserve five independently tinted regions.'};(repo/'reports/queue-category-icons.json').write_text(json.dumps(r,indent=2))
selected=[next(x for x in rows if x['unit']==n)for n in ['fyard','byard','bjyard','dmining','bbase2','bjfreight','fresear','rresear','fhwp','bhwp','chwp','bjhwp','khwp','rhwp','dturret3','fcolony']];sheet=Image.new('RGB',(640,320),(8,15,24));dr=ImageDraw.Draw(sheet);ff=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13)
for j,x in enumerate(selected):
 a,b,w,h=x['cell'];px=(j%8)*80;py=(j//8)*150;sheet.paste(atlas[x['texture']].crop((a,b,a+w,b+h)),(px+8,py+10));dr.text((px+2,py+80),x['unit'][:11],font=ff,fill=(225,235,245))
sheet.save(repo/'reports/queue-category-icons-preview.png')
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Applied ship production-queue images for'+str(len(ships))+' ship definitions, matching model-based build icons. Five status-image layers preserved with transparent masks. Gradients: yards blue, mining green, defence red, tech yellow. All7 HWP icons gain stronger red borders/large HWP badges. No ODF or gameplay changes. In-game queue/health display test pending.';s['updated']=stamp;p.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n['+stamp+'] '+s['current']+' Backup:'+str(backup)+'\n')
print(json.dumps({'shipQueueIcons':len(ships),'queueAtlasPages':len(sheets),'HWPEnhanced':r['hwpEnhanced'],'categoryCounts':{k:len(v)for k,v in r['categoryUnits'].items()},'backup':str(backup)}))
