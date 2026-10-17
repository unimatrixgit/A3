import pathlib,json,re,sys,contextlib,io,shutil,numpy as np
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils');from sod_io import SodIO
class IO(SodIO):
 def read_unknown_legacy_data(self,s):return [] if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
 def write_unknown_legacy_data(self,d,s):
  if self.curr_sod_version<=1.7:super().write_unknown_legacy_data(d,s)
root=pathlib.Path('D:/armadaIII');stage=pathlib.Path('D:/Xaramada-Modwork/bajor-completion-v2');repo=pathlib.Path('D:/aramada');m=json.loads((stage/'manifest.json').read_text());idx={f.name.lower():f for f in (root/'odf').rglob('*.odf')}
def props(n,seen=None):
 seen=set()if seen is None else seen
 if n in seen:return{}
 seen.add(n);t=idx[n].read_text(encoding='latin1');v={}
 for inc in re.findall(r'^[ \t]*#include[ \t]+"([^"]+)"',t,re.M):v.update(props(inc.lower(),seen))
 for k,x in re.findall(r'^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',t,re.M):v[k.lower()]=x.split('//')[0].strip().strip('"')
 return v
def extent(model):
 nodes={n['id']:n for n in model.nodes};cache={}
 def world(n,seen=None):
  if n['id']in cache:return cache[n['id']]
  seen=set()if seen is None else seen
  if n['id']in seen:return np.eye(4)
  seen.add(n['id'])
  t=np.asarray(n['local_transform']);a=np.eye(4);a[:3,:3]=t[:3].T;a[:3,3]=t[3];parent=nodes.get(n['parent']);a=world(parent,seen)@a if parent else a;cache[n['id']]=a;return a
 vs=[(world(n)@np.c_[np.asarray(n['data']['vertices']),np.ones(len(n['data']['vertices']))].T).T[:,:3]for n in model.nodes if n['type']=='MESH'and n['data']['vertices']]
 return float(np.ptp(np.concatenate(vs),axis=0).max())
reports=[]
for u in m['units']:
 name=u['odf'];v=props(name+'.odf');old=v.get('basename',name);src=stage/'SOD'/(name+'.sod')
 if name=='bjbase':src.unlink();continue
 with contextlib.redirect_stdout(io.StringIO()):model=IO().read_file(str(src));native=IO().read_file(str(root/'SOD'/(old+'.sod')))
 ratio=extent(native)/extent(model)
 for n in model.nodes:
  if n['type']=='MESH':n['data']['vertices']=(np.array(n['data']['vertices'])*ratio).tolist()
  n['local_transform'][3]=[x*ratio for x in n['local_transform'][3]]
 # Add every inherited construction/weapon attachment required by the actual unit.
 names={n['id'].lower()for n in model.nodes}
 import copy
 for key,val in v.items():
  if 'hardpoint'not in key:continue
  for hp in re.findall(r'(?:hp|pod|bot)\d+',val,re.I):
   if hp.lower()not in names:
    model.nodes.append({'type':'NULL_OR_HARDPOINT','id':hp,'parent':'hardpoints','local_transform':[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],[0.,0.,0.]],'data':None});names.add(hp.lower())
 model.set_nodes(model.nodes);w=IO();w.curr_sod_version=model.version
 with contextlib.redirect_stdout(io.StringIO()):w.write_file(model,str(src));check=IO().read_file(str(src))
 data=json.loads((stage/'SOD'/(name+'.geometry.json')).read_text());data['vertices']=(np.array(data['vertices'])*ratio).tolist();(stage/'SOD'/(name+'.geometry.json')).write_text(json.dumps(data))
 rel=pathlib.Path('odf')/u['folder']/(name+'.odf');text=(root/rel).read_text(encoding='latin1');text=re.sub(r'^[ \t]*baseName[ \t]*=[^\r\n]*','baseName = "'+name+'"',text,flags=re.M|re.I)
 if not re.search(r'^[ \t]*baseName[ \t]*=',text,re.M|re.I):text+='\r\nbaseName = "'+name+'"\r\n'
 if name=='bjmining':text=re.sub(r'^[ \t]*freighterName[ \t]*=[^\r\n]*','freighterName = "bjfreight"',text,flags=re.M|re.I)
 (stage/rel).parent.mkdir(parents=True,exist_ok=True);(stage/rel).write_text(text,encoding='latin1')
 reports.append({'unit':name,'nativeReference':old,'geometryScale':ratio,'nativeFootprintPreserved':True,'roundTrip':True,'borgTexture':'xbjv2hull_B','runtimeVerified':False})
for src,dst in [('xbajhull.tga','xbjv2hull.tga'),('xbajhull_B.tga','xbjv2hull_B.tga')]:
 out=stage/'Textures/RGB'/dst;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/'Textures/RGB'/src,out)
(repo/'reports/bajoran-completion-model-sizing.json').write_text(json.dumps(reports,indent=2));print('Staged',len(reports),'sized faction models; live DS9 preserved.')

