from pathlib import Path
exec(Path('scripts/stage-armadafiles-yards-20261031.py').read_text().split('targets=[]')[0])
import datetime,subprocess
manifest=json.loads((stage/'manifest.json').read_text());src=source('borg-incursion-2','domyard');raw=src.read_bytes();m=load(src);available={n['id'].lower()for n in m.nodes};texture_src=next(p for p in packagefiles['borg-incursion-2']if p.name.lower()=='zjemyard.tga');pending={'Textures/RGB/Zjemyard.tga':texture_src.read_bytes()};records=[]
for row in manifest['units']:
 if Path(row['sourceModel']).stem.lower()!='domyard':continue
 pending[row['model']]=raw;p=root/row['odf'];text=p.read_text(encoding='latin1');d=cache[row['unit']];changes={}
 for key,value in d.items():
  if key in ['buildhardpoint','repairhardpoint']:new='"build"'
  elif re.fullmatch('weaponhardpoints[0-9]+',key):new='"hp'+str(1+(int(key[len('weaponhardpoints'):])-1)%8).zfill(2)+'"'
  elif key.endswith('targethardpoints'):
   hp=[h for h in re.findall(r'\w+',value)if h.lower()in available];new=' '.join('"'+h+'"'for h in hp)if hp else'"hp01"'
  else:continue
  pattern=r'(?mi)^(\s*'+key+r'\s*=\s*)[^\r\n]*'
  if re.search(pattern,text):text=re.sub(pattern,lambda match:match[1]+new,text)
  else:text+='\r\n'+key+' = '+new+'\r\n'
  changes[key]=new
 for k,v in changes.items():assert set(h.lower()for h in re.findall(r'\w+',v))<=available
 pending[row['odf']]=text.encode('latin1');records.append({'unit':row['unit'],'model':row['model'],'hardpoints':changes})
assert len(records)==5
assert subprocess.check_output(['powershell','-NoProfile','-Command','@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'],text=True).strip()=='0'
backup=Path('D:/Xaramada-Modwork/backups')/('dominion-original-sod-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
for rel,data in pending.items():
 p=root/rel
 if p.exists():
  b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(p.read_bytes());p.chmod(0o666)
 p.write_bytes(data);out=repo/'bajor/overlay'/rel;out.parent.mkdir(parents=True,exist_ok=True)
 if out.exists():out.chmod(0o666)
 out.write_bytes(data);assert p.read_bytes()==out.read_bytes()
for row in records:assert(root/row['model']).read_bytes()==raw
r={'backup':str(backup),'originalSource':str(src),'sourceSha256':hashlib.sha256(raw).hexdigest(),'changes':records,'installedFiles':list(pending),'validation':'Five game models now byte-identical to original downloaded SOD. All ODF hardpoints checked against its native nodes. Original texture supplied. Costs, build lists, technology and weapon definitions unchanged.','runtimeVerified':False,'causeConfirmed':False};(repo/'reports/dominion-original-sod-20261031.json').write_text(json.dumps(r,indent=2)+'\n')
p=repo/'status.json';d=json.loads(p.read_text());d['current']='Dominion white-cube recovery installed:5 yard variants now use byte-identical original downloaded legacy SOD, with original Zjemyard hull texture and native hardpoints selected through ODFs. No model serialization or mesh changes. Game model loading and AI construction need fresh-match retest.';p.write_text(json.dumps(d,indent=2)+'\n')
with(repo/'build.log').open('a')as f:f.write('\n'+datetime.datetime.now().isoformat()+' '+d['current']+'\n')
subprocess.run(['git','add','-f','--',*['bajor/overlay/'+p for p in pending],'scripts/fix-dominion-original-sod-20261031.py','reports/dominion-original-sod-20261031.json','status.json','build.log'],check=True);print(d['current'])
