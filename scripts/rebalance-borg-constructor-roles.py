from pathlib import Path
import re,json,datetime,hashlib
repo=Path('D:/aramada');stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup=Path('D:/Xaramada-Modwork/backups')/('borg-constructor-roles-'+stamp);pending=[];records=[]
def vals(t):return {k.lower():v.strip() for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t)}
def put(t,k,v):return re.sub(r'(?mi)^[ \t]*'+k+r'[ \t]*=[^\r\n]*','',t)+'\n'+k+' = '+str(v)+'\n'
def menu(t,items):
 t=re.sub(r'(?mi)^[ \t]*buildItem\d+[ \t]*=[^\r\n]*','',t)
 for i,n in enumerate(items):t+='\nbuildItem'+str(i)+' = "'+n+'"\n'
 assert len(items)<=13 and len(items)==len(set(items));return t
stars=['bbase','fbase','kbase','rbase','cbase','dbase','brbase','bjbase'];overflow=['bhwp','bassturr','bupgrade','btechass','xbharvest','xbassimst','xbomegalab','hub']
for root in [Path('D:/ArmadaLab'),Path('D:/armadaIII')]:
 idx={p.stem.lower():p for p in (root/'odf').rglob('*.odf')}
 for n in stars+overflow:assert n in idx,n
 baseline=vals((root/'odf/ships/bconst.odf').read_text(encoding='latin1'))
 for name,items in [('xbuconst',stars),('uconst',stars),('bconst2',overflow)]:
  rel=Path('odf/ships')/(name+'.odf');t=(root/rel).read_text(encoding='latin1');t=menu(t,items)
  title='Overflow Assembler' if name=='bconst2'else'Universal Assembler'
  for k,v in {'unitName':'"'+title+'"','tooltip':'"'+title+'"','verboseTooltip':'"'+('Borg overflow constructor. Builds advanced defense, research, assimilation, Omega and transwarp facilities.'if name=='bconst2'else'Universal Assembler. Builds the main starbase of every conventional faction.')+'"'}.items():t=put(t,k,v)
  for k in ['dilithiumCost','metalCost','latinumCost','biomatterCost','crewCost','officerCost','buildTime']:t=put(t,k,baseline[k.lower()])
  t=put(t,'maximumCrew',baseline['crewcost']);pending.append((root,rel,t));records.append({'root':str(root),'unit':name,'menu':items,'costs':{k:baseline[k]for k in ['dilithiumcost','metalcost','crewcost','buildtime']}})
 rel=Path('odf/stations/bbase.odf');t=(root/rel).read_text(encoding='latin1');v=vals(t)
 assert any(x=='"bconst2"'for k,x in v.items()if k.startswith('builditem')),'Third constructor missing from Nexus'
 for name in ['tech1','earlytech','fulltech','nosci','nosuper','nospweap']:
  rel=Path('techtree')/(name+'.tt');t=(root/rel).read_text(encoding='latin1');t=re.sub(r'(?mi)^bconst2\.odf[^\r\n]*','',t)+'\nbconst2.odf '+('0'if name=='fulltech'else'1 bbase.odf')+' // Overflow Assembler; available from Nexus\n';pending.append((root,rel,t))
 for f in(root/'AI/AIPs').glob('borg_*.aip'):
  t=f.read_text(encoding='latin1')
  if 'the_build_list'not in t:continue
  lines=[x for x in t.splitlines()if not re.match(r'^\s*"bconst2"\s*,',x)]
  # The overflow constructor must precede the earliest facility moved from Universal.
  anchor=next(i for i,x in enumerate(lines)if re.match(r'^\s*"(?:bupgrade|btechass|xbharvest|xbassimst|xbomegalab|hub|bhwp|bassturr)"\s*,',x))
  lines.insert(anchor,'    "bconst2", 1, 0, -1, 0, // Overflow Assembler before advanced buildings')
  t='\n'.join(lines)+'\n';t=t.replace('Two constructor types','Three constructor types')
  sequence=re.findall(r'(?m)^\s*"([^"]+)"\s*,',t);assert len(sequence)<=200
  for unit in overflow:
   if unit in sequence:assert sequence.index('bconst2')<sequence.index(unit),(f,unit)
  pending.append((root,f.relative_to(root),t))
 # Keep the model's valid existing buttons and validate every menu entry resolves to a sprite.
 sprite=(root/'Sprites/gui_global.spr').read_text(encoding='latin1')
 for unit in stars+overflow+['bconst2','xbuconst']:
  assert re.search(r'(?mi)^b_'+unit+r'\s',sprite),'Missing button '+unit
for root,rel,t in pending:
 f=root/rel;b=backup/root.name/rel;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(f.read_bytes());f.chmod(0o666);data=t.replace('\r','').replace('\n','\r\n').encode('latin1');f.write_bytes(data);assert f.read_bytes()==data
 out=repo/('lab/overlay'if root.name=='ArmadaLab'else'bajor/overlay')/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
(repo/'reports/borg-constructor-roles.json').write_text(json.dumps({'backup':str(backup),'units':records,'files':len(pending),'buttonsValidated':True,'runtimeVerified':False},indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Borg constructor roles applied to armadaIII and ArmadaLab: Standard Assembler unchanged; Universal only 8 faction starbases; third Overflow Assembler builds 8 advanced facilities moved from Universal plus heavy defenses. Third is Nexus-buildable and unlocked with bbase; five AI plans order it before moved facilities. Constructors cost125 dilithium/25 metal, 150 crew/max, 1 officer,17s. Existing matching build buttons validated. Backed up; gameplay pending.';p.write_text(json.dumps(s,indent=2));
with(repo/'build.log').open('a')as log:log.write('\n'+s['current']+'\n')
print(json.dumps({'files':len(pending),'backup':str(backup),'starbases':stars,'overflow':overflow,'buttonsValidated':True}))
