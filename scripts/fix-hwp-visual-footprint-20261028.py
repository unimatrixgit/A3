from pathlib import Path
import sys,re,json,datetime,shutil,contextlib,io
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils');from sod_io import SodIO
class IO(SodIO):
 def read_unknown_legacy_data(self,s):return []if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
 def write_unknown_legacy_data(self,d,s):
  if self.curr_sod_version<=1.7:super().write_unknown_legacy_data(d,s)
 def write_anim_reference(self,a,s):
  self.write_uint8(a['type'],s);self.write_string(a['node'],s);self.write_string(a['anim'],s);self.write_float(a['playback_offset'],s)
root=Path('D:/armadaIII');repo=Path('D:/aramada');backup=Path('D:/Xaramada-Modwork/backups')/('hwp-textures-size-footprint-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));textures={p.stem.lower():p for p in(root/'Textures').rglob('*')if p.is_file()};rows=[]
def put(t,k,v):
 pat=r'(?mi)^[ \t]*'+k+r'[ \t]*=[^\r\n]*'
 return re.sub(pat,lambda m:k+' = '+str(v),t)if re.search(pat,t)else t+'\n'+k+' = '+str(v)+'\n'
def save(p,data):
 rel=p.relative_to(root);b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b);p.write_bytes(data);out=repo/'bajor/overlay'/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
for name in ['fhwp','khwp','rhwp','chwp','dturret3','bjhwp','bhwp']:
 p=root/'odf/stations'/(name+'.odf');t=p.read_text(encoding='latin1');model=re.findall(r'(?mi)^baseName\s*=\s*"([^"]+)"',t)[-1];sod=root/'SOD'/(model+'.sod')
 with contextlib.redirect_stdout(io.StringIO()):m=IO().read_file(str(sod))
 fixed=0;refs=set();meshes=[n for n in m.nodes if n['type']=='MESH'];snapshot=[(len(n['data']['vertices']),len(n['data']['texture_coordinates']))for n in meshes]
 for n in meshes:
  d=n['data'];refs.add(d['texture']);assert d['texture'].lower()in textures,(name,d['texture'])
  if d.get('texture_material')!='opaque':d['texture_material']='opaque';fixed+=1
 if fixed:
  temp=backup/(model+'-validated.sod');temp.parent.mkdir(parents=True,exist_ok=True);writer=IO();writer.curr_sod_version=m.version
  with contextlib.redirect_stdout(io.StringIO()):writer.write_file(m,str(temp));r=IO().read_file(str(temp))
  assert [(len(n['data']['vertices']),len(n['data']['texture_coordinates']))for n in r.nodes if n['type']=='MESH']==snapshot
  assert all(n['data']['texture_material']=='opaque'for n in r.nodes if n['type']=='MESH')
  save(sod,temp.read_bytes())
 old=float(re.findall(r'(?mi)^ScaleSOD\s*=\s*([\d.]+)',t)[-1]);new=old*1.5;t=put(t,'ScaleSOD',format(new,'.12g'));t=put(t,'footprintBuffer',25)
 # Remove explicit zero directional overrides; use mesh footprint with positive uniform clearance.
 for key in ['northBuffer','southBuffer','eastBuffer','westBuffer']:t=re.sub(r'(?mi)^'+key+r'\s*=[^\r\n]*','',t)
 save(p,t.replace('\r','').replace('\n','\r\n').encode('latin1'))
 rows.append({'platform':name,'model':model,'oldScale':old,'newScale':new,'footprintBuffer':25,'opaqueMeshesCorrected':fixed,'texturesVerified':sorted(refs),'meshCount':len(meshes)})
report={'target':str(root),'backup':str(backup),'platforms':rows,'runtimeVerified':False,'note':'Native opaque texture mode; geometry and UV counts verified by SOD round-trip. Positive footprint clearance restored; directional zero overrides removed. Current size multiplied by 1.5.'};(repo/'reports/hwp-visual-footprint-fix-20261028.json').write_text(json.dumps(report,indent=2))
s=repo/'status.json';j=json.loads(s.read_text(encoding='utf-8-sig'));j['current']='HWP visual fix applied to armadaIII: all seven 50% larger, footprint clearance restored, native opaque hull rendering corrected where needed; every diffuse texture reference exists. Geometry round-trip/file checks passed; in-game verification pending.';s.write_text(json.dumps(j,indent=2))
with(repo/'build.log').open('a',encoding='utf-8')as f:f.write('\n'+datetime.datetime.now().isoformat()+' '+j['current']+'\n')
print(json.dumps({'platforms':len(rows),'meshesCorrected':sum(r['opaqueMeshesCorrected']for r in rows),'backup':str(backup),'runtimeVerified':False}))
