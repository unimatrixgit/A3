from pathlib import Path
import json,re,hashlib,datetime,shutil,os,subprocess
from PIL import Image
repo=Path('D:/aramada');root=Path('D:/armadaIII');pack=json.loads((repo/'reports/unit-identity-applied.json').read_text());sprite=(root/'Sprites/gui_global.spr').read_text(encoding='latin1');stage=Path('D:/Xaramada-Modwork/bajoran-style-ship-portraits');stage.mkdir(exist_ok=True);idx={p.stem.lower():p for p in(root/'odf').rglob('*.odf')};pending={};rows=[];aliases={};textures={}
# Match the working Bajoran hotfix: standalone RGB TGA, full-image coordinates,
# identical resource for all five wireframe slots, and both ODF/model aliases.
for row in pack['units']:
 if '/ships/'not in row['odf'].lower()or row['race']=='bajoran':continue
 n=row['unit'];text=idx[n].read_text(encoding='latin1');m=re.findall(r'(?mi)^\s*baseName\s*=\s*"([^"]+)"',text);model=m[-1].lower()if m else row['model'];name='xqw_'+n
 if row['texture']not in textures:textures[row['texture']]=Image.open(root/'Textures/RGB'/(row['texture']+'.tga')).convert('RGB')
 x,y,w,h=row['cell'];im=textures[row['texture']].crop((x,y,x+w,y+h));assert im.size==(64,64);rel='Textures/RGB/'+name+'.tga';out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True);im.save(out);pending[rel]=out.read_bytes();mapped=[]
 for source in sorted({n,model}):
  for i in range(1,6):
   key=source+'w'+str(i)
   if key in aliases:continue
   aliases[key]=name;mapped.append(key);sprite=re.sub(r'(?mi)^'+re.escape(key)+r'[ \t]+[^\r\n]*','',sprite);sprite+='\n@reference=64\n@tmaterial=default\n'+key+' '+name+' 0 0 64 64\n'
 rows.append({'unit':n,'model':model,'texture':name,'aliases':mapped})
for r in rows:
 for i in range(1,6):assert re.search(r'(?mi)^'+re.escape(r['unit']+'w'+str(i))+r'\s+\S+\s+0\s+0\s+64\s+64\s*$',sprite),r['unit']
pending['Sprites/gui_global.spr']=sprite.replace('\r','').replace('\n','\r\n').encode('latin1')
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running; patch staged'
backup=Path('D:/Xaramada-Modwork/backups')/('bajoran-style-portraits-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));written=[]
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
r={'applied':True,'appliedAt':datetime.datetime.now().astimezone().isoformat(),'backup':str(backup),'stage':str(stage),'method':'Working Bajoran standalone RGB image with full0,0,64,64 coordinates in all five ship portrait slots','shipsUpdated':len(rows),'workingBajoranPortraitsPreserved':True,'rows':rows,'files':list(pending),'manifest':[{'file':f,'sha256':hashlib.sha256(v).hexdigest()}for f,v in pending.items()],'ODFsAndGameplayChanged':False,'runtimeVerified':False};(repo/'reports/bajoran-style-portraits.json').write_text(json.dumps(r,indent=2));p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Applied working Bajoran standalone-image method to'+str(len(rows))+' other-faction ship queue/status portraits. No atlas or transparent-mask portrait resources; all five slots use full individual RGB image. Working Bajoran mappings, category build gradients, HWP badges, names/tooltips and gameplay retained. Gameplay portrait test pending.';s['updated']=r['appliedAt'];p.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n['+s['updated']+'] '+s['current']+' Backup:'+str(backup)+'\n')
print(json.dumps({'shipsUpdated':len(rows),'spriteAliases':len(aliases),'backup':str(backup)}))
