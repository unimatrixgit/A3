from pathlib import Path
import re,json,hashlib
root=Path('D:/armadaIII');stage=Path('D:/Xaramada-Modwork/bajor-hero-scale-tractor');files=[]
def save(rel,t):
 p=root/rel;o=stage/rel;o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));files.append({'path':rel,'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sha256':hashlib.sha256(o.read_bytes()).hexdigest()})
def setprop(t,k,v):
 pat=r'(?mi)^'+re.escape(k)+r'[ \t]*=[^\r\n]*'
 return re.sub(pat,k+' = '+v,t)if re.search(pat,t)else t+'\n'+k+' = '+v+'\n'
for rel,scale in [('odf/ships/bjcolony.odf',.6),('odf/ships/bjconst.odf',.8),('odf/ships/xbjuconst.odf',.65),('odf/stations/bjsensor.odf',.36)]:
 t=(root/rel).read_text();t=setprop(t,'ScaleSOD',str(scale))
 if 'xbjuconst'in rel:t=t.replace('"xbj_gtracbm"','"gtracbm"')
 save(rel,t)
# Use native hero combat definition and Bajoran battleship art/hardpoints.
old=(root/'odf/ships/bjnerys.odf').read_text();battle=(root/'odf/ships/bjbattle.odf').read_text();t=(root/'odf/ships/fente.odf').read_text()
for k,v in [('race','"bajoran"'),('unitName','"Colonel Kira Nerys - Bajoran Command Battleship"'),('tooltip','"Colonel Kira Nerys - Bajoran Command Battleship"'),('verboseTooltip','"Kira Nerys commands a Bajoran hero battleship with Enterprise-E-equivalent combat specifications."'),('possibleCraftNames','"Colonel Kira Nerys"'),('baseName','"br3_bjbattle"')]:t=setprop(t,k,v)
for m in re.finditer(r'(?mi)^(\w+)[ \t]*=[ \t]*([^\r\n]*)',battle):
 k,v=m.groups()
 if 'hardpoint'in k.lower()or k.lower()=='scalesod':t=setprop(t,k,v)
for m in re.finditer(r'(?mi)^(event\w+)[ \t]*=[ \t]*([^\r\n]*)',old):t=setprop(t,*m.groups())
save('odf/ships/bjnerys.odf',t)
# GUI resolves by unit or shared battleship model; match Kira unit aliases to battleship icons.
s=(root/'Sprites/gui_global.spr').read_text()
for suffix in ['']+['w'+str(i)for i in range(1,6)]:
 target='b_bjnerys'if not suffix else'bjnerys'+suffix;source='b_bjbattle'if not suffix else'bjbattle'+suffix
 m=re.search(r'(?m)^'+source+r'([ \t]+[^\r\n]+)',s);assert m
 s=re.sub(r'(?m)^'+target+r'[ \t]+[^\r\n]+',target+m.group(1),s)
save('Sprites/gui_global.spr',s)
report={'stage':str(stage),'files':files,'applied':False,'runtimeVerified':False,'changes':['Universal tractor beam uses direct native reference.','Colony scale 0.096 to 0.6; builders 1.6 to 0.8 and 1.0 to 0.65; sensor 0.11968 to 0.36.','Kira uses Enterprise-E hero definition with Bajoran battleship model/hardpoints and existing Kira voice events.']}
Path('D:/aramada/reports/bajoran-hero-scale-tractor.json').write_text(json.dumps(report,indent=2));print('Staged',len(files),'files')
