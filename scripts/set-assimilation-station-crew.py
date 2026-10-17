from pathlib import Path
import re,shutil,datetime,json
r=Path('D:/armadaIII');repo=Path('D:/aramada');rel=Path('odf/stations/xbassimst.odf');p=r/rel;t=p.read_text(encoding='latin1');b=Path('D:/Xaramada-Modwork/backups')/('assimilation-crew-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))/rel;b.parent.mkdir(parents=True);shutil.copy2(p,b)
for k,v in [('crewCost',200),('maximumCrew',1000)]:
 t,n=re.subn(r'^\s*'+k+r'\s*=.*$',k+' = '+str(v),t,flags=re.M|re.I);assert n==1,(k,n)
p.write_text(t,encoding='latin1');shutil.copy2(p,repo/'overlay'/rel);assert re.search(r'^crewCost = 200$',p.read_text(),re.M);assert re.search(r'^maximumCrew = 1000$',p.read_text(),re.M)
report={'unit':'xbassimst','startingCrew':200,'maximumCrew':1000,'installed':True,'backup':str(b),'gameplayVerified':False};(repo/'reports/assimilation-station-crew.json').write_text(json.dumps(report,indent=2));f=repo/'status.json';s=json.loads(f.read_text(encoding='utf-8-sig'));s['current']='Installed Assimilation Station crew adjustment: starts with 200 crew, maximum capacity 1000. One station file backed up and verified; fresh-game test pending.';f.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a')as log:log.write('\nAssimilation Station updated: crewCost 200, maximumCrew 1000; backed up and verified.\n')
print('Installed: starting crew 200, capacity 1000.')
