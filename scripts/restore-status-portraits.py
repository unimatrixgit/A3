from pathlib import Path
import json,hashlib,datetime,shutil,os,subprocess
repo=Path('D:/aramada');root=Path('D:/armadaIII');p=repo/'reports/queue-category-icons.json';r=json.loads(p.read_text());assert not r.get('queuePortraitsRolledBack'),'Already recovered';assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running'
prior=Path(r['backup']);backup=Path('D:/Xaramada-Modwork/backups')/('restore-status-portraits-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));rel='Sprites/gui_global.spr'
for label,base in [('live',root),('repository',repo/'bajor/overlay')]:
 dst=base/rel;src=prior/label/rel;assert src.exists();b=backup/label/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,b);os.chmod(dst,0o666);shutil.copy2(src,dst);assert dst.read_bytes()==src.read_bytes()
removed=[]
for rel in r['files']:
 if not rel.startswith('Textures/RGB/xqicons'):continue
 for label,base in [('live',root),('repository',repo/'bajor/overlay')]:
  dst=base/rel;assert dst.resolve().is_relative_to(base.resolve()),dst
  if dst.exists():
   b=backup/label/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,b);os.chmod(dst,0o666);dst.unlink()
 removed.append(rel)
# Icon atlases retain category gradients and HWP highlighting; no text or ODF changes.
for x in r['manifest']:
 if x['file'].startswith('Textures/RGB/xuiatlas'):assert hashlib.sha256((root/x['file']).read_bytes()).hexdigest()==x['sha256']
r['queuePortraitsRolledBack']=True;r['queueRollbackAt']=datetime.datetime.now().astimezone().isoformat();r['queueRollbackBackup']=str(backup);r['queueRollbackReason']='User screenshot shows blank/corrupt ship status portrait after shared wireframe update';r['categoryGradientsAndHWPBadgesRetained']=True;r['runtimeVerified']=False;p.write_text(json.dumps(r,indent=2))
sfile=repo/'status.json';s=json.loads(sfile.read_text(encoding='utf-8-sig'));s['current']='RECOVERY APPLIED: restored original shared ship status/production-queue sprite mappings after blank portrait report. Removed36 new queue atlases. Category gradients and7 prominent HWP build badges retained. Names, tooltips and gameplay untouched. In-game portrait retest pending; queue redesign withdrawn.';s['updated']=r['queueRollbackAt'];sfile.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n['+s['updated']+'] '+s['current']+' Backup:'+str(backup)+'\n')
paths=['bajor/overlay/Sprites/gui_global.spr']+['bajor/overlay/'+f for f in removed]+['reports/queue-category-icons.json','scripts/restore-status-portraits.py']
subprocess.run(['git','-C',str(repo),'add','-A','--',*paths],check=True);subprocess.run(['git','-C',str(repo),'-c','gc.auto=0','commit','-q','-m','Restore status portraits while retaining category and HWP build artwork'],check=True);subprocess.run(['git','-C',str(repo),'push','origin','main'],check=True)
print(json.dumps({'restoredSharedPortraitMappings':True,'categoryGradientsRetained':True,'HWPBadgesRetained':True,'removedQueueAtlases':len(removed),'commit':subprocess.check_output(['git','-C',str(repo),'log','-1','--format=%h'],text=True).strip()}))
