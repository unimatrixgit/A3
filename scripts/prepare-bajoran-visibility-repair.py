import pathlib,json,sys,contextlib,io,hashlib
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils');from sod_io import SodIO
class IO(SodIO):
 def read_unknown_legacy_data(self,s):return []if self.curr_sod_version>1.7 else super().read_unknown_legacy_data(s)
 def write_unknown_legacy_data(self,d,s):
  if self.curr_sod_version<=1.7:super().write_unknown_legacy_data(d,s)
root=pathlib.Path('D:/armadaIII');stage=pathlib.Path('D:/Xaramada-Modwork/bajor-visibility-repair');repo=pathlib.Path('D:/aramada');m=json.loads(pathlib.Path('D:/Xaramada-Modwork/bajor-completion-v2/manifest.json').read_text());files=[]
for u in m['units']:
 if u['odf']=='bjbase':continue
 rel='SOD/'+u['odf']+'.sod';source=root/rel
 with contextlib.redirect_stdout(io.StringIO()):model=IO().read_file(str(source))
 changes=[]
 for n in model.nodes:
  if n['type']=='MESH':
   d=n['data'];changes.append({'mesh':n['id'],'previousMaterial':d['texture_material'],'previousBumpMap':d['bump_map']});d['texture_material']='opaque';d['bump_map']=1
 dest=stage/rel;dest.parent.mkdir(parents=True,exist_ok=True);w=IO();w.curr_sod_version=model.version
 with contextlib.redirect_stdout(io.StringIO()):w.write_file(model,str(dest));check=IO().read_file(str(dest))
 assert len(check.nodes)==len(model.nodes)
 assert all(n['data']['texture_material']=='opaque'for n in check.nodes if n['type']=='MESH')
 files.append({'path':rel,'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'changes':changes})
report={'target':str(root),'stage':str(stage),'files':files,'hypothesis':'Generated 1.93 meshes used default/0 material settings; visible installed native models use opaque/1. Align those settings to test invisible hulls. Texture files exist; cause not yet confirmed in game.','geometryPreserved':True,'statsAiAudioUntouched':True,'applied':False,'runtimeVerified':False};(repo/'reports/bajoran-visibility-repair.json').write_text(json.dumps(report,indent=2));print('Staged',len(files),'model material repairs; round-trip checked. Active files unchanged.')
