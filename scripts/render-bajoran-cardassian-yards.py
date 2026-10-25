"""Render the staged Cardassian-derived Bajoran yards, no live writes."""
from pathlib import Path
exec(Path('D:/aramada/scripts/build-native-faction-stations.py').read_text().split('for index,(n,a)in enumerate')[0])
out=repo/'patches/compact-yard-preview';sheet=Image.new('RGB',(1600,850),(10,15,22))
for i,(n,title)in enumerate([('bjyard','Dahkur Militia Yard'),('bjyard2','Shakaar Command Yard')]):
 model=load_model(O/'SOD'/('ty26_'+n+'.sod'));im=preview(model,800);sheet.paste(im,(i*800,30));ImageDraw.Draw(sheet).text((i*800+25,20),title,font=font,fill=(230,210,160));im.save(out/(n+'-cardassian-derived.png'))
sheet.save(out/'bajor-cardassian-yard-sheet.png');print(out/'bajor-cardassian-yard-sheet.png')
