"""Preview the actual staged SOD geometry, rather than a concept image."""
from pathlib import Path
exec(Path('D:/aramada/scripts/build-native-faction-stations.py').read_text().split('for index,(n,a)in enumerate')[0])
out=repo/'patches/compact-yard-preview';art=json.loads((stage/'artwork.json').read_text());rows=[r for r in art if r['kind']=='yard'];sheet=Image.new('RGB',(1280,350*math.ceil(len(rows)/4)),(10,15,22))
for i,r in enumerate(rows):
 n=r['model'].removeprefix('ty26_');m=load_model(O/'SOD'/(r['model']+'.sod'));im=preview(m,640);im.save(out/(n+'-staged.png'));small=im.resize((320,320));sheet.paste(small,((i%4)*320,(i//4)*350));ImageDraw.Draw(sheet).text(((i%4)*320+8,(i//4)*350+320),n+' | '+str(r['bays'])+' bay',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18),fill=(220,235,245))
sheet.save(out/'all-staged-yards.png')
report={'status':'STAGED','yards':len(rows),'borgMinimumYards':3,'roster':json.loads((out/'borg-proposed-production.json').read_text()),'yardFits':{r['model']:r.get('fit')for r in rows},'gameplayVerified':False}
(out/'staging-report.json').write_text(json.dumps(report,indent=2));print(out/'all-staged-yards.png')
