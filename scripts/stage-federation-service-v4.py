"""Stage a replacement for review only; never deploy automatically."""
from pathlib import Path
script=Path('D:/aramada/scripts/stage-vanilla-station-redesign.py').read_text(encoding='utf-8-sig')
script=script.replace("stage=repo/'patches/vanilla-stations-20261026'","stage=repo/'patches/federation-service-v4-20261026'")
script=script.replace("if a['kind']not in ['yard','service','research']:continue","if n!='xyr_f':continue")
insert=" exec(Path('D:/aramada/scripts/federation-service-v4-geometry.py').read_text())\n allparts,source=federation_service_v4(globals());central=source\n"
script=script.replace(" points=np.concatenate([p['data']['vertices']for p in allparts]);",insert+" points=np.concatenate([p['data']['vertices']for p in allparts]);")
script=script.replace("pos=(np.zeros(3)-center)/span*size","pos=(np.array([-1.03,.12,0])-center)/span*size")
exec(compile(script,__file__,'exec'))
p=stage
preview(load_model(p/'overlay/SOD/ty26_xyr_f.sod'),1500).save(p/'federation-service-v4.png')
print('Review only. Installed game unchanged.')
