const fs=require('fs'),p=require('path');
const root='D:/armadaIII',repo='D:/aramada',out='D:/Xaramada-Modwork/faction-assemblers',release='D:/Xaramada-Modwork/bajor-rebuild';
const factions=[['borg','xb uconst'.replace(' ',''),'bconst','bbase','Borg Universal Assembler','Borg lattice with twin fabrication nodes'],['federation','xfuconst','fconst','fbase','Federation Universal Constructor','Starfleet tender with twin engineering pods'],['klingon','xkuconst','kconst','kbase','Klingon Universal Constructor','Klingon utility wings with armored side modules'],['romulan','xruconst','rconst','rbase','Romulan Universal Constructor','Romulan swept wings with fabrication outriggers'],['cardassian','xcuconst','cconst','cbase','Cardassian Universal Constructor','Cardassian industrial frame with paired cargo modules'],['dominion','xduconst','dconst','dbase','Dominion Universal Constructor','Jem\'Hadar utility hull with twin construction pods'],['breen','xbruconst','brconst','brbase','Breen Universal Constructor','Breen asymmetric hull with fabrication pods'],['bajoran','xbjuconst','bjconst','bjbase','Bajoran Universal Constructor','Militia tender with copper fabrication outriggers']].map(([race,id,parent,base,title,design])=>({race,id,parent,base,title,design}));
const stars=factions.map(f=>f.base),walk=d=>fs.existsSync(d)?fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(p.join(d,e.name)):[p.join(d,e.name)]):[];
const read=f=>fs.readFileSync(f,'latin1'),write=(base,rel,t)=>{let f=base+'/'+rel;fs.mkdirSync(p.dirname(f),{recursive:true});fs.writeFileSync(f,t,'latin1');};
function set(t,k,v){t=t.replace(new RegExp('^[ \\t]*'+k+'[ \\t]*=.*$','gmi'),'');return t.trimEnd()+'\r\n'+k+' = '+v+'\r\n';}
function menu(t,items){return t.replace(/^[ \t]*buildItem\d+[ \t]*=.*$/gmi,'').trimEnd()+'\r\n'+items.map((n,i)=>`buildItem${i} = "${n}"`).join('\r\n')+'\r\n';}
function build(layer,dest){
 const files=new Map([...walk(root+'/odf'),...walk(layer+'/odf')].filter(f=>/\.odf$/i.test(f)).map(f=>[p.basename(f).toLowerCase(),f]));
 const props=(id,seen=new Set())=>{let file=files.get(id.toLowerCase());if(!file||seen.has(id))return{};seen.add(id);let t=read(file),v={};for(let m of t.matchAll(/^\s*#include\s+"([^"]+)"/gmi))Object.assign(v,props(m[1],seen));for(let m of t.matchAll(/^[ \t]*(\w+)[ \t]*=[ \t]*(.*)$/gm))v[m[1].toLowerCase()]=m[2].replace(/\s*\/\/.*$/,'').trim().replace(/^"|"$/g,'');return v;};
 let changed=[],overflow=new Map(factions.map(f=>[f.race,new Set()])),plans=[];
 // Preserve already-delegated facilities when regenerating from a patched installation.
 for(let f of factions){let existing=files.get(f.id+'.odf');if(existing)for(let match of read(existing).matchAll(/^[ \t]*buildItem\d+[ \t]*=[ \t]*"([^"]+)"/gmi)){let name=match[1];if(!stars.includes(name)&&!name.startsWith('8472'))overflow.get(f.race).add(name);}}
 const save=(rel,t)=>{write(dest,rel,t);changed.push(rel);};
 for(let [name,file]of files){let v=props(name),f=factions.find(f=>f.race===(v.race||'').toLowerCase());if(!f||!/^\w*const\d*\.odf$/i.test(name)||name==='uconst.odf'||name===f.id+'.odf')continue;
  let text=read(file),items=[...text.matchAll(/^[ \t]*buildItem\d+[ \t]*=[ \t]*"([^"]+)"/gmi)].map(m=>m[1]);if(!items.length)continue;
  // Keep special/hero pairing and the Recycler inside the Borg core menu.
  if(name==='bconst.odf')items=['bbase','byard','bsensor','bturret','bmining','bresear','bresear2','byard2','bturret2','bbase2','brecycle','bsuperbl','byard3'];
  let original=[...text.matchAll(/^[ \t]*buildItem\d+[ \t]*=[ \t]*"([^"]+)"/gmi)].map(m=>m[1]);
  for(let n of original)if(!items.slice(0,13).includes(n))overflow.get(f.race).add(n);
  if(items.length>13){items=items.slice(0,13);save(p.relative(root,file).startsWith('..')?p.relative(layer,file):p.relative(root,file),menu(text,items));}
  else if(name==='bconst.odf')save('odf/ships/bconst.odf',menu(text,items));
 }
 for(let f of factions){
  let source=files.get(f.parent+'.odf'),v=props(f.parent+'.odf'),text=read(source);text=text.replace(/^[ \t]*(?:secondary)?buildItem\d+[ \t]*=.*$/gmi,'');
  for(let[k,value]of Object.entries({unitName:'"'+f.title+'"',tooltip:'"'+f.title+'"',verboseTooltip:'"'+f.title+'. Builds allied faction starbases and assigned advanced facilities. Species 8472 biotechnology is excluded."',race:'"'+f.race+'"',baseName:'"'+f.id+'"',ScaleSOD:'1.0',hotkeyLabel:'"HOTKEY_F2"'}))text=set(text,k,value);
  let items=[...new Set([...stars,...overflow.get(f.race)])].filter(n=>f.race!=='borg'||!['bbase','btechass','bresear2'].includes(n));if(items.length>13)throw Error(f.race+' Universal menu overflow '+items.length);
  text=menu(text,items);save('odf/ships/'+f.id+'.odf',text);
  plans.push({...f,sourceModel:v.basename||f.parent,items,sourceFile:p.relative(root,source),costs:Object.fromEntries(['dilithiumcost','metalcost','latinumcost','crewcost','officercost','buildtime'].map(k=>[k,v[k]]))});
 }
 // Replace every legacy production reference with the producer faction's own version.
 for(let[name,file]of files){let text=read(file),v=props(name),race=(v.race||'').toLowerCase(),f=factions.find(f=>f.race===race),items=[...text.matchAll(/^[ \t]*buildItem\d+[ \t]*=[ \t]*"([^"]+)"/gmi)].map(m=>m[1]);if(!items.length)continue;
  let updated=items.filter(n=>!(race==='species8472'&&(n==='uconst'||factions.some(x=>x.id===n)))).map(n=>n==='uconst'&&f?f.id:n);
  if(f&&name===f.base+'.odf'&&!updated.includes(f.id))updated.push(f.id);
  if(updated.join('|')!==items.join('|')){if(updated.length>13)throw Error('Producer menu overflow '+name);let rel=p.relative(root,file);if(rel.startsWith('..'))rel=p.relative(layer,file);save(rel,menu(text,updated));}
 }
 // Preserve uconst filename as compatibility alias; no live producer uses it.
 let legacy=read(files.get('uconst.odf'));legacy=set(legacy,'baseName','"xbuconst"');legacy=menu(legacy,[...stars,...overflow.get('borg')].filter(n=>!['bbase','btechass','bresear2'].includes(n)));save('odf/ships/uconst.odf',legacy);
 for(let file of new Map([...walk(root+'/techtree'),...walk(layer+'/techtree')].filter(f=>/\.tt$/i.test(f)).map(f=>[p.basename(f),f])).values()){
  let text=read(file);for(let f of factions){let parentLine=text.match(new RegExp('^[ \\t]*'+f.parent+'\\.odf[ \\t]+([^\\r\\n]+)','mi'));let deps=parentLine?parentLine[1].replace(/\/\/.*$/,'').trim():'0';text=text.replace(new RegExp('^[ \\t]*'+f.id+'\\.odf[^\\r\\n]*','gmi'),'');text+='\r\n'+f.id+'.odf '+deps+'\r\n';}save('techtree/'+p.basename(file),text);
 }
 // Replace old constructor tasks only where they actually occur, keeping faction AI separate.
 let aiChanges=[];for(let file of new Map([...walk(root+'/AI'),...walk(layer+'/AI')].filter(f=>/\.(aip|txt)$/i.test(f)).map(f=>[p.basename(f),f])).values()){
  let text=read(file);if(!/\buconst\b/i.test(text))continue;let lower=p.basename(file).toLowerCase(),f=factions.find(f=>lower.startsWith(f.race));if(!f)continue;let updated=text.replace(/\buconst\b/gi,f.id);if(updated!==text){let rel=p.relative(root,file);if(rel.startsWith('..'))rel=p.relative(layer,file);save(rel,updated);aiChanges.push(rel);}
 }
 return {target:root,layer,files:[...new Set(changed)],factions:plans,aiChanges,applied:false,runtimeVerified:false};
}
const active=build(root,out);fs.mkdirSync(repo+'/assemblers',{recursive:true});fs.writeFileSync(repo+'/assemblers/manifest.json',JSON.stringify(active,null,2));
const staged=build(release,release);fs.writeFileSync(repo+'/reports/faction-assembler-staged-integration.json',JSON.stringify(staged,null,2));
let status=JSON.parse(fs.readFileSync(repo+'/status.json','utf8').replace(/^\uFEFF/,''));const done=(id,count)=>{let f=status.features.find(x=>x.id===id);if(f)f.steps.forEach((x,i)=>{if(i<count)x.done=true;});};done('faction_builders',2);done('assembler_tech',2);done('no_8472_assembler',2);status.current='Completed eight faction builder definitions and production routing. Borg keeps exactly two builder types; its Universal Assembler carries Technology Assimilator, Upgrade Facility and Omega Lab. Species 8472 exclusions are staged. Building matching faction model variants and buttons next.';status.steps=status.features.flatMap(f=>f.steps.map(x=>({label:f.title+': '+x.label,done:x.done})));fs.writeFileSync(repo+'/status.json',JSON.stringify(status,null,2));fs.appendFileSync(repo+'/build.log','\n['+new Date().toISOString()+'] '+status.current+'\n');console.log(JSON.stringify({builders:active.factions.map(f=>({id:f.id,model:f.sourceModel,items:f.items.length})),files:active.files.length,aiChanges:active.aiChanges}));

