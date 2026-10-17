from pathlib import Path
import re,json,hashlib
root=Path('D:/armadaIII');stage=Path('D:/Xaramada-Modwork/non-bajor-ai-target-fix');files=[];changes=[]
for faction,old,new in [('borg','bomega','bomega1'),('romulan','rdestr1','rdestroy')]:
 for suffix in ['build_list','instant_action_build_list','offensive_list','defensive_list','endgame_list']:
  p=root/'AI/AIPs'/(faction+'_'+suffix+'.aip');s=p.read_text(encoding='latin1');t,n=re.subn(r'(?m)(^[ \t]*)"'+old+r'"(?=[ \t]*,)',r'\1"'+new+'"',s);assert n==1,(p,n)
  rel=p.relative_to(root).as_posix();o=stage/rel;o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));files.append({'path':rel,'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sha256':hashlib.sha256(o.read_bytes()).hexdigest()});changes.append({'profile':p.name,'from':old,'to':new})
r={'target':str(root),'stage':str(stage),'files':files,'changes':changes,'applied':False,'runtimeVerified':False,'bajorUntouched':True};Path('D:/aramada/reports/non-bajor-ai-target-fix.json').write_text(json.dumps(r,indent=2));print('Staged ten non-Bajor AI profiles; no live changes')
