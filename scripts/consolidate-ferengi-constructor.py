from pathlib import Path
exec(Path('D:/aramada/scripts/build-mirror-ferengi-research.py').read_text().split('# Existing Cardassian artwork')[0])
import shutil,os,hashlib
pending={};before={n:resolve(n)for n in ['xfgconst','xbgconst','xu3fer2']};(repo/'reports/ferengi-single-constructor-before.json').write_text(json.dumps(before,indent=2))
items=[]
for n in ['xfgconst','xu3fer2']:
 for k,v in sorted(before[n].items(),key=lambda kv:int(kv[0][9:])if re.fullmatch('builditem[0-9]+',kv[0])else-1):
  if re.fullmatch('builditem[0-9]+',k)and v not in items:items.append(v)
assert len(items)==14
for n in before:
 t=text(n);title='Ferengi Temporal Constructor';t=update(t,{'unitName':q(title),'tooltip':q(title),'verboseTooltip':q('Ferengi mercenary subrace constructor. Builds all primary faction starbases, Ferengi yards, Commerce Institute, Mirror Universe yard and researched metal orbitals.'if n!='xbgconst'else'Ferengi mercenary subrace constructor under Borg contract. Paid in dilithium and metal; no latinum research or collector. Retains Transwarp Drive.')})
 if n!='xbgconst':
  t=re.sub(r'(?mi)^\s*buildItem\d+\s*=[^\r\n]*','',t)
  for i,v in enumerate(items):t=put(t,'buildItem'+str(i),q(v))
 pending[index[n].relative_to(root).as_posix()]=t
 for key in ['dilithiumcost','metalcost','latinumcost','crewcost','maximumcrew','maxspecialenergy','specialenergyrate','weapon1','weaponhardpoints1','basename']:
  assert resolve(n).get(key)==before[n].get(key),(n,key)
producers=[]
for n in index:
 d=resolve(n);menu=sorted((int(k[9:]),v)for k,v in d.items()if re.fullmatch('builditem[0-9]+',k))
 if not any(v.lower()=='xu3fer2'for _,v in menu):continue
 result=[]
 for _,v in menu:
  v='xfgconst'if v.lower()=='xu3fer2'else v
  if v not in result:result.append(v)
 t=re.sub(r'(?mi)^\s*buildItem\d+\s*=[^\r\n]*','',text(n))
 for i,v in enumerate(result):t=put(t,'buildItem'+str(i),q(v))
 pending[index[n].relative_to(root).as_posix()]=t;producers.append(n)
for tree in ['tech1','earlytech','fulltech','nosci','nospweap','nosuper']:
 rel='techtree/'+tree+'.tt';t=(root/rel).read_text(encoding='latin1');t=re.sub(r'(?mi)^\s*xu3fer2\.odf\s+[^\r\n]*','',t)+'\nxu3fer2.odf -1\n';pending[rel]=t
ai=[]
for f in(root/'AI/AIPs').glob('*.aip'):
 t=f.read_text(encoding='latin1')
 if not re.search(r'(?m)^\s*"xu3fer2"\s*,',t):continue
 seen=False;out=[]
 for line in t.splitlines():
  if re.match(r'^\s*"(?:xfgconst|xu3fer2)"\s*,',line):
   if seen:continue
   line=line.replace('"xu3fer2"','"xfgconst"');seen=True
  out.append(line)
 pending[f.relative_to(root).as_posix()]='\n'.join(out)+'\n';ai.append(f.name)
backup=Path('D:/Xaramada-Modwork/backups')/('ferengi-single-constructor-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));spritehash=hashlib.sha256((root/'Sprites/gui_global.spr').read_bytes()).hexdigest()
for rel in pending:
 for label,base in [('live',root),('repository',repo/'bajor/overlay')]:
  f=base/rel;b=backup/label/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,b)
for rel,t in pending.items():
 data=t.replace('\r','').replace('\n','\r\n').encode('latin1')
 for base in [root,repo/'bajor/overlay']:
  f=base/rel;os.chmod(f,0o666);f.write_bytes(data);assert f.read_bytes()==data
assert hashlib.sha256((root/'Sprites/gui_global.spr').read_bytes()).hexdigest()==spritehash
pp=repo/'reports/constructor-tier-plan.json';p=json.loads(pp.read_text());g=next(x for x in p['factions']if x['faction']=='ferengi');g['proposed']=[{'tier':3,'constructor':'xfgconst','buildings':items,'existing':True}];g['oldConstructors']=['xfgconst','xu3fer2'];g['subrace']=True;next(x for x in p['factions']if x['faction']=='borg_ferengi')['subrace']=True;pp.write_text(json.dumps(p,indent=2))
r={'appliedAt':datetime.datetime.now().astimezone().isoformat(),'backup':str(backup),'files':list(pending),'name':'Ferengi Temporal Constructor','buildings':items,'borgPricedVariant':'xbgconst (one option in Borg catalog)','removedProductionOption':'xu3fer2','aiPlans':ai,'iconsUnchanged':True,'runtimeVerified':False};(repo/'reports/ferengi-single-constructor.json').write_text(json.dumps(r,indent=2))
s=repo/'status.json';d=json.loads(s.read_text());d['current']='Constructor names updated to Basic / Advanced / Temporal. Breen have one native constructor with10 options. Ferengi are a mercenary subrace with one Temporal Constructor per catalog,14 normal construction options; Borg contracts keep their own pricing and transwarp. Extra constructor options removed from production, technology and AI. Icons unchanged; gameplay test pending.';d['updated']=r['appliedAt'];s.write_text(json.dumps(d,indent=2))
with(repo/'build.log').open('a')as f:f.write('\n['+r['appliedAt']+'] '+d['current']+' Backup:'+str(backup)+'\n')
print('Applied one Ferengi constructor per catalog;',len(items),'normal menu options;',len(ai),'AI plans updated; icons unchanged.')
