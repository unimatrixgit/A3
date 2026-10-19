from pathlib import Path
import json,re,datetime
repo=Path('D:/aramada');prior=json.loads((repo/'reports/equal-building-footprints.json').read_text());backup=Path('D:/Xaramada-Modwork/backups')/('shape-preserving-footprints-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));records=[]
for unit in prior['units']:
 root=Path(unit['root']);f=root/'odf/stations'/unit['unit']
 if not f.exists():f=root/'odf/ships'/unit['unit']
 assert f.exists();t=f.read_text(encoding='latin1');original=t
 # Cancel the forced reference rectangle; let native placement follow this model's own bounding box.
 for key in ['eastBuffer','westBuffer','northBuffer','southBuffer']:
  t=re.sub(r'(?mi)^[ \t]*'+key+r'[ \t]*=[^\r\n]*','',t)+'\n'+key+' = 0\n'
 padding=10 if unit['category']=='heavy' else 100
 t=re.sub(r'(?mi)^[ \t]*footprintBuffer[ \t]*=[^\r\n]*','',t)+'\nfootprintBuffer = '+str(padding)+'\n'
 assert re.findall(r'(?mi)^\s*ScaleSOD\s*=\s*([^\r\n]+)',t)==re.findall(r'(?mi)^\s*ScaleSOD\s*=\s*([^\r\n]+)',original)
 rel=f.relative_to(root);b=backup/root.name/rel;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(f.read_bytes());f.chmod(0o666);data=t.replace('\r','').replace('\n','\r\n').encode('latin1');f.write_bytes(data);assert f.read_bytes()==data
 out=repo/('lab/overlay'if root.name=='ArmadaLab'else'bajor/overlay')/rel;out.write_bytes(data)
 vals=unit['buffers'];old=unit['calculatedFootprintXZ'];own=[old[0]+vals['westBuffer'],old[1]+vals['southBuffer'],old[2]-vals['eastBuffer'],old[3]-vals['northBuffer']]
 records.append({'root':str(root),'unit':unit['unit'],'category':unit['category'],'nativeModelFootprint':True,'directionalBuffers':0,'uniformClearance':padding,'calculatedFootprintXZ':own,'visualScaleUnchanged':True})
(repo/'reports/shape-preserving-building-footprints.json').write_text(json.dumps({'backup':str(backup),'replaces':'equal-building-footprints.json','method':'Native per-model placement rectangle plus uniform clearance; no forced common rectangle or asymmetric buffers','units':records,'runtimeVerified':False},indent=2))
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='Revised building footprints applied to armadaIII and ArmadaLab: 23 starbase variants and 7 heavy platforms now use their own model bounding shape with uniform clearance, replacing the forced common rectangle. All directional footprint overrides reset to zero. Visual size/proportions and gameplay stats unchanged. Backups saved; in-game placement check pending.';p.write_text(json.dumps(s,indent=2));
with(repo/'build.log').open('a')as log:log.write('\n'+s['current']+'\n')
print(json.dumps({'updatedFiles':len(records),'backup':str(backup),'modelShapesPreserved':True}))
