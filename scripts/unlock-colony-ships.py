from pathlib import Path
exec(Path('D:/aramada/scripts/build-mirror-ferengi-research.py').read_text().split('# Existing Cardassian artwork')[0])
import shutil,subprocess,os,hashlib
assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running'
colonies=sorted(n for n in index if resolve(n).get('classlabel')=='colony'and resolve(n).get('unitname'));pending={};old={}
for tree in ['tech1','earlytech','fulltech','nosci','nospweap','nosuper']:
 rel='techtree/'+tree+'.tt';lines=[];removed=[]
 for line in(root/rel).read_text(encoding='latin1').splitlines():
  a=line.split('//')[0].split()
  if a and Path(a[0]).stem.lower()in colonies:removed.append(line);continue
  lines.append(line)
 lines+=['','// Colony vessels are available without technology prerequisites.']+[n+'.odf 0'for n in colonies];pending[rel]='\n'.join(lines)+'\n';old[tree]=removed
 for n in colonies:assert len(re.findall(r'(?mi)^'+re.escape(n)+r'\.odf\s+0\s*$',pending[rel]))==1
backup=Path('D:/Xaramada-Modwork/backups')/('colony-no-tech-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));manifest=[]
for rel,t in pending.items():
 data=t.replace('\r','').replace('\n','\r\n').encode('latin1')
 for label,base in [('live',root),('repository',repo/'bajor/overlay')]:
  dst=base/rel;b=backup/label/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,b);os.chmod(dst,0o666);dst.write_bytes(data);assert dst.read_bytes()==data
 manifest.append({'file':rel,'sha256':hashlib.sha256(data).hexdigest()})
r={'applied':True,'appliedAt':datetime.datetime.now().astimezone().isoformat(),'backup':str(backup),'colonies':colonies,'previousRequirements':old,'files':list(pending),'manifest':manifest,'runtimeVerified':False,'producerRequirement':'An owned producer is still needed; no colony research or prerequisite structures required by technology tree.'};(repo/'reports/colony-no-tech.json').write_text(json.dumps(r,indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Applied839 three-line tooltips: name / special powers or function / lore(max50 characters). Names and icons unchanged. Removed tech gates from all10 colony-ship definitions in all6 tech trees. Icons-only loading confirmed by user; new tooltip display/loading test pending.';s['updated']=r['appliedAt'];p.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n['+s['updated']+'] '+s['current']+' Backup:'+str(backup)+'\n')
print(json.dumps({'unlockedColonyShips':colonies,'trees':len(pending),'backup':str(backup)}))
