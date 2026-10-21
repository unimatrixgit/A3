"""Independent semantic checks for the staged/installed armadaIII-only patch."""
from pathlib import Path
from functools import lru_cache
import hashlib,json,re,sys

root=Path('D:/armadaIII');repo=Path('D:/aramada');package=repo/'patches/20261021-ship-research-balance'
report=json.loads((package/'manifest.json').read_text());installed='--installed'in sys.argv
idx={p.stem.lower():p.relative_to(root).as_posix()for p in(root/'odf').rglob('*.odf')}
for p in(package/'overlay/odf').rglob('*.odf'):idx[p.stem.lower()]=p.relative_to(package/'overlay').as_posix()
def read(relative):
    staged=package/'overlay'/relative
    return ((root/relative)if installed or not staged.exists()else staged).read_text(encoding='latin1')
@lru_cache(None)
def props(name,trail=()):
    name=Path(name).stem.lower()
    assert name not in trail,('include cycle',trail,name)
    if name not in idx:return {}
    content=read(idx[name]);values={}
    for inc in re.findall(r'(?mi)^[ \t]*#include\s+"([^\"]+)"',content):values.update(props(inc,trail+(name,)))
    for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',content):values[k.lower()]=v.split('//')[0].strip()
    return values
def unquote(value):return value.strip('"')
def tree(name,trail=()):
    assert name not in trail
    entries={}
    for line in read('techtree/'+name).splitlines():
        line=line.split('//')[0].strip()
        if line.startswith('#include'):
            entries.update(tree(line.split(None,1)[1].strip('"'),trail+(name,)));continue
        a=line.split()
        if len(a)>1 and a[0].lower().endswith('.odf'):
            count=int(a[1]);assert count<0 or count==len(a)-2,(name,line)
            entries[Path(a[0]).stem.lower()]=(count,[Path(x).stem.lower()for x in a[2:]])
    return entries
normal=tree('tech1.tt');all_tech={name:tree(name+'.tt')for name in ['tech1','earlytech','nosci','nosuper','nospweap','fulltech','freetech']}
producers={}
for name in idx:
    for k,v in props(name).items():
        if re.fullmatch(r'(?:secondary)?builditem\d+',k):producers.setdefault(unquote(v).lower(),[]).append(name)
def research_gate(weapon,race):
    queue=list(normal.get(weapon,(0,[]))[1]);seen=set();found=False
    while queue:
        item=queue.pop()
        if item in seen:continue
        seen.add(item);p=props(item)
        if unquote(p.get('classlabel','')).lower()in {'pod','researchpod'}:
            assert unquote(p.get('race','')).lower()==race,(weapon,race,item,'wrong faction')
            assert producers.get(item),(item,'missing producer')
            found=True
        queue.extend(normal.get(item,(0,[]))[1])
    return found
utility={a['weapon']for a in report['specialSlotAudit']if a['status']=='basic utility retained'}
checked=0
for ship in {a['ship']for a in report['specialSlotAudit']}:
    values=props(ship);race=unquote(values['race']).lower()
    for k,w in values.items():
        if not re.fullmatch(r'weapon\d+',k):continue
        weapon=unquote(w).lower();a=props(weapon)
        if unquote(a.get('special','0')).rstrip('fF')!='1'or weapon in utility:continue
        if normal.get(weapon,(0,[]))[0]<0:continue
        assert research_gate(weapon,race),(ship,weapon,'no own research')
        checked+=1
        for name in ['earlytech','nosci','nosuper']:
            assert all_tech[name].get(weapon,(0,[]))[0]!=0,(name,weapon,'unlocked')
for alias in report['weaponAliases']:
    assert props(alias['original'])==props(alias['alias']),(alias,'weapon behavior changed')
    p=props(alias['alias'])
    if unquote(p.get('classlabel','')).lower()!='detectcloak'or unquote(p.get('buttonslot',''))!='0':
        assert re.search(r'(?mi)^b_'+alias['alias']+r'\s',read('Sprites/gui_global.spr'))
for race,r in report['research'].items():
    facility=props(r['facility']);pod=props(r['pod']);assert unquote(pod['race'])==race
    items=[k for k in facility if re.fullmatch(r'builditem\d+',k)]
    hardpoints=re.findall(r'[A-Za-z_]+\d+',unquote(facility['podhardpoints']))
    assert len(items)==len(hardpoints)<=13
    model=unquote(pod['basename']);assert (root/'SOD'/(model+'.sod')).exists(),model
    assert re.search(r'(?mi)^b_'+r['pod']+r'\s',read('Sprites/gui_global.spr'))
    assert all_tech['fulltech'][r['pod']][0]==0
    assert all_tech['freetech'][r['pod']][0]==0
for row in report['prices']:
    p=props(row['ship'])
    for k,value in row['after'].items():assert float(unquote(p[k]).rstrip('fF'))==value
    assert float(unquote(p['crewcost']))==row['newCrewCost']
    assert sum(row['after'].values())>0
    if 'maximumcrew'in p:assert row['newCrewCost']<=float(unquote(p['maximumcrew']))
    if row['race']=='species8472':assert row['newCrewCost']==0 and row['after']['dilithiumcost']==row['after']['metalcost']==0
for row in report['platforms']:
    p=props(row['unit']);assert float(p['crewcost'])==float(p['maximumcrew'])==0
    assert float(p['officercost'])==2*row['oldOfficers']
for row in report['files']:
    path=(root if installed else package/'overlay')/row['file']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==row['afterSha256'],row['file']
for name in report['aiProfilesUpdated']:
    content=read('AI/AIPs/'+name)
    assert len(re.findall(r'(?m)^\s*"[^\"]+"\s*,\s*-?\d+\s*,',content))<=200,(name,'AI list overflow')
cube=props('bbattle1');assert float(cube['dilithiumcost'])==550 and float(cube['metalcost'])==150
result={'target':str(root),'installedFilesChecked':installed,'files':len(report['files']),
        'specialWeaponSlotsWithFactionResearch':checked,'researchPods':len(report['research']),
        'shipsPriced':len(report['prices']),'heavyPlatforms':7,'issues':[],'runtimeVerified':False}
(package/('installed-validation.json'if installed else'staged-validation.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result))
