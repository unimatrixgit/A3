from pathlib import Path
s=Path('scripts/stage-yard-variety-20261031.py').read_text();exec(s.split('for name,a in design')[0])
from PIL import ImageFont
manifest=json.loads((stage/'manifest.json').read_text());sprite=(root/'Sprites/gui_global.spr').read_text(encoding='latin1');font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',14);records=[];sheet=Image.new('RGB',(8*100,math.ceil(len(manifest['units'])/8)*100),(10,16,24));draw=ImageDraw.Draw(sheet)
for i,row in enumerate(manifest['units']):
 n=row['unit'];alias=Path(row['model']).stem;model=load(overlay/row['model']);im=preview(model,160).resize((64,64),Image.Resampling.LANCZOS).convert('RGB');icon=im.copy();dr=ImageDraw.Draw(icon)
 # Keep the existing game's framed build-button format, with tier/service badge.
 color={'f':(90,170,255),'b':(70,230,90),'k':(235,90,70),'r':(110,230,170),'c':(230,180,70),'d':(185,120,235),'bj':(225,165,80),'br':(100,215,230),'fg':(240,175,65),'bg':(70,230,90)}[design['assets'][n]['theme']]
 dr.rectangle((0,0,63,63),outline=color,width=2);label='R'if row['tier']<0 else str(row['tier']+1);dr.rectangle((47,45,62,62),fill=(10,15,20));dr.text((49,45),label,font=font,fill=color)
 td=overlay/'Textures/RGB';td.mkdir(parents=True,exist_ok=True);gb='gb'+alias;wf='wf'+alias;icon.save(td/(gb+'.tga'));im.save(td/(wf+'.tga'))
 keys=['b_'+n,'b_'+alias]+[u+'w'+str(j)for u in[n,alias]for j in range(1,6)]
 for key in keys:sprite=re.sub(r'(?mi)^'+re.escape(key)+r'[ \t]+[^\r\n]*','',sprite)
 sprite+='\n@reference=64\n@tmaterial=default\nb_'+n+' '+gb+' 0 0 64 64\nb_'+alias+' '+gb+' 0 0 64 64\n'
 for u in[n,alias]:
  for j in range(1,6):sprite+=u+'w'+str(j)+' '+wf+' 0 0 64 64\n'
 x=i%8*100;y=i//8*100;sheet.paste(icon,(x+18,y));draw.text((x+2,y+68),n,fill='white');records.append({'unit':n,'buildTexture':gb,'groupTexture':wf,'spriteAliases':keys})
p=overlay/'Sprites/gui_global.spr';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(sprite.replace('\r','').replace('\n','\r\n').encode('latin1'));sheet.save(stage/'buttons-preview.png');(stage/'buttons.json').write_text(json.dumps({'units':records,'sourceSpriteSha256':hashlib.sha256((root/'Sprites/gui_global.spr').read_bytes()).hexdigest(),'installed':False},indent=2)+'\n');print('Staged',len(records),'build and group icon sets')
