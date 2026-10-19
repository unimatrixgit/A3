from pathlib import Path
import re,json,datetime
repo=Path('D:/aramada');stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup=Path('D:/Xaramada-Modwork/backups')/('bajoran-cyclone-'+stamp);pending=[]
def put(t,k,v):return re.sub(r'(?mi)^[ \t]*'+k+r'[ \t]*=[^\r\n]*','',t)+'\n'+k+' = '+v+'\n'
for root in [Path('D:/ArmadaLab'),Path('D:/armadaIII')]:
 t=(root/'odf/stations/fhwp.odf').read_text(encoding='latin1')
 for k,v in {'unitName':'"Bajoran Cyclone Defense Station"','tooltip':'"Bajoran Cyclone Defense Station"','verboseTooltip':'"Bajoran heavy defense platform. Three beam banks, two torpedo banks and one rapid-fire torpedo launcher."','race':'"bajoran"','baseName':'"fhwp"'}.items():t=put(t,k,v)
 assert (root/'SOD/fhwp.sod').exists()
 pending.append((root,Path('odf/stations/bjhwp.odf'),t))
 rel=Path('odf/ships/bjconst.odf');c=(root/rel).read_text(encoding='latin1');slots={int(n):v.strip('" ')for n,v in re.findall(r'(?mi)^[ \t]*buildItem(\d+)[ \t]*=[ \t]*([^\r\n]+)',c)}
 slot=next(i for i in range(13)if i not in slots) if 'bjhwp' not in slots.values() else next(i for i,v in slots.items()if v=='bjhwp')
 if slot not in slots:c+='\nbuildItem'+str(slot)+' = "bjhwp"\n'
 assert slot==12
 pending.append((root,rel,c))
 for name in ['tech1','earlytech','fulltech','nosci','nosuper','nospweap']:
  rel=Path('techtree')/(name+'.tt');c=(root/rel).read_text(encoding='latin1');c=re.sub(r'(?mi)^bjhwp\.odf[^\r\n]*','',c)+'\nbjhwp.odf 0 // Bajoran Cyclone: unlocked\n';pending.append((root,rel,c))
 rel=Path('Sprites/gui_global.spr');c=(root/rel).read_text(encoding='latin1')
 for original,alias in [('b_fhwp','b_bjhwp')]+[('fhwpw'+str(i),'bjhwpw'+str(i))for i in range(1,6)]:
  m=re.search(r'(?mi)^'+original+r'[ \t]+[^\r\n]*',c);assert m,original
  if not re.search(r'(?mi)^'+alias+r'[ \t]',c):c=c[:m.end()]+'\n'+re.sub('^'+original,alias,m[0])+c[m.end():]
 pending.append((root,rel,c))
for root,rel,t in pending:
 f=root/rel
 if f.exists():
  b=backup/root.name/rel;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(f.read_bytes());f.chmod(0o666)
 data=t.replace('\r','').replace('\n','\r\n').encode('latin1');f.write_bytes(data)
 out=repo/('lab/overlay'if root.name=='ArmadaLab'else'bajor/overlay')/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);assert f.read_bytes()==data
(repo/'reports/bajoran-cyclone.json').write_text(json.dumps({'backup':str(backup),'unit':'bjhwp','constructor':'bjconst','slot':12,'clonedFrom':'fhwp','runtimeVerified':False},indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Bajoran Cyclone installed in armadaIII and ArmadaLab: exact Federation fhwp stats/loadout/model, Bajoran faction, bjconst slot12, unlocked in all six skirmish tech trees, build button and five wireframes mapped to existing Cyclone artwork. Backed up and file-verified; gameplay pending.';p.write_text(json.dumps(s,indent=2));
with(repo/'build.log').open('a')as log:log.write('\n'+s['current']+'\n')
print(s['current'])
