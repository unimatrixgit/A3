"""Use only existing research for existing special-weapon variants; no new ODFs."""
from pathlib import Path
from functools import lru_cache
import datetime,hashlib,json,re,shutil,subprocess

root=Path('D:/armadaIII');repo=Path('D:/aramada')
assert subprocess.check_output(['C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe','-NoProfile','-Command','@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'],text=True).strip()=='0'
idx={p.stem.lower():p for p in(root/'odf').rglob('*.odf')}
@lru_cache(None)
def props(name,seen=()):
    name=Path(name).stem.lower()
    assert name not in seen
    if name not in idx:return {}
    values={};content=idx[name].read_text(encoding='latin1')
    for inc in re.findall(r'(?mi)^[ \t]*#include\s+"([^\"]+)"',content):values.update(props(inc,seen+(name,)))
    for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',content):values[k.lower()]=v.split('//')[0].strip().strip('"')
    return values
def tree(name,seen=()):
    assert name not in seen
    result={}
    for line in(root/'techtree'/name).read_text(encoding='latin1').splitlines():
        line=line.split('//')[0].strip()
        if line.startswith('#include'):
            result.update(tree(line.split(None,1)[1].strip('"'),seen+(name,)));continue
        x=line.split()
        if len(x)>1 and x[0].lower().endswith('.odf'):result[Path(x[0]).stem.lower()]=x[1:]
    return result
normal=tree('tech1.tt')
def pods(weapon):
    return [Path(x).stem.lower()for x in normal.get(weapon,['0'])[1:]if props(x).get('classlabel')in {'pod','researchpod'}]
def signature(weapon):
    p=props(weapon)
    return tuple(p.get(k,'').lower()for k in ['classlabel','wpnname','ordname','detectclass'])
canonical={w for w,gate in normal.items()if int(gate[0])>0 and pods(w)and props(w).get('special')=='1'}
users={}
for name,path in idx.items():
    if path.parent.name.lower()!='ships':continue
    p=props(name)
    if not p.get('race'):continue
    for key,weapon in p.items():
        if re.fullmatch(r'weapon\d+',key)and props(weapon).get('special')=='1':users.setdefault(weapon.lower(),set()).add(p['race'])
aliases={}
for weapon,races in users.items():
    if weapon in canonical:continue
    choices=[candidate for candidate in canonical if signature(candidate)==signature(weapon)
        and all(any(props(pod).get('race')==race for pod in pods(candidate))for race in races)]
    if choices:
        choices.sort(key=lambda n:(n.startswith(('ya','xy_','xbj_')),len(n),n))
        aliases[weapon]=choices[0]

backup=Path('D:/Xaramada-Modwork/backups')/('existing-ability-research-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
changes=[];mode_trees={name:tree(name+'.tt')for name in ['tech1','earlytech','nosci','nosuper','nospweap']}
for mode,entries in mode_trees.items():
    relative=Path('techtree')/(mode+'.tt');path=root/relative;content=path.read_text(encoding='latin1');before=content
    mappings={w:w for w in canonical}|aliases
    for weapon,original in sorted(mappings.items()):
        current=entries.get(weapon,['0']);native=entries.get(original,normal[original])
        if int(current[0])<0:continue
        if mode=='nospweap'and weapon==original:continue
        if int(native[0])<0:desired=['-1']
        elif int(current[0])>0:continue
        else:desired=normal[original]
        if current==desired:continue
        pattern=r'(?mi)^'+re.escape(weapon)+r'\.odf[ \t]+[^\r\n]*'
        line=weapon+'.odf '+' '.join(desired)+' // Existing ability research; same requirement as '+original
        if re.search(pattern,content):content=re.sub(pattern,line,content)
        else:content=content.rstrip()+'\n'+line+'\n'
        changes.append({'tree':mode,'weapon':weapon,'canonical':original,'before':current,'after':desired})
    if content!=before:
        saved=backup/relative;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,saved)
        data=content.replace('\r','').replace('\n','\r\n').encode('latin1');path.write_bytes(data)
        out=repo/'bajor/overlay'/relative;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)

# Validate only existing research was reused; no new unit/weapon definitions.
assert not list((root/'odf').rglob('z21*.odf'))
assert tree('tech1.tt')['gplasmabank']==['1','carpod1.odf']
for row in changes:
    actual=tree(row['tree']+'.tt')[row['weapon']];assert actual==row['after']
    if int(actual[0])>0:
        assert actual==normal[row['canonical']]
        assert all(Path(x).stem.lower()in idx for x in actual[1:])
report={'target':str(root),'newResearchItems':0,'newOdfFiles':0,'newWeaponAliases':0,
 'existingAbilityVariantsCorrected':len(aliases),'changes':changes,'backup':str(backup),
 'plasmaBank':'Existing gplasmabank -> carpod1 retained; no new research item',
 'scope':'Only variants of already researchable abilities, matched by native class/name/ordnance/detection mode and existing faction research. Previously innate abilities without such a match remain innate. Full/free-tech presets unchanged.',
 'runtimeVerified':False,'issues':[]}
(repo/'reports/existing-ability-research-fix-20261021.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'existingAbilityVariants':len(aliases),'technologyEntriesCorrected':len(changes),'newResearchItems':0,'newOdfFiles':0,'plasmaBank':'carpod1','backup':str(backup)}))
