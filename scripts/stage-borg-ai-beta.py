from pathlib import Path
import re,json
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
stage=Path('D:/Xaramada-Modwork/borg-ai-beta');tt={}
for line in(root/'techtree/tech1.tt').read_text(encoding='latin1').splitlines():
 a=line.split('//')[0].split()
 if len(a)>1 and a[0].endswith('.odf'):tt[a[0].lower()]=[x.lower()for x in a[2:2+max(int(a[1]),0)]]
order=[('bbase',1),('bconst',2),('bbase2',1),('bmining',1),('bfreight',2),('byard',1),('bdestroy',3),('bsensor',1),('bturret',2),('bresear',1),('bcruise1',2),('bcolony',1),('bresear2',1),('xbuconst',1),('bupgrade',1),('byard2',1),('bfreight',3),('bturret2',2),('bcruise2',2),('bbattle1',2),('brecycle',1),('btechass',1),('xbharvest',1),('xbassimst',1),('xbrepair',1),('borpod11',1),('borpod12',1),('borpod13',1),('borpod14',1),('borpod15',1),('borpod21',1),('borpod22',1),('borpod23',1),('borpod24',1),('borpod25',1),('bbattle2',2),('bspecial',1),('borpod5',1),('borpod4',1),('borpod3',1),('borpod1',1),('borpod2',1),('borpod6',1),('borpod7',1),('borpod8',1),('borpod9',1),('bsuperbl',1),('byard3',1),('blocutus',1),('bomega1',1),('xbomegalab',1),('xbomegapod',1),('xobbattle1',1),('bdestroy2',5),('bbattle1',4),('bbattle2',4)]
avail={v.lower().removesuffix('.odf')+'.odf'for k,v in props('borg').items()if re.fullmatch('standardunits[0-9]+',k)};issues=[]
for i,(name,count)in enumerate(order):
 n=name+'.odf'
 if n in avail:continue
 missing=[x for x in tt.get(n,[])if x not in avail];producers=[x for x in avail if any(v.lower().removesuffix('.odf')+'.odf'==n for k,v in props(x).items()if re.fullmatch(r'(?:secondary)?builditem\d+',k))]
 if n not in tt or missing or not producers:issues.append(dict(row=i,unit=n,missing=missing,producer=producers))
 avail.add(n)
assert not issues,issues
files=[]
for p in(root/'AI/AIPs').glob('borg_*list.aip'):
 t='// Borg economy-first beta build order. Two constructor types; native technology checks.\n#include "aipdef.h"\nint checkTechnologyAvailable = 1;\nWay_Better_Build_List_Element the_build_list[MAX_ELEMENTS] =\n{\n'
 t+='\n'.join(f'    "{n}", {c}, 0, -1, 0,' for n,c in order)+'\n};\n'
 dst=stage/p.relative_to(root);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(t,encoding='latin1');files.append(str(p.relative_to(root)))
(repo/'reports/borg-ai-beta.json').write_text(json.dumps(dict(stage=str(stage),files=files,rowsPerProfile=len(order),profiles=len(files),issues=issues,gameplayVerified=False,notes=['Metal orbital before research spending.','Both research nodes and upgrade facility precede advanced ships.','Removed unreachable legacy assimilation turret from AI only.','Only Borg Assembler and faction Universal Assembler.','All rows have an available producer and preceding prerequisites.']),indent=2))
print('Validated',len(files),'profiles,',len(order),'steps each; zero producer/prerequisite issues.')
