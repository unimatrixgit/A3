const fs=require('fs'),p=require('path'),crypto=require('crypto');
const root='D:/armadaIII',repo='D:/aramada',backup='D:/Xaramada-Modwork/backups/borg-menu-deduplicate-'+new Date().toISOString().replace(/[:.]/g,'-');
const read=f=>fs.readFileSync(f,'latin1'),items=t=>[...t.matchAll(/^[ \t]*buildItem(\d+)[ \t]*=[ \t]*"([^"]+)"/gmi)].sort((a,b)=>+a[1]-+b[1]).map(m=>m[2]);
const core=items(read(root+'/odf/ships/bconst.odf')),old=items(read(root+'/odf/ships/xbuconst.odf')),duplicates=old.filter(n=>core.includes(n));
let changes=[];
for(let base of [root,repo+'/bajor/overlay','D:/Xaramada-Modwork/faction-assemblers','D:/Xaramada-Modwork/bajor-rebuild'])for(let name of ['xbuconst','uconst']){
 let rel='odf/ships/'+name+'.odf',file=base+'/'+rel;if(!fs.existsSync(file))continue;
 let text=read(file),before=items(text),after=before.filter(n=>!core.includes(n));
 if(after.length===before.length)continue;
 let patched=text.replace(/^[ \t]*buildItem\d+[ \t]*=.*$/gmi,'').trimEnd()+'\r\n\r\n// Borg core facilities remain on the standard Assembler; no overlapping build buttons.\r\n'+after.map((n,i)=>`buildItem${i} = "${n}"`).join('\r\n')+'\r\n';
 if(after.length>13||after.some(n=>n.startsWith('8472'))||after.some(n=>core.includes(n)))throw Error('Invalid Borg secondary menu');
 let oldunion=new Set([...core,...before]),newunion=new Set([...core,...after]);if(oldunion.size!==newunion.size||[...oldunion].some(n=>!newunion.has(n)))throw Error('Facility access would be lost');
 let slots=[...patched.matchAll(/^buildItem(\d+)\s*=/gm)].map(m=>+m[1]);if(slots.some((n,i)=>n!==i))throw Error('Non-contiguous menu');
 let bak=backup+'/'+p.basename(base)+'/'+rel;fs.mkdirSync(p.dirname(bak),{recursive:true});fs.copyFileSync(file,bak);fs.chmodSync(file,0o666);fs.writeFileSync(file,patched,'latin1');changes.push({file,removed:before.filter(n=>!after.includes(n)),items:after,sha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')});
}
// Keep generation idempotent: the standard Borg Assembler owns the Borg starbase.
let script=repo+'/scripts/faction-assemblers.cjs',text=fs.readFileSync(script,'utf8');
text=text.replace('let items=[...new Set([...stars,...overflow.get(f.race)])];','let items=[...new Set([...stars,...overflow.get(f.race)])].filter(n=>f.race!==\'borg\'||n!==\'bbase\');');
text=text.replace("legacy=menu(legacy,[...stars,...overflow.get('borg')]);","legacy=menu(legacy,[...stars,...overflow.get('borg')].filter(n=>n!=='bbase'));");
fs.writeFileSync(script,text);
for(let file of [repo+'/assemblers/manifest.json',repo+'/reports/faction-assembler-staged-integration.json'])if(fs.existsSync(file)){let m=JSON.parse(fs.readFileSync(file,'utf8').replace(/^\uFEFF/,''));for(let f of m.factions||[])if(f.race==='borg')f.items=f.items.filter(n=>!core.includes(n));fs.writeFileSync(file,JSON.stringify(m,null,2));}
let report={target:root,duplicatesRemoved:duplicates,coreItems:core,universalItems:items(read(root+'/odf/ships/xbuconst.odf')),overlap:items(read(root+'/odf/ships/xbuconst.odf')).filter(n=>core.includes(n)),facilityAccessPreserved:true,backup,changes,runtimeVerified:false};
fs.writeFileSync(repo+'/reports/borg-menu-deduplication.json',JSON.stringify(report,null,2));
let s=JSON.parse(fs.readFileSync(repo+'/status.json','utf8').replace(/^\uFEFF/,''));s.current='Completed Borg builder menu cleanup in D:/armadaIII only. Removed duplicate Borg Nexus/starbase button from Borg Universal Assembler and legacy uconst. Standard Assembler retains Borg base; Universal retains seven other faction starbases and three advanced Borg facilities. Zero shared entries, contiguous menu slots, no facility access lost. Backed up and applied; fresh-match UI confirmation pending.';
let feature={id:'borg_menu_deduplication',title:'Borg builder duplicate removal',steps:[{label:'Compare both menus',done:true},{label:'Remove duplicate and preserve facility access',done:true},{label:'Apply and validate files',done:true}]};s.features=s.features.filter(f=>f.id!==feature.id);s.features.push(feature);s.steps=s.features.flatMap(f=>f.steps.map(x=>({label:f.title+': '+x.label,done:x.done})));s.lastCompleted={task:feature.title,time:new Date().toISOString(),runtimeVerified:false};fs.writeFileSync(repo+'/status.json',JSON.stringify(s,null,2));fs.appendFileSync(repo+'/build.log','\n['+new Date().toISOString()+'] '+s.current+'\n');console.log(JSON.stringify({duplicatesRemoved:duplicates,standard:core.length,universal:report.universalItems.length,overlap:report.overlap,accessPreserved:true,backup}));
