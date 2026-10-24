from pathlib import Path
exec(Path('D:/aramada/scripts/build-mirror-ferengi-research.py').read_text().split('# Existing Cardassian artwork')[0])
import shutil,os,hashlib
props=json.loads((repo/'reports/constructor-rename-before.json').read_text());r=json.loads((repo/'reports/constructor-mirror-patch.json').read_text());pending={};rows=[];tiers={c['unit']:(c['tier'],c['race'])for c in r['constructors']}
for n,target in r['legacyAliases'].items():tiers[n]=tiers[target]
names={'federation':'Federation','borg':'Borg','klingon':'Klingon','romulan':'Romulan','cardassian':'Cardassian','dominion':'Dominion','breen':'Breen','bajoran':'Bajoran','species8472':'Species 8472','ferengi':'Ferengi','borg_ferengi':'Borg Ferengi'}
breen=['brbase','bryard','brmining','brorbital','brresear','brresear2','bryard2','bryard3','mrybreen','xfgmerc'];breenbuilders={'brconst','xbrconst2','xbruconst'}
for n,(level,race)in tiers.items():
 if race=='breen':level=1
 title=names[race]+' '+{1:'Basic Constructor',2:'Advanced Constructor',3:'Temporal Constructor'}[level]
 if n.startswith('xu3'):title+=' (Specialist)'
 d=props[n];desc=d.get('verbosetooltip','');desc=re.sub(r'^Tier [123]:\s*','',desc,flags=re.I);desc=title+'. '+desc
 if race=='breen':desc=title+'. Builds all Breen mining, research and shipyard facilities, the Breen starbase, Mirror Universe yard and Ferengi Contract Yard. Ferengi constructors offer other factions\' starbases.'
 t=update(text(n),{'unitName':q(title),'tooltip':q(title),'verboseTooltip':q(desc)})
 if race=='breen':
  t=re.sub(r'(?mi)^\s*buildItem\d+\s*=[^\r\n]*','',t)
  for i,unit in enumerate(breen):t=put(t,'buildItem'+str(i),q(unit))
 rel=Path(d['file']).relative_to(root).as_posix();pending[rel]=t;rd=resolve(n)
 for k,v in d.items():
  if k in ['unitname','tooltip','verbosetooltip','file']or(race=='breen'and re.fullmatch('builditem[0-9]+',k)):continue
  assert rd.get(k)==v,(n,k)
 rows.append({'unit':n,'name':title,'tier':level,'race':race})
# Only one native Breen constructor option in every production menu.
producers=[]
for n in index:
 d=resolve(n);items=sorted((int(k[9:]),v)for k,v in d.items()if re.fullmatch('builditem[0-9]+',k))
 if not any(v.lower()in breenbuilders for _,v in items):continue
 result=[]
 for _,v in items:
  v='brconst'if v.lower()in breenbuilders else v
  if v not in result:result.append(v)
 t=re.sub(r'(?mi)^\s*buildItem\d+\s*=[^\r\n]*','',text(n))
 for i,v in enumerate(result):t=put(t,'buildItem'+str(i),q(v))
 rel=index[n].relative_to(root).as_posix();pending[rel]=t;producers.append(n)
for tree in ['tech1','earlytech','fulltech','nosci','nospweap','nosuper']:
 rel='techtree/'+tree+'.tt';t=(root/rel).read_text(encoding='latin1')
 for n in breenbuilders:t=re.sub(r'(?mi)^\s*'+n+r'\.odf\s+[^\r\n]*','',t)
 t+='\nbrconst.odf 0\nxbrconst2.odf -1\nxbruconst.odf -1\n';pending[rel]=t
ai=[]
for f in(root/'AI/AIPs').glob('*.aip'):
 t=f.read_text(encoding='latin1')
 if not re.search(r'(?m)^\s*"(?:xbrconst2|xbruconst)"\s*,',t):continue
 out=[];seen=False
 for line in t.splitlines():
  if re.match(r'^\s*"(?:brconst|xbrconst2|xbruconst)"\s*,',line):
   if seen:continue
   line=re.sub(r'"(?:xbrconst2|xbruconst)"','"brconst"',line);seen=True
  out.append(line)
 pending[f.relative_to(root).as_posix()]='\n'.join(out)+'\n';ai.append(f.name)
# Model and sprite files are deliberately outside this manifest.
assert not any(rel.lower().startswith(('sod/','textures/','sprites/'))for rel in pending)
spritehash=hashlib.sha256((root/'Sprites/gui_global.spr').read_bytes()).hexdigest()
backup=Path('D:/Xaramada-Modwork/backups')/('constructor-names-breen-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
for rel in pending:
 for label,base in [('live',root),('repository',repo/'bajor/overlay')]:
  dst=base/rel
  if dst.exists():b=backup/label/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,b)
for rel,t in pending.items():
 data=t.replace('\r','').replace('\n','\r\n').encode('latin1')
 for base in [root,repo/'bajor/overlay']:
  dst=base/rel;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():os.chmod(dst,0o666)
  dst.write_bytes(data);assert dst.read_bytes()==data
assert hashlib.sha256((root/'Sprites/gui_global.spr').read_bytes()).hexdigest()==spritehash
result={'appliedAt':datetime.datetime.now().astimezone().isoformat(),'backup':str(backup),'constructors':rows,'files':list(pending),'breenBuildings':breen,'productionMenus':producers,'aiPlans':ai,'iconsUnchanged':True,'transwarpEnergyMenusAndStatsPreservedExceptBreenConsolidation':True,'runtimeVerified':False}
(repo/'reports/constructor-names-breen.json').write_text(json.dumps(result,indent=2))
# Keep the approved plan consistent with the Breen exception for future builders.
pp=repo/'reports/constructor-tier-plan.json';plan=json.loads(pp.read_text());g=next(g for g in plan['factions']if g['faction']=='breen');g['proposed']=[{'tier':1,'constructor':'brconst','buildings':breen,'existing':True}];g['oldConstructors']=sorted(breenbuilders);g['foreignStarbasesVia']='Ferengi Temporal Constructor';pp.write_text(json.dumps(plan,indent=2))
s=repo/'status.json';d=json.loads(s.read_text());d['current']='Renamed constructor tiers to [Race] Basic / Advanced / Temporal Constructor. Existing icons untouched. Breen now offer one native Basic Constructor with10 options; redundant Breen production/tech options removed and AI adjusted. Borg transwarp and special energy preserved. File checks passed; in-game display not tested.';d['updated']=result['appliedAt'];s.write_text(json.dumps(d,indent=2))
with(repo/'build.log').open('a')as log:log.write('\n['+d['updated']+'] '+d['current']+' Backup:'+str(backup)+'\n')
print('Renamed',len(rows),'constructors; single Breen menu:',len(breen),'items;',len(ai),'AI plans adjusted; icons unchanged.')
