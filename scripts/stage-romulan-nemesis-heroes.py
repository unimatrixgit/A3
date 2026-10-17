from pathlib import Path
import re,json,shutil,wave,audioop,contextlib,io
exec(Path('D:/aramada/scripts/build-bajoran-redesign-v3.py').read_text().split('ROOT=')[0])
r=Path('D:/armadaIII');repo=Path('D:/aramada');src=Path('D:/Xaramada-Modwork/romulan-heroes-extracted');o=Path('D:/Xaramada-Modwork/romulan-heroes-stage');o.mkdir(exist_ok=True)
def put(rel,t):
 p=o/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='latin1')
def copy(p,rel):
 d=o/rel;d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d)
for n in ['rscimitar','rvaldore']:
 copy(src/'ODF/ships'/(n+'.odf'),Path('odf/ships')/(n+'.odf'));copy(src/'SOD'/(n+'.SOD'),Path('SOD')/(n+'.sod'))
for p in(src/'Textures/RGB').glob('*.tga'):copy(p,Path('Textures/RGB')/p.name)
# Never replace global events, GUI, or yard definitions with the pack's versions.
events=(r/'events.dat').read_text(encoding='latin1');source_events=(src/'events.dat').read_text(encoding='latin1');blocks={m[1]:m[2]for m in re.finditer(r'(?ms)^([A-Za-z_][\w]*)[ \t]*\{(.*?)^\}',source_events)};newblocks={k:v for k,v in blocks.items()if k.lower().startswith(('scimitar','valdore'))};clips={}
usedEvents=set()
for n in ['rscimitar','rvaldore']:
 usedEvents.update(re.findall(r'^event\w+\s*=\s*"([^"]+)"',(src/'ODF/ships'/(n+'.odf')).read_text(encoding='latin1'),re.M|re.I))
newblocks={k:'\n'.join(line for line in v.splitlines()if not re.search(r'Sound\s+<(?!romulan>)[^>]+>',line))for k,v in newblocks.items()if k in usedEvents}
for name,body in newblocks.items():
 assert not re.search(r'^'+re.escape(name)+r'\s*\{',events,re.M),name
 for clip in re.findall(r'(?mi)^\s*Sound(?:\s+<[^>]+>)?\s+"([^"]+)"',body):clips[clip]=next((p for p in(src/'Sounds').rglob('*')if p.name.lower()==clip.lower()),None)
for clip,p in clips.items():
 if p is None:
  p=next((p for p in(r/'sounds').rglob('*')if p.name.lower()==clip.lower()),None)
 assert p,clip
 dest=o/'sounds/voiceover/ingame'/('xr2_'+clip.lower());dest.parent.mkdir(parents=True,exist_ok=True)
 with wave.open(str(p))as w:channels=w.getnchannels();width=w.getsampwidth();rate=w.getframerate();raw=w.readframes(w.getnframes())
 if width==1:raw=audioop.bias(raw,1,-128)
 if width!=2:raw=audioop.lin2lin(raw,width,2)
 if channels==2:raw=audioop.tomono(raw,2,.5,.5)
 assert channels in[1,2]
 if rate!=22050:raw,_=audioop.ratecv(raw,2,1,rate,22050,None)
 with wave.open(str(dest),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(22050);w.writeframes(raw)
for name,body in newblocks.items():
 for clip in clips:body=body.replace('"'+clip+'"','"xr2_'+clip.lower()+'"')
 events+='\n'+name+'{'+body+'\n}\n'
put(Path('events.dat'),events)
put(Path('events.dat'),events+'\nScimitarAcknowledge{\nTable\n Sound "xr2_scimitack2.wav"\nSoundPriority 2\n}\n')
for unit,parent,name in [('xhrshinzon','rscimitar','Shinzon - Scimitar'),('xhrdonatra','rvaldore','Donatra - Valdore')]:
 source_text=(src/'ODF/ships'/(parent+'.odf')).read_text(encoding='latin1');fields={k.lower():v.strip()for k,v in re.findall(r'^\s*(\w+)\s*=\s*([^\r\n]*)',source_text,re.M)}
 t=f'#include "rbattle.odf"\nunitName = "{name}"\nlabel = "{name}"\ntooltip = "{name}"\nverboseTooltip = "Romulan Nemesis command hero. Built at the Romulan command shipyard."\nbaseName = "{parent}"\nrace = "romulan"\nisHero = 1\nlatinumCost = 0\nbiomatterCost = 0\nhotkeyLabel = ""\npossibleCraftNames = "'+('IRW Scimitar'if parent=='rscimitar'else'IRW Valdore')+'"\n'
 for key in ['maxHealth','shieldRate','maxSpecialEnergy','specialEnergyRate','dilithiumCost','metalCost','crewCost','officerCost','buildTime','ScaleSOD']:
  if key.lower()in fields:t+=key+' = '+fields[key.lower()]+'\n'
 for i in range(1,9):
  for key in ['weapon'+str(i),'weaponHardpoints'+str(i)]:t+=key+' = '+fields[key.lower()]+'\n'
 prefix='Scimitar'if parent=='rscimitar'else'Valdore'
 for action in ['Select','Acknowledge','Attack','Stop','Move','Repair','RedAlert','YellowAlert','GreenAlert','Transport','SelfDestruct','Decommission','CloakEngage','CloakDisengage']:
  ev=prefix+action
  if action=='Decommission':ev='XV_xhrhero_Decommission'
  elif parent=='rvaldore'and action=='Stop':ev='ValdoreAcknowledge'
  t+=f'event{action} = "{ev}"\n'
 put(Path('odf/ships')/(unit+'.odf'),t)
p=r/'odf/stations/ryard3.odf';t=p.read_text(encoding='latin1');assert not re.search(r'buildItem(?:8|9)\s*=',t,re.I);put(p.relative_to(r),t+'\nbuildItem8 = "xhrshinzon"\nbuildItem9 = "xhrdonatra"\n')
for p in(r/'techtree').glob('*.tt'):
 t=p.read_text(encoding='latin1');m=re.search(r'^xhrhero\.odf[ \t]+([^\r\n]*)',t,re.M|re.I)
 if m:put(p.relative_to(r),t+'\nxhrshinzon.odf '+m[1]+'\nxhrdonatra.odf '+m[1]+'\n')
p=r/'Sprites/gui_global.spr';t=p.read_text(encoding='latin1');t+='\n// Nemesis hero artwork from k_merse pack.\n@reference=64\n@tmaterial=default\n'
for name,tex in [('xhrshinzon','gbrscimitar'),('xhrdonatra','gbrvaldore'),('rscimitar','gbrscimitar'),('rvaldore','gbrvaldore')]:t+=f'b_{name} {tex} 0 0 64 64\n'
t+='@reference=128\n'
for name in ['rscimitar','rvaldore']:
 for k in range(1,6):t+=f'{name}w{k} wf{name} 0 0 128 128\n'
put(p.relative_to(r),t)
# Validate native hardpoints and resolved weapon names prior to any installation.
idx={p.name.lower():p for p in(r/'odf').rglob('*.odf')}
for n in ['rscimitar','rvaldore']:
 with contextlib.redirect_stdout(io.StringIO()):m=IO().read_file(str(o/'SOD'/(n+'.sod')))
 anchors={x['id'].lower()for x in m.nodes};t=(o/'odf/ships'/(n+'.odf')).read_text(encoding='latin1')
 for w in re.findall(r'^weapon\d+\s*=\s*"([^"]+)"',t,re.M|re.I):assert w.lower()+'.odf'in idx,w
 for hptext in re.findall(r'^weaponhardpoints\d+\s*=([^\r\n]+)',t,re.M|re.I):
  for hp in re.findall('"([^"]+)"',hptext):assert hp.lower()in anchors,(n,hp)
report={'stage':str(o),'source':'http://armadafiles.com/files/armada-2/ships/romulan/romulan-scimitar-valdore-hero-ships/details','author':'k_merse','modelCredits':{'Valdore':'Howedar mesh; Redragon textures; Major A Payne conversion','Scimitar':'SFC3/Taldren model; Major A Payne conversion'},'sourceModelsAndODFsUnmodified':True,'sourceAssetsNotRedistributedToGitHub':True,'heroWrappers':['xhrshinzon','xhrdonatra'],'voiceClips':len(clips),'voiceFormat':'PCM16 mono22050','files':[str(p.relative_to(o))for p in o.rglob('*')if p.is_file()and not(p.suffix=='.odf'and p.stem in ['rscimitar','rvaldore'])and not(p.suffix=='.wav'and p.name not in ['xr2_'+n.lower()for n in clips])],'gameplayVerified':False,'installed':False};(repo/'reports/romulan-nemesis-heroes.json').write_text(json.dumps(report,indent=2));print('Staged',len(report['files']),'files; voice clips',len(clips),'native weapons/hardpoints verified.')
