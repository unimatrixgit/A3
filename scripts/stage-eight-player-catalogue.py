from pathlib import Path
import json,re,hashlib
root=Path('D:/armadaIII');work=Path('D:/Xaramada-Modwork/eight-player-completion');stage=work/'stage';stage.mkdir(exist_ok=True);archives=json.loads((work/'extraction.json').read_text());existing={hashlib.sha256(p.read_bytes()).hexdigest():p.name for p in(root/'bzn').glob('*.bzn')};idx={p.stem.lower()for p in(root/'odf').rglob('*.odf')};rows=[];files=[]
def players(b):
 end=b.find(b'LoadBarGameObject');head=b[:end if end>0 else 12000];return len(re.findall(rb'\x06\x00\x00\x00player',head))
for x in archives:
 for path in x.get('maps',[]):
  p=Path(path);b=p.read_bytes();h=hashlib.sha256(b).hexdigest();n=players(b);row={'source':x['url'],'title':x['title'],'map':p.name,'bytes':len(b),'detectedPlayerStarts':n,'sha256':h}
  if x['title']in ["From Hell's Heart",'Praxsis','Tadeja','Time']:row['status']='excluded Fleet Operations requirement'
  elif n!=8:row['status']='excluded not verified eight-player binary header'
  elif h in existing:row['status']='already present (identical map)';row['existingFile']=existing[h]
  else:
   companion=next((q for q in p.parent.iterdir()if q.stem.lower()==p.stem.lower()and q.suffix.lower()=='.txt'),None);missing=[]
   if companion:
    pairs=re.findall(r'(?mi)//\s*Handle for .*?\(([^)]+)\)\s*object[ \t]+(\S+)',companion.read_text(encoding='latin1'));missing=sorted({cls for cls,obj in pairs if cls.lower()not in idx and not any(obj.lower().startswith(n) and obj[len(n):].isdigit() for n in idx)})
   if missing:row['status']='excluded missing object definitions';row['missingObjects']=missing
   elif x.get('extraAssets'):row['status']='excluded archive requires extra assets; preserve current environment'
   else:
    stem=p.stem
    if(root/'bzn'/p.name).exists():stem='AF8_'+x['url'].split('/')[-2].replace('-','_')[:35]+'_'+p.stem
    for q in p.parent.iterdir():
     if q.is_file()and q.stem.lower()==p.stem.lower()and q.suffix.lower()in ['.bzn','.bmp','.txt']:
      name=stem+q.suffix.lower();dest=stage/name
      if(root/'bzn'/name).exists():
       if(root/'bzn'/name).read_bytes()==q.read_bytes():continue
       raise ValueError('Unexpected companion conflict '+name)
      dest.write_bytes(q.read_bytes());files.append({'path':'bzn/'+name,'stage':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
    row['status']='staged';row['installedName']=stem+'.bzn';existing[h]=stem+'.bzn'
  rows.append(row)
r={'target':str(root),'archivesChecked':len(archives),'mapCandidates':len(rows),'maps':rows,'files':files,'applied':False,'runtimeVerified':False,'method':'Eight typed player-start strings in native BZN header; compared with all 25 earlier known-eight maps. Archive requirements and companion object references checked where available. No ODF/model/texture imports; existing map files never overwritten.'};Path('D:/aramada/reports/eight-player-map-completion.json').write_text(json.dumps(r,indent=2));from collections import Counter;print(json.dumps({'statuses':dict(Counter(x['status']for x in rows)),'stagedFiles':len(files)}))
