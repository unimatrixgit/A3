from pathlib import Path
import json,re,collections,datetime
repo=Path('D:/aramada');p=json.loads((repo/'reports/mirror-yard-before.json').read_text());mirror=json.loads((repo/'reports/mirror-ferengi-research.json').read_text())
stars=['bbase','fbase','kbase','rbase','cbase','dbase','brbase','bjbase']
groups={
 'federation':['fconst','fconst2','f31const','xfuconst'],
 'borg':['bconst','bconst2','uconst','xbuconst'],
 'klingon':['kconst','kconst2','xkuconst'],
 'romulan':['rconst','rconst2','xruconst'],
 'cardassian':['cconst','domconst','xcuconst'],
 'dominion':['dconst','xcdconst','xcduniv','xduconst'],
 'breen':['brconst','xbruconst'],
 'bajoran':['bjconst','xbjuconst'],
 'species8472':['714const','8472_passive','8472_defender'],
 'ferengi':['xfgconst'],
 'borg_ferengi':['xbgconst']}
ids={
 'federation':['fconst','fconst2','xfuconst'], 'borg':['bconst','bconst2','xbuconst'],
 'klingon':['kconst','kconst2','xkuconst'], 'romulan':['rconst','rconst2','xruconst'],
 'cardassian':['cconst','xcconst2','xcuconst'], 'dominion':['dconst','xdconst2','xduconst'],
 'breen':['brconst','xbrconst2','xbruconst'], 'bajoran':['bjconst','xbjconst2','xbjuconst'],
 'species8472':['8472_passive','714const','xsuconst'], 'ferengi':[None,None,'xfgconst'],
 'borg_ferengi':[None,None,'xbgconst']}
# Explicit special structures override generic engine class labels. Several are
# implemented as starbases/shipyards even though their actual role is different.
special=set('fsuperbl ksuperbl rsuperbl zsuperbl bsuperbl hub bassturr xbassimst xbharvest btechass bjsuperlab'.split())
t2=set('fyard3 xflegacyyard s31yard byard3 kyard3 kimpyard ryard3 cyard3 cobyard dyard3 dsuperbl bryard3 bjyard3 xhs_yard3 xfomegalab xbomegalab xbtarray'.split())
t1=set('fremmeler fargus rtsens cardassian_super_station'.split())
ferengi=set('xfgmerc xfgserv xfgresearch xfgmetal2 xfgmetal3 xbgmerc xbgserv xbgresearch xbgmetal2 xbgmetal3'.split())
newmir={'federation':['mryfeda','mryfedb'],'borg':['mryborg'],'klingon':['mrykling'],'romulan':['mryrom'],'cardassian':['mrycard'],'dominion':['mrydom'],'breen':['mrybreen'],'bajoran':['mrybajor'],'species8472':['mry8472'],'ferengi':['mryfer']}
def menu(n):return [v.lower()for k,v in sorted(p[n].items(),key=lambda kv:int(kv[0][9:])if re.fullmatch('builditem[0-9]+',kv[0])else-1)if re.fullmatch('builditem[0-9]+',k)]
def name(n):return p.get(n,{}).get('unitname',n)
def tier(n):
 d=p.get(n,{});cl=d.get('classlabel','').lower()
 if n in ferengi or n in special:return 3
 if n in t2 or re.search('turr|hwp|sentinel',n):return 2
 if n in t1:return 1
 if cl=='starbase':return 3
 if n.startswith('mry'):return 2
 return 1
records=[];removed=[]
for race,builders in groups.items():
 old=list(dict.fromkeys(n for b in builders for n in menu(b)))
 # Active Embryo produces ships, not buildings: preserve its evolution menu.
 if race=='species8472':old=[n for n in old if n not in ['8472_collector','8472_scout','8472fig','8472_destroy','8472_cruise1','8472_cruise2']]
 pools={1:[],2:[],3:[]}
 for n in old:pools[3 if race in ['ferengi','borg_ferengi']else tier(n)].append(n)
 if race not in ['ferengi','borg_ferengi']:
  for n in stars:
   if n not in pools[3]:pools[3].append(n)
 for n in newmir.get(race,[]):pools[3 if race=='ferengi'else 2].append(n)
 if race in ['ferengi','borg_ferengi']:pools[3].append('xfgmetal3'if race=='ferengi'else'xbgmetal3')
 pools[3]=[n for n in stars if n in pools[3]]+[n for n in pools[3]if n not in stars]
 rows=[]
 for level,items in pools.items():
  for j in range(0,len(items),13):
   segment=items[j:j+13];unit=ids[race][level-1]
   if j:unit='xu3'+{'federation':'fed','borg':'bor','klingon':'kli','romulan':'rom','cardassian':'car','dominion':'dom','breen':'bre','bajoran':'baj','species8472':'847','ferengi':'fer','borg_ferengi':'bfg'}[race]+str(j//13+1)
   rows.append({'tier':level,'constructor':unit,'buildings':segment,'existing':unit in p})
 assigned={n for row in rows for n in row['buildings']};missing=sorted(set(old)-assigned);removed+=missing
 records.append({'faction':race,'oldConstructors':builders,'oldBuildings':old,'proposed':rows,'omitted':missing})
# Audit actual production references separately from race labels and tech entries.
produced={v.lower()for d in p.values()for k,v in d.items()if re.fullmatch('(secondary)?builditem[0-9]+',k)}
orphans=[]
for n,d in p.items():
 if '/stations/'not in d.get('file','').replace('\\','/').lower():continue
 if n in produced or d.get('classlabel','').lower() in ['pod','upgrade','shieldupgrade','weaponupgrade','sensorupgrade','engineupgrade','specialenergyupgrade']:continue
 if d.get('race')not in groups:continue
 if not d.get('unitname')or n.startswith('mrp'):continue
 orphans.append({'unit':n,'name':name(n),'faction':d.get('race'),'class':d.get('classlabel')})
r={'status':'proposal only; not applied','generated':datetime.datetime.now().astimezone().isoformat(),'commonStarbases':stars,'factions':records,'omittedPreviouslyBuildableBuildings':sorted(set(removed)),'stationDefinitionsWithoutProductionReference':orphans}
(repo/'reports/constructor-tier-plan.json').write_text(json.dumps(r,indent=2))
md='# Proposed constructor tiers\n\nNot applied. Existing construction options are preserved across the proposed tiers. Mirror yards and tier-II Ferengi equipment are planned additions, not yet installed. Maximum 13 menu entries per constructor; additional T3 variants retain overflow.\n\nT1: economy, standard yards, research and upgrades. T2: hero/Omega/mirror yards and defenses. T3: all eight primary faction starbases, faction special structures and Ferengi facilities. Ferengi constructors themselves are T3.\n\nAll strategic starbases: requested price 1,500 dilithium + 1,500 metal, starting crew150; maximum crew unchanged. Heavy platforms and ships using the starbase engine class are not automatically treated as strategic starbases. Species8472 economic compatibility needs to be preserved.\n\n'
for row in records:
 md+='## '+row['faction']+'\n\n'
 for b in row['proposed']:
  md+='### T'+str(b['tier'])+' — '+b['constructor']+(' (new)'if not b['existing']else'')+'\n\n'
  for n in b['buildings']:md+='- '+name(n)+' (`'+n+'`)'+(' — planned Mirror Universe yard'if n.startswith('mry')else'')+'\n'
  md+='\n'
 md+='Previously available buildings omitted: '+(', '.join(row['omitted'])or'none')+'.\n\n'
md+='## Unreferenced station definitions\n\nThese already lack a production reference in the current installation; they are not buildings removed by this proposal. Campaign/script placement and actual purpose must be checked before enabling them. Research pods are excluded by class where identifiable.\n\n'
for d in orphans:md+='- '+d['faction']+': '+d['name']+' (`'+d['unit']+'`, '+str(d['class'])+')\n'
(repo/'reports/constructor-tier-plan.md').write_text(md)
print(json.dumps({'factions':len(records),'previouslyBuildable':sum(len(x['oldBuildings'])for x in records),'omitted':removed,'unreferencedStationDefinitions':len(orphans),'constructors':[(x['faction'],[(b['tier'],b['constructor'],len(b['buildings']))for b in x['proposed']])for x in records]},indent=2))
