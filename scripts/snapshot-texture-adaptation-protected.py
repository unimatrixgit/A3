from pathlib import Path
import hashlib,json
root=Path('D:/armadaIII');files=list((root/'odf').rglob('*.odf'))+list((root/'techtree').glob('*.tt'))+list((root/'SOD').glob('br3_*.sod'))+[root/'SOD/fds9.sod',root/'Sprites/gui_global.spr']+list((root/'Textures/RGB').glob('bjic*.tga'))
r={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()for p in files};Path('D:/Xaramada-Modwork/armadafiles-bajor/protected-before-texture-adaptation.json').write_text(json.dumps(r,indent=2));print('Saved',len(r),'protected model/gameplay/icon hashes')
