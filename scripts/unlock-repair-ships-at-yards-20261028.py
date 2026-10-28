from pathlib import Path
import re,json,datetime,shutil,subprocess
root=Path('D:/armadaIII');repo=Path('D:/aramada')
assert subprocess.check_output(['powershell','-NoProfile','-Command','@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'],text=True).strip()=='0','Close Armada III before installation.'
pairs={'fsrepair':'xyr_f','ksrepair':'xyr_k','rsrepair':'xyr_r','csrepair':'xyr_c','dsrepair':'xyr_d','bjrepair':'xyr_bj','xbrepair':'xyr_b','xfgrepair':'xyr_fg','xbgrepair':'xyr_bg','brrepair':'xyr_br','xsrepair':'mysyard'}
backup=Path('D:/Xaramada-Modwork/backups')/('repair-yard-tech-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));changes=[]
for ship,station in pairs.items():
 assert(root/'odf/ships'/(ship+'.odf')).exists()and(root/'odf/stations'/(station+'.odf')).exists()
 text=(root/'odf/stations'/(station+'.odf')).read_text(encoding='latin1');assert re.search(r'(?mi)^buildItem\d+\s*=\s*"'+ship+'"',text)
for mode in ['tech1','earlytech','nosci','nosuper','nospweap']:
 rel=Path('techtree')/(mode+'.tt');p=root/rel;t=p.read_text(encoding='latin1');original=t
 for ship,station in pairs.items():
  pat=r'(?mi)^'+ship+r'\.odf[ \t]+[^\r\n]*';desired=ship+'.odf 1 '+station+'.odf';matches=re.findall(pat,t)
  if matches:t=re.sub(pat,lambda m:desired,t)
  else:t=t.rstrip()+'\n'+desired+'\n'
  if matches!=[desired]:changes.append({'tree':mode,'ship':ship,'before':matches,'after':desired})
 if t!=original:
  b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b);data=t.replace('\r','').replace('\n','\r\n').encode('latin1');p.write_bytes(data);(repo/'bajor/overlay'/rel).write_bytes(data)
 for ship,station in pairs.items():assert re.findall(r'(?mi)^'+ship+r'\.odf[ \t]+([^\r\n]+)',t)==['1 '+station+'.odf']
(repo/'reports/repair-yard-tech-20261028.json').write_text(json.dumps({'backup':str(backup),'mapping':pairs,'changes':changes,'fullAndFreeTechUnchanged':True,'campaignTreesUnchanged':True,'newResearchItems':0,'runtimeVerified':False},indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='All 11 faction repair ships now unlock with their faction repair yard in five standard tech presets, replacing previous science/upgrade prerequisites. No extra research required; full/free-tech and campaigns preserved. Applied to armadaIII; file checks passed, gameplay pending.';p.write_text(json.dumps(s,indent=2))
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n'+datetime.datetime.now().isoformat()+' '+s['current']+'\n')
print(json.dumps({'ships':len(pairs),'standardTrees':5,'entriesChanged':len(changes),'newResearchItems':0}))
