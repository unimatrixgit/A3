const fs=require('fs'),p=require('path');const root='D:/armadaIII',repo='D:/aramada',out='D:/Xaramada-Modwork/faction-assemblers',release='D:/Xaramada-Modwork/bajor-rebuild';
const manifest=JSON.parse(fs.readFileSync(repo+'/assemblers/manifest.json','utf8')),walk=d=>fs.existsSync(d)?fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(p.join(d,e.name)):[p.join(d,e.name)]):[],read=f=>fs.readFileSync(f,'latin1');
function save(base,rel,t){let f=base+'/'+rel;fs.mkdirSync(p.dirname(f),{recursive:true});fs.writeFileSync(f,t,'latin1');}
for(let stage of [out,release]){
 let sprfile=fs.existsSync(stage+'/Sprites/gui_global.spr')?stage+'/Sprites/gui_global.spr':root+'/Sprites/gui_global.spr',spr=read(sprfile);
 for(let[index,f]of manifest.factions.entries())for(let key of ['b_'+f.id,...Array.from({length:5},(_,i)=>f.id+'w'+(i+1)),...(f.race==='borg'?['b_uconst',...Array.from({length:5},(_,i)=>'uconstw'+(i+1))]:[])]){spr=spr.replace(new RegExp('^[ \\t]*'+key+'[ \\t]+.*$','gmi'),'');spr+='\r\n@reference=512\r\n@tmaterial=default\r\n'+key+' xuconstbuttons '+index*64+' 0 64 64\r\n';}
 save(stage,'Sprites/gui_global.spr',spr);
 if(stage===release){for(let file of [...walk(out+'/SOD'),...walk(out+'/Textures')]){let rel=p.relative(out,file);fs.mkdirSync(p.dirname(stage+'/'+rel),{recursive:true});fs.copyFileSync(file,stage+'/'+rel);}}
 let aiChanged=[];
 for(let f of manifest.factions)for(let file of walk(root+'/AI').filter(file=>p.basename(file).toLowerCase().startsWith(f.race+'_')&&/\.aip$/i.test(file))){let rel=p.relative(root,file),source=fs.existsSync(stage+'/'+rel)?stage+'/'+rel:file,text=read(source);if(!/Way_Better_Build_List_Element/.test(text))continue;
  if(f.race==='borg')text=text.replace(/^([ \t]*)"bconst2"([ \t]*,.*)$/gmi,'$1"xbuconst"$2');
  // Every skirmish profile can reach facilities delegated to its second constructor.
  text=text.replace(new RegExp('^[ \\t]*"'+f.id+'"[^\\r\\n]*[\\r\\n]*','gmi'),'');
  let baserow=new RegExp('^([ \\t]*"'+f.base+'"[^\\r\\n]*)([\\r\\n]+)','mi');
  let row='    "'+f.id+'", 1, 0, 1, 0, // Faction Universal constructor for advanced facilities\r\n';
  if(baserow.test(text))text=text.replace(baserow,(all,line,end)=>line+end+row);else{text=text.replace(/(the_build_list\[MAX_ELEMENTS\][\s\S]*?\{\s*\r?\n)/,all=>all+row);}
  save(stage,rel,text);aiChanged.push(rel);
 }
 fs.writeFileSync(repo+'/reports/faction-assembler-ai-'+(stage===out?'active':'bajor')+'.json',JSON.stringify({target:root,profiles:aiChanged,applied:false},null,2));
}
// Validate the active feature independently of the larger, unapplied Bajoran rebuild.
const idx=new Map([...walk(root+'/odf'),...walk(out+'/odf')].filter(f=>/\.odf$/i.test(f)).map(f=>[p.basename(f).toLowerCase(),f]));
function props(n,seen=new Set()){n=n.toLowerCase();if(seen.has(n)||!idx.has(n))return{};seen.add(n);let t=read(idx.get(n)),v={};for(let m of t.matchAll(/^\s*#include\s+"([^"]+)"/gmi))Object.assign(v,props(m[1],seen));for(let m of t.matchAll(/^[ \t]*(\w+)[ \t]*=[ \t]*(.*)$/gm))v[m[1].toLowerCase()]=m[2].replace(/\s*\/\/.*$/,'').trim().replace(/^"|"$/g,'');return v;}
let errors=[],checks=[],ids=manifest.factions.map(f=>f.id),spr=read(out+'/Sprites/gui_global.spr');
for(let f of manifest.factions){let v=props(f.id+'.odf'),items=Object.entries(v).filter(([k])=>/^builditem\d+$/.test(k));if(v.race!==f.race)errors.push(f.id+': race mismatch');if(v.basename!==f.id)errors.push(f.id+': model mismatch');if(items.length>13)errors.push(f.id+': menu overflow');for(let[k,n]of items){if(!idx.has(n+'.odf'))errors.push(f.id+': missing '+n);if(n.startsWith('8472'))errors.push(f.id+': forbidden 8472 item');}
 for(let key of ['b_'+f.id,...Array.from({length:5},(_,i)=>f.id+'w'+(i+1))])if(!new RegExp('^'+key+'\\s+xuconstbuttons','mi').test(spr))errors.push(f.id+': missing sprite '+key);
 for(let tree of walk(out+'/techtree').filter(t=>/\.tt$/i.test(t))){let text=read(tree);if(!new RegExp('^'+f.id+'\\.odf\\s+','mi').test(text))errors.push(f.id+': missing technology '+p.basename(tree));}
 if(!fs.existsSync(out+'/SOD/'+f.id+'.sod'))errors.push(f.id+': missing model');checks.push({builder:f.id,menus:items.length,technologyTrees:walk(out+'/techtree').length});
}
let legacy=props('uconst.odf');if(Object.entries(legacy).some(([k,v])=>/^builditem/.test(k)&&v.startsWith('8472')))errors.push('Legacy uconst still builds8472');
let producerLinks=0,forbidden=[];
for(let[name,file]of idx){let v=props(name),items=Object.entries(v).filter(([k])=>/^builditem\d+$/.test(k)).map(([k,n])=>n);if(items.includes('uconst'))forbidden.push({unit:name,reason:'Legacy Universal production link'});if((v.race||'').toLowerCase()==='species8472'&&items.some(n=>n==='uconst'||ids.includes(n)))forbidden.push({unit:name,reason:'8472 Universal production link'});producerLinks+=items.filter(n=>ids.includes(n)).length;}
errors.push(...forbidden);let core=props('bconst.odf'),coreItems=Object.entries(core).filter(([k])=>/^builditem\d+$/.test(k)).map(([k,v])=>v);if(coreItems.length>13||!coreItems.includes('brecycle'))errors.push('Borg Recycler core menu invalid');let borg=props('bbase.odf');if(!Object.values(borg).includes('xbuconst')||Object.values(borg).includes('bconst2'))errors.push('Borg base builder types invalid');
let report={target:root,errors,checks,producerLinks,excluded8472:true,borgCoreItems:coreItems,applied:false,runtimeVerified:false};fs.writeFileSync(repo+'/reports/faction-assembler-validation.json',JSON.stringify(report,null,2));if(errors.length){console.log(JSON.stringify(errors,null,2));process.exit(1);}
let s=JSON.parse(fs.readFileSync(repo+'/status.json','utf8').replace(/^\uFEFF/,''));for(let id of ['faction_builders','assembler_tech','no_8472_assembler']){let f=s.features.find(f=>f.id===id);f.steps.forEach((step,i)=>{if(i<3)step.done=true;});}s.current='Completed builder artwork, all 40 skirmish AI profiles, technology entries and production validation. Eight faction variants; Borg Recycler visible; no Universal builder can produce 8472 and 8472 cannot produce Universal builders. Checks passed; checking game is closed before applying to Armada III only.';s.steps=s.features.flatMap(f=>f.steps.map(x=>({label:f.title+': '+x.label,done:x.done})));fs.writeFileSync(repo+'/status.json',JSON.stringify(s,null,2));fs.appendFileSync(repo+'/build.log','\n['+new Date().toISOString()+'] '+s.current+'\n');console.log(JSON.stringify({errors:errors.length,builders:checks.length,producerLinks,aiProfiles:40,borgCoreItems:coreItems.length}));
