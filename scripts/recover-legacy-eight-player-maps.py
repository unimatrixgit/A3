from pathlib import Path
import json,shutil,datetime,hashlib,subprocess
r=Path('D:/armadaIII');repo=Path('D:/aramada');source=Path('D:/Xaramada-Modwork/eight-player-completion/extracted');assert subprocess.run(['powershell','-NoProfile','-Command','if(Get-Process Armada2 -ErrorAction SilentlyContinue){exit 1}'],capture_output=True).returncode==0,'Game running'
new=[]
aliases={'odf/ships/8472_heromother.odf':'#include "8472_heromothership.odf"\nbaseName = "8472_heromothership"\n','odf/ships/8472_mother.odf':'#include "8472_mothership.odf"\nbaseName = "xvstock_8472_mothership"\n','odf/stations/PB_Cardassia.odf':'#include "PB_CLSSM.odf"\nbaseName = "PB_CLSSM"\nunitName = "Cardassia Prime"\npossibleCraftNames = "Cardassia Prime"\n'}
# Use each installed model explicitly; legacy names must not request nonexistent alias SODs.
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
for rel,t in aliases.items():
 parent='8472_heromothership'if'heromother'in rel else'8472_mothership'if'8472_mother'in rel else'pb_clssm';model=props(parent).get('basename',parent);t=t.replace('baseName = "8472_heromothership"','baseName = "'+model+'"') if'heromother'in rel else t
 assert (r/'SOD'/(model+'.sod')).exists(),model
 p=r/rel;assert not p.exists(),rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='latin1');dest=repo/'overlay'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);new.append({'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
installed=[]
for key,filename in [('alpha-beta-quadrant-map','alphabeta2.bzn'),('alpha-quadrant-v2','alphaquadv2.bzn'),('planet-clusters','Planet Clusters.bzn'),('glenns-warzone','mp08walr.bzn')]:
 src=next((source/key).rglob(filename));destname=filename
 if (r/'bzn'/filename).exists():destname='X8_'+filename
 if(r/'bzn'/destname).exists():continue
 for ext in ['.bzn','.bmp','.txt']:
  p=src.with_suffix(ext)
  if not p.exists():continue
  dst=(r/'bzn'/destname).with_suffix(ext);assert not dst.exists();shutil.copy2(p,dst);new.append({'path':str(dst.relative_to(r)),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
 installed.append({'sourceCatalogue':key,'sourceMap':filename,'installedMap':destname,'originalEnvironmentRetained':True,'runtimeVerified':False})
report={'installedMaps':installed,'addedFiles':new,'existingFilesOverwritten':0,'environmentModelsTexturesChanged':0,'aliases':aliases,'excludedFinal':[{'reason':'Requires Fleet Operations engine','count':4},{'reason':'Map binary has four/seven starts rather than verified eight','count':4}],'note':'Original stock planet appearance retained for Glenn and Cardassia. Text companions may contain obsolete handles; binary map untouched. New files only; remove listed files to roll back.'};(repo/'reports/eight-player-map-legacy-recovery.json').write_text(json.dumps(report,indent=2));print('Installed',len(installed),'additional maps;',len(new),'new files; zero overwrites.')
