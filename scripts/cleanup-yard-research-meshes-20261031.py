from pathlib import Path
s=Path('scripts/stage-yard-variety-20261031.py').read_text();exec(s.split('for name,a in design')[0])
import datetime,subprocess
stage=repo/'patches/yard-cleanup-20261031';overlay=stage/'overlay';overlay.mkdir(parents=True,exist_ok=True);manifest=json.loads((repo/'patches/yard-variety-20261031/manifest.json').read_text());records=[];checked=[]
from PIL import ImageFont
font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',14)
for row in manifest['units']:
 n=row['unit'];tier=row['tier'];checked.append(n)
 if tier not in [1,4]:continue
 code=design['assets'][n]['theme'];prefix={'bj':'c','fg':'r','bg':'b','br':'br'}.get(code,code);a=len(parts(prefix+'yard2')[0]);b=len(parts(prefix+('resear2'if tier==4 else'resear'))[0]);ids={'yv31_'+str(i)for i in range(a,a+b)}
 model=load(root/row['model']);present={v['id']for v in model.nodes if v['type']=='MESH'};assert ids<=present,(n,len(ids),len(present))
 anchors=[copy.deepcopy(v)for v in model.nodes if v['type']!='MESH'];model.nodes[:]=[v for v in model.nodes if not(v['type']=='MESH'and v['id']in ids)]
 out=overlay/row['model'];out.parent.mkdir(parents=True,exist_ok=True);w=IO();w.curr_sod_version=model.version
 with contextlib.redirect_stdout(io.StringIO()):w.write_file(model,str(out))
 m=load(out);assert[v for v in m.nodes if v['type']!='MESH']==anchors
 im=preview(m,160).resize((64,64),Image.Resampling.LANCZOS).convert('RGB');icon=im.copy();dr=ImageDraw.Draw(icon);color={'f':(90,170,255),'b':(70,230,90),'k':(235,90,70),'r':(110,230,170),'c':(230,180,70),'d':(185,120,235),'bj':(225,165,80),'br':(100,215,230),'fg':(240,175,65),'bg':(70,230,90)}[code];dr.rectangle((0,0,63,63),outline=color,width=2);dr.rectangle((47,45,62,62),fill=(10,15,20));dr.text((49,45),str(tier+1),font=font,fill=color)
 alias=Path(row['model']).stem;td=overlay/'Textures/RGB';td.mkdir(parents=True,exist_ok=True);icon.save(td/('gb'+alias+'.tga'));im.save(td/('wf'+alias+'.tga'));records.append({'unit':n,'removedResearchMeshes':b,'model':row['model'],'buildIcon':'Textures/RGB/gb'+alias+'.tga','groupIcon':'Textures/RGB/wf'+alias+'.tga'});print(n,'removed',b,flush=True)
(stage/'manifest.json').write_text(json.dumps({'checkedYards':checked,'changed':records,'runtimeVerified':False,'repairDocksUnchanged':True},indent=2)+'\n');print('Checked',len(checked),'cleaned',len(records))
