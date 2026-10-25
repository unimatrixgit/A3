from pathlib import Path
import re,json,hashlib,datetime,shutil,subprocess,math
root=Path('D:/armadaIII');repo=Path('D:/aramada');stage=repo/'patches/fleet-nexuses-20261025';overlay=stage/'overlay'
idx={p.stem.lower():p for p in(root/'odf').rglob('*.odf')};idx['ffreight']=root/'odf/ships/ffreight.odf'
pending={};baseline={};cache={}
def source(n):return idx[n].read_text(encoding='latin1')
def raw(n):
 rel=idx[n].relative_to(root).as_posix();return pending[rel]if rel in pending else source(n)
def props(n,seen=None):
 seen=set()if seen is None else seen
 if n in seen:return{}
 seen.add(n);t=raw(n);d={}
 for inc in re.findall(r'(?mi)^[ \t]*#include[ \t]+"([^"]+)"',t):d.update(props(Path(inc).stem.lower(),seen))
 for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t):d[k.lower()]=v.split('//')[0].strip().strip('"')
 return d
def q(v):return '"'+str(v)+'"'
def put(t,k,v):return re.sub(r'(?mi)^[ \t]*'+re.escape(k)+r'[ \t]*=[^\r\n]*','',t).rstrip()+'\n'+k+' = '+str(v)+'\n'
def update(t,d):
 for k,v in d.items():t=put(t,k,v)
 return t
def emit(n,t,folder='stations'):
 if n not in idx:idx[n]=root/'odf'/folder/(n+'.odf')
 pending[idx[n].relative_to(root).as_posix()]=t
def ordered(d,prefix='builditem'):return[(int(k[len(prefix):]),v)for k,v in sorted(d.items(),key=lambda kv:int(kv[0][len(prefix):])if re.fullmatch(prefix+r'\d+',kv[0])else-1)if re.fullmatch(prefix+r'\d+',k)]
def menu(t,items):
 assert len(items)<=14,items
 t=re.sub(r'(?mi)^[ \t]*buildItem\d+[ \t]*=[^\r\n]*','',t)
 for i,n in enumerate(items):t=put(t,'buildItem'+str(i),q(n))
 return t
def clean(t,pattern):return re.sub(r'(?mi)^[ \t]*(?:'+pattern+r')[ \t]*=[^\r\n]*','',t)
def num(v):return float(str(v).rstrip('fF;'))
P={n:props(n)for n in list(idx)}
baseline={n:{'file':idx[n].relative_to(root).as_posix(),'properties':d,'hash':hashlib.sha256(idx[n].read_bytes()).hexdigest()}for n,d in P.items()}
CORE_NAMES={'f':'San Francisco Fleet Nexus','b':'Unimatrix Fleet Nexus','k':"Ty'Go'Kor Fleet Forge",'r':'Rator III Warbird Nexus','c':'Monac Fleet Foundry','d':'Torros III Fleet Nexus','bj':'Dahkur Militia Nexus','br':'Breen Confederacy Fleet Nexus','fg':'Grand Nagus Commerce Nexus','bg':'Grand Nagus Commerce Nexus'}
RACE={'f':'federation','b':'borg','k':'klingon','r':'romulan','c':'cardassian','d':'dominion','bj':'bajoran','br':'breen','fg':'ferengi','bg':'borg'}
BUILD={'f':'fconst','b':'bconst','k':'kconst','r':'rconst','c':'cconst','d':'dconst','bj':'bjconst','br':'brconst','fg':'xfgconst','bg':'xbgconst'}
BASE={'f':'fbase','b':'bbase','k':'kbase','r':'rbase','c':'cbase','d':'dbase','bj':'bjbase','br':'brbase','fg':'xfgmerc','bg':'xbgmerc'}
YARDS={'f':['fyard','fyard2','fyard3'],'b':['byard','byard2','byard3'],'k':['kyard','kyard2','kyard3'],'r':['ryard','ryard2','ryard3'],'c':['cyard','cyard2','cyard3'],'d':['dyard','nxdheavy','dyard3'],'bj':['bjyard','bjyard2'],'br':['bryard'],'fg':['xfgmerc','xfgserv'],'bg':['xbgmerc','xbgserv']}
YARD_NAMES={'f':['Antares Escort Dock','Copernicus Cruiser Dock','McKinley Capital Dock'],'b':['Assembly Matrix','Tactical Assembly Matrix','Omega Assimilation Matrix'],'k':["B'rel Patrol Dock","Vor'cha Assault Dock",'Kahless Command Forge'],'r':['Valdore Patrol Dock',"D'deridex Assembly Dock",'Tal Shiar Command Dock'],'c':['Hideki Patrol Dock','Galor Assembly Dock','Obsidian Command Dock'],'d':["Jem'Hadar Attack Dock",'Founder Heavy Dock','Great Link Command Dock'],'bj':['Militia Patrol Dock','Shakaar Command Dock'],'br':['Confederacy Assault Dock'],'fg':["D'Kora Contract Dock",'Nog Industrial Dock'],'bg':["D'Kora Contract Dock",'Nog Industrial Dock']}
SERVICE_NAMES={'f':['Starbase 74 Service Nexus','McKinley Service Dock','Copernicus Service Dock'],'b':['Collective Regeneration Nexus','Regeneration Matrix','Reclamation Matrix'],'k':["Qo'noS Refit Citadel",'Ketha Refit Dock','Mogh Recovery Dock'],'r':["Ch'Rihan Restoration Nexus",'Ki Baratan Refit Dock','Rator Recovery Dock'],'c':['Cardassia Prime Refit Nexus','Lakarian Service Dock','Coranum Recovery Dock'],'d':['Great Link Restoration Nexus','Founder Restoration Dock',"Jem'Hadar Recovery Dock"],'bj':['Dahkur Refit Sanctuary','Kendra Service Dock','Militia Recovery Dock'],'br':['Confederacy Cryogenic Service Nexus','Gor Restoration Dock','Pran Reclamation Dock'],'fg':["Nog's Service Exchange",'Profit Recovery Dock','Asset Reclamation Dock'],'bg':["Nog's Service Exchange",'Profit Recovery Dock','Asset Reclamation Dock']}
RESEARCH={'f':['fresear','fresear2','fupgrade'],'b':['bresear','bresear2','bupgrade'],'k':['kresear','kresear2','kupgrade'],'r':['rresear','rresear2','rupgrade','xselaresearch'],'c':['cresear','cresear2','cupgrade'],'d':['dresear','dresear2','dupgrade'],'bj':['bjresear','bjresear2','bjupgrade'],'br':['brresear','brresear2'],'fg':['xfgresearch'],'bg':['xbgresearch']}
RESEARCH_NAMES={'f':'Daystrom Research Institute','b':'Collective Analysis Complex','k':"Qu'Vat Research Citadel",'r':'Tal Shiar Science Directorate','c':'Obsidian Research Institute','d':"Founder's Science Enclave",'bj':'Bajoran Science Institute','br':'Confederacy Science Complex','fg':'Nagus Commerce Institute','bg':'Nagus Commerce Institute'}
LAB_NAMES={'f':['Cochrane Propulsion Laboratory','Zimmerman Systems Laboratory','Daystrom Tactical Laboratory','Temporal Investigations Annex'],'b':['Propulsion Adaptation Node','Systems Optimisation Node','Tactical Assimilation Node','Advanced Analysis Node'],'k':['Imperial Propulsion Laboratory','Imperial Systems Laboratory','Disruptor Development Forge','Special Weapons Forge'],'r':['Singularity Engineering Laboratory','Cloaking Systems Laboratory','Plasma Weapons Laboratory',"Sela's Special Projects"],'c':['Central Command Engineering','Cardassian Systems Bureau','Spiral-Wave Weapons Laboratory','Obsidian Special Projects'],'d':['Dominion Propulsion Laboratory','Vorta Systems Laboratory','Polaron Weapons Laboratory',"Jem'Hadar Adaptation Laboratory"],'bj':['Militia Engineering Laboratory','Kendra Systems Laboratory','Militia Tactical Laboratory','Celestial Temple Observatory'],'br':['Cryogenic Engineering Laboratory','Concealment Systems Laboratory','Polaron Weapons Laboratory','Energy Dissipation Laboratory'],'fg':['Dilithium Contracts Bureau','Metal Processing Bureau','Latinum Prospecting Bureau','Advanced Extraction Bureau'],'bg':['Dilithium Contracts Bureau','Metal Processing Bureau','Advanced Extraction Bureau','Contract Systems Bureau']}
BEAMS={'f':'fbasephas','b':'bb3phas','k':'kc12phas','r':'rc07phas','c':'cc10phas','d':'zjmphas','bj':'fbasephas','br':'zjmphas','fg':'xfgcruisb','bg':'xfgcruisb'}
TORPS={'f':'fbaserphot','b':'bb3phot','k':'kc05phot','r':'rc08phot','c':'cc08plas','d':'jmphot','bj':'fbaserphot','br':'jmphot','fg':'xfgcruist','bg':'xfgcruist'}
HWP={'f':'fhwp','b':'bhwp','k':'khwp','r':'rhwp','c':'chwp','d':'dturret3','bj':'bjhwp','br':'nxbrhwp','fg':'nxfghwp','bg':'nxbghwp'}
