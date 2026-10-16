import sys,contextlib,io,pathlib,re,json,shutil,time
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils');from sod_io import SodIO
class Reader(SodIO):
 def read_unknown_legacy_data(self,s):return [] if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
root=pathlib.Path('D:/armadaIII');repo=pathlib.Path('D:/aramada');backup=pathlib.Path('D:/Xaramada-Modwork/backups/bajor-native-reference-repair-'+str(int(time.time())));idx={f.name.lower():f for f in (root/'odf').rglob('*.odf')};m=json.loads((repo/'bajor/rebuild-manifest.json').read_text(encoding='utf-8-sig'));changes=[];added=[]
def props(name,seen=None):
 seen=set()if seen is None else seen
 if name in seen or name not in idx:return{}
 seen.add(name);t=idx[name].read_text(encoding='latin1');v={}
 for inc in re.findall(r'^\s*#include\s+"([^"]+)"',t,re.M):v.update(props(inc.lower(),seen))
 for k,val in re.findall(r'^[ \t]*(\w+)[ \t]*=[ \t]*(.*)',t,re.M):v[k.lower()]=val.split('//')[0].strip().strip('"')
 return v
for u in m['units']:
 if u['odf']=='bjbase':continue
 file=idx[u['odf']+'.odf'];t=file.read_text(encoding='latin1');old=t;v=props(u['odf']+'.odf');model=v.get('basename',u['odf'])
 try:
  with contextlib.redirect_stdout(io.StringIO()):s=Reader().read_file(str(root/'SOD'/(model+'.sod')))
 except Exception:
  if u.get('role')!='pod':raise
  model='fedpod2'
  with contextlib.redirect_stdout(io.StringIO()):s=Reader().read_file(str(root/'SOD'/(model+'.sod')))
  t=re.sub(r'^[ \t]*baseName[ \t]*=.*$','baseName = "fedpod2"',t,flags=re.I|re.M)
 valid={n['id'].lower()for n in s.nodes};hps=sorted([n for n in valid if re.fullmatch(r'hp\d+',n)],key=lambda n:int(n[2:]));fallback=hps or sorted(n for n in valid if n.startswith('pod'))or['Scene Root']
 for key,value in v.items():
  if 'hardpoint'not in key:continue
  words=re.findall(r'(?:hp|pod)\d+',value,re.I);missing=[w for w in words if w.lower()not in valid]
  if not missing:continue
  def remap(match):
   name=match[0]
   if name.lower()in valid:return name
   number=int(re.search(r'\d+',name)[0]);return min(fallback,key=lambda h:abs(int(re.search(r'\d+',h)[0])-number)if re.search(r'\d+',h)else 9999)
  new=re.sub(r'(?:hp|pod)\d+',remap,value,flags=re.I);t=re.sub(r'^[ \t]*'+re.escape(key)+r'[ \t]*=.*$','',t,flags=re.I|re.M).rstrip()+'\r\n'+key+' = "'+new.strip('"')+'"\r\n'
 for n in s.nodes:
  if n['type']!='MESH':continue
  borg=n['data'].get('borgification');texture=borg.get('texture','')if borg else''
  if not texture or texture=='_B':continue
  found=any((root/'Textures').rglob(texture+'.tga'))
  if not found:
   target=root/'Textures/RGB'/(texture+'.tga');shutil.copy2(root/'Textures/RGB/xbajhull_B.tga',target);added.append(str(target))
 if t!=old:
  rel=file.relative_to(root);bak=backup/rel;bak.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,bak);file.write_text(t,encoding='latin1');overlay=repo/'bajor/overlay'/rel;overlay.write_text(t,encoding='latin1');changes.append(str(rel))
report={'target':str(root),'backup':str(backup),'visualReferencesPatched':changes,'missingBorgTextureFallbacksAdded':added,'statsAndGameplayRetained':True,'runtimeVerified':False};(repo/'reports/bajoran-native-reference-repair.json').write_text(json.dumps(report,indent=2));print(json.dumps({'visualDefinitionsRepaired':len(changes),'missingAssimilationTexturesFilled':len(added)}))
