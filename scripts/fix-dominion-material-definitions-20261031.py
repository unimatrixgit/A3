from pathlib import Path
exec(Path('scripts/stage-armadafiles-yards-20261031.py').read_text().split('targets=[]')[0])
import datetime,subprocess
manifest=json.loads((stage/'manifest.json').read_text());backup=Path('D:/Xaramada-Modwork/backups')/('dominion-material-definitions-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));pending={};fixed=[];template=copy.deepcopy(load(sods['ay31_fyard']).materials[0]);texture_source=root/'Textures/RGB/ay31t0d6bedacb46d.tga';assert texture_source.exists();pending['Textures/RGB/dmyard31.tga']=texture_source.read_bytes()
for row in manifest['units']:
 m=load(root/row['model']);names={a['name'].lower()for a in m.materials};needed={g['lighting_material']for n in m.nodes if n['type']=='MESH'for g in n['data']['vertex_lighting_groups']};missing={n for n in needed if n and n.lower()not in names}
 if not missing:continue
 before=copy.deepcopy(m.nodes)
 for name in sorted(missing):
  mat=copy.deepcopy(template);mat['name']=name;mat['ambient_color']=[.35]*3;mat['diffuse_color']=[1.0]*3;mat['specular_color']=[.15]*3;mat['specular_shininess']=24.0;mat['self_illumination_enabled']=False;m.materials.append(mat)
 for node in m.nodes:
  if node['type']=='MESH'and node['data']['texture']=='ay31t0d6bedacb46d':node['data']['texture']='dmyard31'
 out=repo/'patches/dominion-material-definitions-20261031'/row['model'];out.parent.mkdir(parents=True,exist_ok=True);w=IO();w.curr_sod_version=m.version
 with contextlib.redirect_stdout(io.StringIO()):w.write_file(m,str(out))
 check=load(out);assert{g['lighting_material'].lower()for n in check.nodes if n['type']=='MESH'for g in n['data']['vertex_lighting_groups']}<={v['name'].lower()for v in check.materials}
 for a,b in zip(before,check.nodes):
  a=copy.deepcopy(a)
  if a['type']=='MESH'and a['data']['texture']=='ay31t0d6bedacb46d':a['data']['texture']='dmyard31'
  assert a==b
 pending[row['model']]=out.read_bytes();fixed.append({'unit':row['unit'],'materialDefinitionsAdded':sorted(missing),'model':row['model']})
assert len(fixed)==5
assert subprocess.check_output(['powershell','-NoProfile','-Command','@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'],text=True).strip()=='0'
for rel,data in pending.items():
 p=root/rel
 if p.exists():
  b=backup/rel;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(p.read_bytes());p.chmod(0o666)
 p.write_bytes(data);out=repo/'bajor/overlay'/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);assert p.read_bytes()==out.read_bytes()
report={'backup':str(backup),'yardModelsAudited':55,'fixed':fixed,'installedFiles':list(pending),'validation':'All55 material group references inspected; all5 undefined domyard materials repaired. Texture linked with8-character basename. Model round-trip and geometry/UV/hardpoint preservation verified.','runtimeVerified':False,'aiCauseConfirmed':False};(repo/'reports/dominion-material-definitions-20261031.json').write_text(json.dumps(report,indent=2)+'\n')
p=repo/'status.json';d=json.loads(p.read_text());d['current']='Dominion white-yard fix installed:5 downloaded yard variants lacked the domyard lighting-material definition; definitions added and hull TGA linked via short native-style name. All55 yards audited for undefined lighting materials. Geometry, UVs and docking points unchanged. Runtime appearance and AI progress still require testing.';p.write_text(json.dumps(d,indent=2)+'\n')
with(repo/'build.log').open('a')as f:f.write('\n'+datetime.datetime.now().isoformat()+' '+d['current']+'\n')
subprocess.run(['git','add','-f','--',*['bajor/overlay/'+x for x in pending],'reports/dominion-material-definitions-20261031.json','scripts/fix-dominion-material-definitions-20261031.py','status.json','build.log'],check=True);print(d['current'])
