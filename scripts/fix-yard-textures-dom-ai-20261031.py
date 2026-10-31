from pathlib import Path
import json,re,datetime,subprocess,hashlib
exec(Path('scripts/stage-armadafiles-yards-20261031.py').read_text().split('targets=[]')[0])
manifest=json.loads((stage/'manifest.json').read_text());fixstage=repo/'patches/yard-texture-dom-ai-20261031';fixoverlay=fixstage/'overlay';fixoverlay.mkdir(parents=True,exist_ok=True);pending={};fixed=[]
for row in manifest['textureDefinitions']:
 if not row['file'].lower().endswith('.bmp'):continue
 pack=row['package'];name=row['original'];choices=[p for p in packagefiles[pack]if p.stem.lower()==name and p.suffix.lower()=='.tga'and not any(x in str(p).lower()for x in['admirals','shipimages'])]
 if not choices:choices=[p for p in(root/'Textures/RGB').glob('*')if p.stem.lower()==name and p.suffix.lower()=='.tga']
 assert choices,(pack,name);src=choices[0];im=Image.open(src);assert im.width&(im.width-1)==0 and im.height&(im.height-1)==0
 rel='Textures/RGB/'+row['renamed']+'.tga';out=fixoverlay/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(src.read_bytes());pending[rel]=out.read_bytes();texidx[row['renamed']]=out;fixed.append({'oldThumbnail':row['file'],'correctTexture':rel,'source':str(src),'alias':row['renamed'],'size':im.size})
affected=[];font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',13)
for row in manifest['units']:
 model=load(root/row['model']);used={n['data']['texture'].lower()for n in model.nodes if n['type']=='MESH'}
 if not used&{r['alias']for r in fixed}:continue
 im=preview(model,200).resize((64,64),Image.Resampling.LANCZOS).convert('RGB');icon=im.copy();draw=ImageDraw.Draw(icon);draw.rectangle((0,0,63,63),outline=(110,175,210),width=2)
 for prefix,img in [('gb',icon),('wf',im)]:
  rel='Textures/RGB/'+prefix+Path(row['model']).stem+'.tga';p=fixoverlay/rel;p.parent.mkdir(parents=True,exist_ok=True);img.save(p);pending[rel]=p.read_bytes()
 affected.append(row['unit'])
profiles=[]
for p in sorted((root/'AI/AIPs').glob('dominion_*list.aip')):
 text=p.read_text(encoding='latin1');lines=text.splitlines(keepends=True)
 def unit(line):
  m=re.match(r'\s*"([^"]+)"',line);return m[1]if m else''
 yi=next(i for i,l in enumerate(lines)if unit(l)=='dyard');ci=next(i for i,l in enumerate(lines)if unit(l)=='dconst');assert ci<yi
 line=lines.pop(yi);lines.insert(ci+1,line);text=''.join(lines)
 rows=re.findall(r'(?m)^\s*"([^"]+)"\s*,\s*(\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)',text);avail={Path(v).stem.lower()for k,v in cache['dominion'].items()if re.fullmatch('standardunits[0-9]+',k)}
 for i,row in enumerate(rows):
  n=row[0];g,deps=tech.get(n,(0,[]));assert n in avail or(g>=0 and set(deps)<=avail and producers.get(n,set())&avail),(p.name,i,n)
  avail.add(n)
 rel=p.relative_to(root).as_posix();pending[rel]=text.encode('latin1');profiles.append({'file':rel,'opening':[r[0]for r in rows[:12]],'steps':len(rows)})
assert subprocess.check_output(['powershell','-NoProfile','-Command','@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'],text=True).strip()=='0','Game must be closed'
backup=Path('D:/Xaramada-Modwork/backups')/('yard-textures-dom-ai-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
for rel,data in pending.items():
 p=root/rel
 if p.exists():
  b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(p.read_bytes());p.chmod(0o666)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);out=repo/'bajor/overlay'/rel;out.parent.mkdir(parents=True,exist_ok=True)
 if out.exists():out.chmod(0o666)
 out.write_bytes(data);assert p.read_bytes()==out.read_bytes()
report={'backup':str(backup),'textureCorrections':fixed,'yardIconsUpdated':affected,'all55YardTextureMappingsReviewed':True,'dominionProfiles':profiles,'installedFiles':list(pending),'runtimeVerified':False,'limitations':'Dominion yard-first ordering removes the initial mining-station request from its path to a shipyard. The actual runtime stall cause is unconfirmed and needs a fresh-match retest.'};(repo/'reports/yard-textures-dom-ai-20261031.json').write_text(json.dumps(report,indent=2)+'\n')
p=repo/'status.json';d=json.loads(p.read_text());d['current']=f'White yard textures corrected:3 thumbnail BMPs replaced by actual hull TGAs, affecting{len(affected)} yards; matching icons refreshed. All55 yard texture mappings reviewed. Dominion5 profiles now request yard before mining station; static checks pass, runtime stall resolution pending.';p.write_text(json.dumps(d,indent=2)+'\n')
with(repo/'build.log').open('a')as f:f.write('\n'+datetime.datetime.now().isoformat()+' '+d['current']+'\n')
subprocess.run(['git','add','-f','--',*['bajor/overlay/'+r for r in pending],'reports/yard-textures-dom-ai-20261031.json','scripts/stage-armadafiles-yards-20261031.py','scripts/fix-yard-textures-dom-ai-20261031.py','status.json','build.log'],check=True);print(d['current'])
