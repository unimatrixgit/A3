from pathlib import Path
import sys,json,re,hashlib,contextlib,io
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils');from sod_io import SodIO
class Reader(SodIO):
 def read_unknown_legacy_data(self,s):return []if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
root=Path('D:/armadaIII');stage=Path('D:/Xaramada-Modwork/bajor-yard-repair');files=[]
for name in ['bjyard','bjyard2','bjyard3']:
 rel='odf/stations/'+name+'.odf';p=root/rel;t=p.read_text();base=re.search(r'(?mi)^baseName[ \t]*=[ \t]*"([^"]+)"',t)[1]
 with contextlib.redirect_stdout(io.StringIO()):m=Reader().read_file(str(root/'SOD'/(base+'.sod')))
 nodes={n['id'].lower()for n in m.nodes};hp=re.search(r'(?mi)^repairhardpoint[ \t]*=[ \t]*"([^"]+)"',t)
 assert hp and hp[1].lower()in nodes,(name,'Missing repair docking node')
 t,n=re.subn(r'(?mi)^repairFacility[ \t]*=[ \t]*0[ \t]*$', 'repairFacility = 1',t);assert n==1
 t=t.replace("//Even though we are a shipyard we don't have a repair facility",'// Accept friendly ships for repair at the native repair docking point.')
 o=stage/rel;o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes(t.replace('\r','').replace('\n','\r\n').encode('latin1'));files.append({'path':rel,'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sha256':hashlib.sha256(o.read_bytes()).hexdigest(),'repairHardpoint':hp[1]})
Path('D:/aramada/reports/bajoran-yard-repair.json').write_text(json.dumps({'stage':str(stage),'files':files,'applied':False,'runtimeVerified':False},indent=2));print('Prepared three repair-enabled yards; all docking nodes present')
