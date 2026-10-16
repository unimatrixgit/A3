"""Inspect model texture references; restore exact missing textures in armadaIII only."""
import contextlib, io, json, pathlib, shutil, sys, time
ROOT = pathlib.Path('D:/armadaIII')
REPO = pathlib.Path('D:/aramada')
sys.path.insert(0, 'D:/Xaramada-Modwork/tools/stau/src/sod_utils')
from sod_io import SodIO

sources = [pathlib.Path('D:/Startrek Armada II install/Activision/Star Trek Armada II'), pathlib.Path('D:/Xaramada-Modwork/staging/bi2files/MAINDIR'), pathlib.Path('D:/Xaramada-Modwork/staging/ghost/Ghosts_Comp_mod/Star Trek Armada II')]
available = {}
for source in sources:
    for file in source.rglob('*'):
        if file.is_file() and file.suffix.lower() == '.tga':
            available.setdefault(file.name.lower(), file)
textures = {f.name.lower(): f for f in (ROOT/'Textures').rglob('*') if f.is_file()}
manifest = json.loads((REPO/'bajor/manifest.json').read_text())
report = {'target':str(ROOT), 'bajoran':[], 'restoredTextures':[], 'otherModels':[], 'runtimeVerified':False}

def check(file):
    with contextlib.redirect_stdout(io.StringIO()):
        model = SodIO().read_file(str(file))
    meshes=[]
    for node in model.nodes:
        if node['type'] != 'MESH':
            continue
        data=node['data']
        base=data.get('texture','')
        borg=data.get('borgification',{}).get('texture','')
        row={'mesh':node['id'],'base':base,'assimilated':borg}
        for key,name in [('base',base),('assimilated',borg)]:
            if not name:
                row[key+'Available']=False
                continue
            filename=(name if name.lower().endswith('.tga') else name+'.tga').lower()
            if filename not in textures and filename in available:
                destination=ROOT/'Textures/RGB'/available[filename].name
                shutil.copy2(available[filename],destination)
                textures[filename]=destination
                report['restoredTextures'].append(str(destination))
            row[key+'Available']=filename in textures
        meshes.append(row)
    return meshes

for unit in manifest['units']:
    file=ROOT/'SOD'/(unit['model']+'.sod')
    try:
        report['bajoran'].append({'unit':unit['odf'],'meshes':check(file)})
    except Exception as error:
        report['bajoran'].append({'unit':unit['odf'],'error':str(error)})
for file in (ROOT/'SOD').iterdir():
    if file.suffix.lower()!='.sod' or file.stem.lower().startswith(('bj','xvstock_')):
        continue
    try:
        meshes=check(file)
        missing=[m for m in meshes if not m['baseAvailable'] or (m['assimilated'] and not m['assimilatedAvailable'])]
        if missing:
            report['otherModels'].append({'model':file.name,'missing':missing})
    except Exception as error:
        report['otherModels'].append({'model':file.name,'parseError':str(error)})
(REPO/'reports/assimilation-textures.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'bajoranModels':len(report['bajoran']),'bajoranMeshesWithoutAssimilation':sum(not m['assimilatedAvailable'] for u in report['bajoran'] for m in u.get('meshes',[])), 'restoredTextures':len(report['restoredTextures']), 'otherModelsNeedingReview':len(report['otherModels'])}))
