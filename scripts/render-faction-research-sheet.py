"""Render the staged faction laboratory SODs without modifying the game."""
from pathlib import Path
exec(Path('D:/aramada/scripts/build-native-faction-stations.py').read_text().split('for index,(n,a)in enumerate')[0])
out=repo/'patches/faction-research-preview';out.mkdir(exist_ok=True);rows=[r for r in json.loads((stage/'artwork.json').read_text())if r['kind']=='research'];sheet=Image.new('RGB',(1280,350*math.ceil(len(rows)/4)),(10,15,22));examples=[]
for i,r in enumerate(rows):
 n=r['unit'];model=load_model(O/'SOD'/(r['model']+'.sod'));im=preview(model,800);im.save(out/(n+'.png'));sheet.paste(im.resize((320,320)),((i%4)*320,(i//4)*350));ImageDraw.Draw(sheet).text(((i%4)*320+10,(i//4)*350+322),n+' | '+r['theme'],font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18),fill=(225,225,200))
 if n in ['bresear','cresear','bjresear']:examples.append((n,im))
sheet.save(out/'all-research-stations.png');trio=Image.new('RGB',(1800,650),(10,15,22))
for i,(n,im)in enumerate(examples):trio.paste(im.resize((600,600)),(i*600,40));ImageDraw.Draw(trio).text((i*600+20,15),{'bresear':'Borg','cresear':'Cardassian','bjresear':'Bajoran'}[n],font=font,fill=(230,230,210))
trio.save(out/'borg-cardassian-bajoran.png');(out/'preview-report.json').write_text(json.dumps({'status':'STAGED','stations':len(rows),'yardsChanged':False,'researchFunctionsChanged':False,'podHardpointsPreserved':True,'bajoranCardassianSharedFamily':True,'runtimeVerified':False},indent=2));print(out/'all-research-stations.png')
variety=Image.new('RGB',(1800,1260),(10,15,22))
for i,(n,title)in enumerate([('bresear','Borg analysis'),('bresear2','Borg advanced science'),('bupgrade','Borg upgrades'),('fresear','Federation engineering'),('rresear2','Romulan science'),('cresear2','Cardassian advanced science')]):
 variety.paste(Image.open(out/(n+'.png')).resize((600,600)),((i%3)*600,(i//3)*630+30));ImageDraw.Draw(variety).text(((i%3)*600+20,(i//3)*630+10),title,font=font,fill=(225,230,215))
variety.save(out/'research-variety-preview.png')
