from pathlib import Path
import json,re,collections,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont
repo=Path('D:/aramada');root=Path('D:/armadaIII');stage=Path('D:/Xaramada-Modwork/unit-identity-stage');m=json.loads((stage/'manifest.json').read_text());sprite=(stage/'Sprites/gui_global.spr').read_text(encoding='latin1');original=(root/'Sprites/gui_global.spr').read_text(encoding='latin1');P=json.loads((repo/'reports/icon-refresh-before.json').read_text());models={p.stem.lower():p for p in(root/'SOD').glob('*')if p.suffix.lower()=='.sod'}
def put(t,k,v):return re.sub(r'(?mi)^[ \t]*'+re.escape(k)+r'\s*=[^\r\n]*','',t)+'\n'+k+' = "'+v+'"\n'
# Missing model assets in dormant legacy definitions cannot be accurately depicted.
produced={v.lower()for d in P.values()for k,v in d.items()if re.fullmatch('(secondary)?builditem[0-9]+',k)}
excluded=[x for x in m['units']if x['artwork']=='missing-model-placeholder'];assert all(x['unit']not in produced for x in excluded),excluded
m['excludedDormantMissingAssets']=[{'unit':x['unit'],'reason':'No installed model or build icon; not offered by any producer; left unchanged'}for x in excluded];m['units']=[x for x in m['units']if x not in excluded]
for x in excluded:
 m['files'].remove(x['odf']);m['sourceODFHashes'].pop(x['odf']);sprite=re.sub(r'(?mi)^b_'+x['unit']+r'[ \t]+[^\r\n]*','',sprite)
 # Restore any previous sprite mapping verbatim if present.
 match=re.search(r'(?mi)^b_'+x['unit']+r'[ \t]+[^\r\n]*',original)
 if match:
  ref=re.findall(r'(?mi)^@reference\s*=\s*(\d+)',original[:match.start()])[-1];sprite+='\n@reference='+ref+'\n'+match[0]+'\n'
byModel=collections.defaultdict(list)
for x in m['units']:byModel[x['model']].append(x)
conflict={k for k,v in byModel.items()if len({(x['role'],x['race'])for x in v})>1};copies=[];added=set();wireframes=0
for x in m['units']:
 n=x['unit'];model=x['model'];alias='xui_'+n if model in conflict else model
 if model in conflict:
  rel='SOD/'+alias+'.sod';out=stage/rel;out.parent.mkdir(exist_ok=True);shutil.copyfile(models[model],out);m['files'].append(rel);m.setdefault('sourceAssetHashes',{})[str(models[model].relative_to(root)).replace('\\','/')]=hashlib.sha256(models[model].read_bytes()).hexdigest();p=stage/x['odf'];p.write_bytes(put(p.read_text(encoding='latin1'),'baseName',alias).replace('\r','').replace('\n','\r\n').encode('latin1'));copies.append({'unit':n,'originalModel':model,'iconModelAlias':alias})
 if alias!=n and alias not in added:
  added.add(alias);key='b_'+alias;sprite=re.sub(r'(?mi)^'+re.escape(key)+r'[ \t]+[^\r\n]*','',sprite);a=x['cell'];sprite+='\n@reference=512\n@tmaterial=default\n'+key+' '+x['texture']+' '+' '.join(map(str,a))+'\n'
 if model in conflict:
  for i in range(1,6):
   dest=alias+'w'+str(i);found=None
   for donor in [n+'w'+str(i),model+'w'+str(i)]:
    found=re.search(r'(?mi)^'+re.escape(donor)+r'[ \t]+[^\r\n]*',original)
    if found:break
   if found:
    ref=re.findall(r'(?mi)^@reference\s*=\s*(\d+)',original[:found.start()])[-1];sprite+='\n@reference='+ref+'\n@tmaterial=default\n'+re.sub(r'^\S+',dest,found[0])+'\n';wireframes+=1
 x['iconModelAlias']=alias
(stage/'Sprites/gui_global.spr').write_bytes(sprite.replace('\r','').replace('\n','\r\n').encode('latin1'));m['sharedModelConflictCopies']=copies;m['preservedWireframeAliases']=wireframes
# Validate all icon cells and name uniqueness, and ensure text/model-alias changes cannot alter gameplay stats.
assert len({x['name'].lower()for x in m['units']})==len(m['units'])
for x in m['units']:
 assert re.search(r'(?mi)^b_'+re.escape(x['unit'])+r'\s',sprite)
 assert re.search(r'(?mi)^b_'+re.escape(x['iconModelAlias'])+r'\s',sprite)
 im=Image.open(stage/'Textures/RGB'/(x['texture']+'.tga'));assert im.size==(512,512);a=x['cell'];assert a[0]+64<=512 and a[1]+64<=512
 def raw(t):
  return {k.lower():v.strip()for k,v in re.findall(r'(?mi)^\s*([a-z][a-z0-9_]*)\s*=\s*([^\r\n]*)',t)if k.lower()not in ['unitname','tooltip','verbosetooltip','basename']}
 assert raw((stage/x['odf']).read_text(encoding='latin1'))==raw((root/x['odf']).read_text(encoding='latin1')),x['unit']
 for line in (stage/x['odf']).read_text(encoding='latin1').splitlines():assert len(line)<2000,x['unit']
# Remove stale generated files from earlier stage passes, within this exact staging directory only.
keep=set(m['files'])|{'manifest.json','unit-icons-preview.png'}
for p in stage.rglob('*'):
 if p.is_file()and p.relative_to(stage).as_posix()not in keep and 'preview'not in p.relative_to(stage).parts:
  assert p.resolve().is_relative_to(stage.resolve());p.unlink()
# Representative preview: faction and resource roles, heroes, constructors, weapons platforms.
selected=[]
for race in ['federation','borg','klingon','romulan','cardassian','dominion','bajoran','ferengi','breen','species8472']:
 group=[x for x in m['units']if x['race']==race];row=[]
 for role in ['BUILD','T2','BASE','DIL','MET','COL','HWP','HERO']:
  matches=[x for x in group if x['role']==role]
  if matches:row.append(matches[0])
 selected.extend(row)
sheet=Image.new('RGB',(960,1040),(9,16,25));dr=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',11)
for j,x in enumerate(selected):
 px=(j%8)*120;py=(j//8)*104;im=Image.open(stage/'Textures/RGB'/(x['texture']+'.tga'));a,b,w,h=x['cell'];sheet.paste(im.crop((a,b,a+w,b+h)).resize((80,80)),(px+20,py));dr.text((px+2,py+81),x['unit'][:18],font=font,fill=(225,235,245))
sheet.save(stage/'unit-icons-preview.png')
m['validation']={'uniqueNames':len(m['units']),'buttonsAndModelAliasesVerified':True,'combatEconomyAndAbilitiesUnchanged':True,'applied':False};m['manifest']=[{'file':f,'sha256':hashlib.sha256((stage/f).read_bytes()).hexdigest()}for f in m['files']];(stage/'manifest.json').write_text(json.dumps(m,indent=2));(repo/'reports/unit-identity-staged.json').write_text(json.dumps(m,indent=2))
lines=['# Staged unit names and tooltips','','Live game unchanged. '+str(len(m['units']))+' faction ships/stations, unique names, model-based buttons and role badges. Heroes carry faction emblems. '+str(len(m['fallbacks'])-len(excluded))+' legacy models retain existing game artwork with new badges. Five unused definitions with missing assets remain unchanged.','','| Faction | Unit | New name | Hover description |','|---|---|---|---|']
for x in m['units']:lines.append('| '+x['race']+' | '+x['unit']+' | '+x['name'].replace('|','/')+' | '+x['description'].replace('|','/')+' |')
(repo/'reports/unit-identity-staged.md').write_text('\n'.join(lines),encoding='utf-8')
p=repo/'status.json';s=json.loads(p.read_text(encoding='utf-8-sig'));s['current']='STAGED ONLY:839 faction ship/station icons and unique names/tooltips.14 icon atlases, role badges, hero faction emblems, shared-model mappings validated.5 legacy definitions retain native artwork;5 unused definitions missing assets left unchanged. Live game files unchanged; awaiting user readiness.';p.write_text(json.dumps(s,indent=2),encoding='utf-8')
print(json.dumps({'stagedUnits':len(m['units']),'sharedModelCopies':len(copies),'wireframeAliases':wireframes,'existingArtworkFallbacks':len(m['fallbacks'])-len(excluded),'excludedDormant':len(excluded),'liveGameChanged':False}))
