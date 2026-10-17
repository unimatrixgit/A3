import contextlib,io,sys,pathlib,re,json,os
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils');from sod_io import SodIO
class Reader(SodIO):
 def read_unknown_legacy_data(self,s):return [] if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
root=pathlib.Path('D:/armadaIII');stage=pathlib.Path('D:/Xaramada-Modwork/bajor-durability-research');idx={f.name.lower():f for folder in [root/'odf',stage/'odf']for f in folder.rglob('*.odf')};textures={f.name.lower()for folder in [root/'Textures',root/'Textures']for f in folder.rglob('*.tga')}
def props(name,seen=None):
 seen=set()if seen is None else seen
 if name in seen or name not in idx:return{}
 seen.add(name);t=idx[name].read_text(encoding='latin1');v={}
 for inc in re.findall(r'^\s*#include\s+"([^"]+)"',t,re.M):v.update(props(inc.lower(),seen))
 for k,val in re.findall(r'^\s*(\w+)\s*=\s*(.*)',t,re.M):v[k.lower()]=val.split('//')[0].strip().strip('"')
 return v
m=json.loads(pathlib.Path('D:/aramada/bajor/rebuild-manifest.json').read_text(encoding='utf-8-sig'));errors=[];warnings=[];results=[]
for u in m['units']:
 v=props(u['odf']+'.odf');model=v.get('basename',u['odf']);file=stage/'SOD'/(model+'.sod');file=file if file.exists()else root/'SOD'/(model+'.sod')
 try:
  with contextlib.redirect_stdout(io.StringIO()):s=Reader().read_file(str(file))
 except Exception as exc:
  if os.environ.get('BAJOR_VALIDATE_LIVE')=='1':
   warnings.append({'unit':u['odf'],'model':model,'reason':'External parser cannot fully decode native installed model','detail':str(exc)})
   continue
  raise
 names={n['id'].lower()for n in s.nodes};meshes=[n for n in s.nodes if n['type']=='MESH'];faces=sum(len(g['faces'])for n in meshes for g in n['data']['vertex_lighting_groups'])
 if not faces:errors.append([u['odf'],'Empty geometry'])
 for k,value in v.items():
  if 'hardpoint' in k:
   for hp in re.findall(r'(?:hp|pod)\d+',value,re.I):
    if hp.lower()not in names:errors.append([u['odf'],'Missing actual model hardpoint',hp])
 for n in meshes:
  d=n['data'];tex=[d['texture']];b=d.get('borgification');tex+=([b['texture']]if b else[])
  for t in tex:
   if t and t!='_B' and t.lower()+'.tga'not in textures:errors.append([u['odf'],'Missing actual model texture',t])
 results.append({'unit':u['odf'],'actualModel':model,'faces':faces,'nodes':len(s.nodes)})
report={'target':str(root),'units':results,'errors':errors,'warnings':warnings,'runtimeVerified':False};pathlib.Path('D:/aramada/reports/bajoran-durability-assets'+('-live' if os.environ.get('BAJOR_VALIDATE_LIVE')=='1' else '')+'.json').write_text(json.dumps(report,indent=2));print(json.dumps({'modelsChecked':len(results),'errors':errors,'parserWarnings':len(warnings)}));sys.exit(bool(errors))





