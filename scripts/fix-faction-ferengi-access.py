"""Audit conventional-faction Ferengi access and add Federation's missing yard link."""
from pathlib import Path
import re,json,hashlib,datetime,subprocess,shutil
root=Path('D:/armadaIII');repo=Path('D:/aramada');stage=repo/'patches/faction-ferengi-access-20261025';O=stage/'overlay'
idx={p.stem.lower():p for p in(root/'odf').rglob('*.odf')};pending={};checks=[]
def props(n,seen=None):
 seen=set()if seen is None else seen
 if n in seen:return{}
 seen.add(n);p=idx[n];rel=p.relative_to(root).as_posix();t=pending[rel]if rel in pending else p.read_text(encoding='latin1');d={}
 for inc in re.findall(r'(?mi)^[ \t]*#include[ \t]+"([^"]+)"',t):d.update(props(Path(inc).stem.lower(),seen))
 for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t):d[k.lower()]=v.split('//')[0].strip().strip('"')
 return d
def ck(ok,label):
 assert ok,label
 checks.append(label)
def items(n):return[v for k,v in props(n).items()if re.fullmatch(r'builditem\d+',k)]
original=props('fconst2');f=idx['fconst2'];text=f.read_text(encoding='latin1');menu=items('fconst2')
ck('xfgmerc'not in menu,'Federation missing Contract Yard link confirmed');ck(len(menu)<14,'Federation MK II has room')
slot=max(int(k[9:])for k in original if re.fullmatch(r'builditem\d+',k))+1
text=text.rstrip()+'\r\n\r\n// Ferengi contract access: overflow from the full MK III menu.\r\nbuildItem'+str(slot)+' = "xfgmerc"\r\n';pending[f.relative_to(root).as_posix()]=text
ck({k:v for k,v in props('fconst2').items()if k!='builditem'+str(slot)}==original,'Only one Federation construction-menu entry changed')
config=[('federation','fbase','fconst2','xfg'),('borg','bbase','bconst2','xbg'),('klingon','kbase','xkuconst','xfg'),('romulan','rbase','xruconst','xfg'),('cardassian','cbase','xcuconst','xfg'),('dominion','dbase','xduconst','xfg'),('bajoran','bjbase','xbjuconst','xfg'),('breen','brbase','brconst','xfg')]
rows=[];sprite=(root/'Sprites/gui_global.spr').read_text(encoding='latin1')
for race,base,builder,prefix in config:
 yard=prefix+'merc';constructor=prefix+'const';service=prefix+'serv'
 ck(builder in items(base),race+': native builder produced at primary starbase')
 ck(yard in items(builder),race+': Contract Yard on reachable native constructor')
 ck(constructor in items(yard),race+': Ferengi assembler produced at Contract Yard')
 ck(service in items(constructor),race+': Service Yard buildable by Ferengi assembler')
 ck(prefix+'research'in items(constructor),race+': research station buildable')
 ck(prefix+'const2'in items(service),race+': second Ferengi assembler produced')
 for unit in [yard,constructor,service,prefix+'research',prefix+'const2']:
  ck(bool(re.search(r'(?mi)^b_'+unit+r'[ \t]+',sprite)),race+': existing GUI icon '+unit)
  if race=='borg':ck(float(props(unit).get('latinumcost',0))==0,'Borg: no Latinum charge '+unit)
 for tree in [root/'techtree'/(n+'.tt')for n in ['tech1','earlytech','fulltech','nosci','nosuper','nospweap']]:
  tt=tree.read_text(encoding='latin1')
  for unit in [yard,constructor,service]:
   matches=re.findall(r'(?mi)^'+unit+r'\.odf[ \t]+([^\r\n/]+)',tt);ck(len(matches)==1,tree.name+': unique '+unit);a=matches[0].split();ck(int(a[0])>=0 and int(a[0])==len(a)-1,tree.name+': enabled '+unit)
 rows.append({'race':race,'nativeBuilder':builder,'menuPosition':items(builder).index(yard)+1,'yard':yard,'FerengiAssembler':constructor,'ServiceYard':service})

pattern=re.compile(r'(?m)^[ \t]*"([^"]+)"[ \t]*,[^\r\n]*');ai=[]
fedblock=['xfgmerc','xfgconst','xfgserv','xfgconst2','xfgresearch','xfgpdil','xfgpmet','xfgplat','xfgpdil2','xfgpmet2','xfgplat2','xfgmnr1','xfgmnr2','xfgmetal2','xfgmetal3','xfgdref']
for race,base,builder,prefix in config:
 for file in(root/'AI/AIPs').glob(race+'_*list.aip'):
  t=file.read_text(encoding='latin1');matches=list(pattern.finditer(t));names=[m[1].lower()for m in matches];added=[]
  if race=='federation':
   ck(builder in names,file.name+': Federation MK II is already ordered')
   added=[n for n in fedblock if n not in names]
   last=matches[-1];block=''.join('\n    "'+n+'", 1, 0, -1, 0, // Ferengi construction / research access'for n in added)
   t=t[:last.end()]+block+t[last.end():];pending[file.relative_to(root).as_posix()]=t
   names=[m[1].lower()for m in pattern.finditer(t)]
  for a,b in [(builder,prefix+'merc'),(prefix+'merc',prefix+'const'),(prefix+'const',prefix+'serv'),(prefix+'serv',prefix+'const2'),(prefix+'const',prefix+'research')]:
   ck(a in names and b in names and names.index(a)<names.index(b),file.name+': '+a+' before '+b)
  ai.append({'file':file.name,'added':added,'pathVerified':True})
ck(len(ai)==40,'All 40 eligible faction AI profiles checked')
for n in ['8472_passive','714const','xsuconst']:
 ck(not any(x.startswith(('xfg','xbg'))for x in items(n)),'Species 8472 Ferengi exclusion preserved: '+n)
files=[]
for rel,t in pending.items():
 out=O/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));files.append({'file':rel,'sourceHash':hashlib.sha256((root/rel).read_bytes()).hexdigest(),'stagedHash':hashlib.sha256(out.read_bytes()).hexdigest()})
report={'status':'STAGED','factions':rows,'ai':ai,'checks':len(checks),'files':files,'runtimeVerified':False,'species8472':'Excluded as previously requested','newSpritesNeeded':False}
(stage/'manifest.json').write_text(json.dumps(report,indent=2));(repo/'reports/faction-ferengi-access.json').write_text(json.dumps(report,indent=2))
running=subprocess.run(['powershell','-NoProfile','-Command','@(Get-CimInstance Win32_Process -Filter "Name=\'Armada2.exe\' OR Name=\'Armada.exe\'").Count'],capture_output=True,text=True,check=True)
if int(running.stdout.strip()or'0'):
 print(json.dumps({'status':'STAGED - GAME RUNNING','files':len(files),'checks':len(checks)}));raise SystemExit(0)
backup=Path('D:/Xaramada-Modwork/backups')/('faction-ferengi-access-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
for r in files:
 rel=r['file'];ck(hashlib.sha256((root/rel).read_bytes()).hexdigest()==r['sourceHash'],'live baseline unchanged '+rel);out=backup/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,out)
changed=[]
try:
 for r in files:
  rel=r['file'];(root/rel).chmod(0o666);shutil.copyfile(O/rel,root/rel);changed.append(rel);assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==r['stagedHash']
except Exception:
 for rel in changed:shutil.copyfile(backup/rel,root/rel)
 raise
for r in files:
 rel=r['file'];dest=repo/'bajor/overlay'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/rel,dest)
report.update(status='APPLIED - GAMEPLAY TEST PENDING',backup=str(backup));(repo/'reports/faction-ferengi-access-applied.json').write_text(json.dumps(report,indent=2))
s=json.loads((repo/'status.json').read_text(encoding='utf-8-sig'));s['current']='Ferengi access audited across eight conventional factions. Federation MK II now builds the Ferengi Contract Yard (12th option); its five AI profiles include Ferengi construction/research. All 40 eligible AI routes checked. Borg retains MK II access and no-Latinum prices; 8472 remains excluded. Gameplay test pending.';(repo/'status.json').write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as log:log.write('\n[Ferengi access] Applied '+str(len(files))+' files; '+str(len(checks))+' checks. Federation MK II -> Contract Yard -> Ferengi assembler -> Service Yard. Eight factions / 40 AI profiles audited. Backup '+str(backup)+'. Gameplay test pending.\n')
print(json.dumps({'status':report['status'],'files':len(files),'checks':len(checks),'backup':str(backup),'routes':rows},indent=2))
