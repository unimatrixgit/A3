const l=require('./odf-lib.cjs'),crypto=require('node:crypto'),cp=require('node:child_process');
const reportPath=l.repo+'/reports/pending-game-patch-staged.json',r=JSON.parse(l.fs.readFileSync(reportPath,'utf8'));
if(r.applied)throw Error('Already applied; preserve original backup');
const running=cp.execFileSync('powershell',['-NoProfile','-Command','@(Get-Process armada2 -ErrorAction SilentlyContinue).Count'],{encoding:'utf8'}).trim();if(running!=='0')throw Error('Armada II must be closed');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex'),byRel=new Map(r.files.map(x=>[x.relativePath,x])),index=new Map(l.index),cache=new Map();
for(const x of r.files){
 if(l.p.isAbsolute(x.relativePath)||x.relativePath.split('/').includes('..'))throw Error('Invalid path');
 const live=l.root+'/'+x.relativePath,src=l.p.join(r.stage,x.relativePath);
 if((l.fs.existsSync(live)?hash(l.fs.readFileSync(live)):null)!==x.liveSHA256)throw Error('Live file changed: '+x.relativePath);
 if(hash(l.fs.readFileSync(src))!==x.stagedSHA256)throw Error('Stage hash changed: '+x.relativePath);
 if(/\.odf$/i.test(src))index.set(l.p.basename(src).toLowerCase(),live);
}
function text(rel){return l.read(l.p.join(byRel.has(rel)?r.stage:l.root,rel));}
function props(id,seen=new Set()){
 id=id.toLowerCase().replace(/\.odf$/,'')+'.odf';if(cache.has(id))return cache.get(id);if(seen.has(id)||!index.has(id))return{};seen=new Set(seen);seen.add(id);
 const file=index.get(id),rel=l.p.relative(l.root,file).replaceAll('\\','/'),s=text(rel),d={};
 for(const m of s.matchAll(/^\s*#include\s+"([^"]+)"/gmi))Object.assign(d,props(m[1],seen));
 for(const m of s.matchAll(/^\s*([a-z][a-z0-9_]*)\s*=\s*([^\r\n]*)/gmi))d[m[1].toLowerCase()]=m[2].split('//')[0].trim().replace(/^"|"$/g,'');
 cache.set(id,d);return d;
}
const errors=[],check=(v,m)=>{if(!v)errors.push(m);},sprite=text('Sprites/gui_global.spr');
const baseReport=JSON.parse(l.fs.readFileSync(l.repo+'/reports/basic-constructor-starbases-staged.json','utf8'));
for(const c of baseReport.changes){const d=props(c.unit);check(Object.entries(d).some(([k,v])=>/^builditem\d+$/.test(k)&&v===c.starbase),'Missing Basic starbase '+c.unit);}
for(const c of r.changes){const d=props(c.unit);check(+d.crewcost===c.newCrew&&+d.maximumcrew===c.newMaximumCrew,'Cube crew mismatch '+c.unit);}
const producers=new Map();
for(const[n]of index){const d=props(n);let count=0;for(const[k,v]of Object.entries(d))if(/^(secondary)?builditem\d+$/.test(k)){check(v!=='xu3bor2','Retired producer option '+n);if(!producers.has(v.toLowerCase()))producers.set(v.toLowerCase(),new Set());producers.get(v.toLowerCase()).add(n.slice(0,-4));if(/^builditem\d+$/.test(k))count++;}if(d.classlabel==='constructionrig'||d.classlabel==='evolver')check(count<=14,'Menu overflow '+n);}
const target=props('bconst2');for(const n of ['hub','xbgmerc','unicomplex'])check(Object.values(target).includes(n),'Missing Advanced option '+n);
for(const c of r.constructorConversions){
 const source=props(c.source),w=props(c.ability),to=props(c.target);check(w.classlabel==='fusingweapon'&&w.special==='1','Wrong conversion class '+c.ability);check(w.fusedclass===c.target&&w.multireqclass0===c.source&&w.multireqmin0==='1','Wrong conversion route '+c.ability);check(w.fusingmetalcost==='0','Conversion cost '+c.ability);check(source.is_starbase!=='1','Unsafe fusion source '+c.source);check(to.race===source.race,'Wrong target faction '+c.source);check(new RegExp('^b_'+c.ability+'\\s','mi').test(sprite),'Missing upgrade icon '+c.ability);
 const weapons=Object.entries(source).filter(([k])=>/^weapon\d+$/.test(k));const fusion=weapons.filter(([,v])=>props(v).classlabel==='fusingweapon');check(fusion.length===1,'Duplicate fusion buttons '+c.source);
 const slots=weapons.map(([,v])=>props(v)).filter(d=>d.special==='1'&&+d.buttonslot>0).map(d=>d.buttonslot);check(new Set(slots).size===slots.length,'Button slot collision '+c.source);
 const before=l.properties(l.index.get(c.source+'.odf'));for(const k of ['maxspecialenergy','specialenergyrate'])check(source[k]===before[k],'Energy changed '+c.source);
 for(const[k,v]of Object.entries(before))if(/^weapon(?:hardpoints)?\d+$/.test(k))check(source[k]===v,'Existing weapon changed '+c.source);
}
const trees={};for(const name of ['tech1','earlytech','fulltech','nosci','nospweap','nosuper']){
 const tt=new Map();for(const line of text('techtree/'+name+'.tt').split(/\r?\n/)){const a=line.split('//')[0].trim().split(/\s+/);if(a.length>1&&/\.odf$/i.test(a[0]))tt.set(a[0].toLowerCase().slice(0,-4),+a[1]<0?null:a.slice(2,2+ +a[1]).map(v=>v.toLowerCase().slice(0,-4)));}
 for(const c of r.constructorConversions)check(tt.has(c.ability)&&tt.get(c.ability)?.length===0,'Conversion locked '+name+' '+c.ability);check(tt.has('xu3bor2')&&tt.get('xu3bor2')===null,'Specialist still unlocked '+name);trees[name]=tt;
}
const aiReport=JSON.parse(l.fs.readFileSync(l.repo+'/reports/ai-start-recovery.json','utf8')),cfg={federation:'fed',klingon:'kling',romulan:'rom',cardassian:'card'};
for(const p of aiReport.profiles){const start=props(cfg[p.race]||p.race),seen=new Set(Object.entries(start).filter(([k])=>/^standardunits\d+$/.test(k)).map(([,v])=>v.toLowerCase().replace(/\.odf$/,'')));const seq=[...text('AI/AIPs/'+p.file).matchAll(/^\s*"([^"]+)"\s*,/gm)].map(m=>m[1].toLowerCase());check(seq.length<=200,'AI overflow '+p.file);for(const n of seq){check(n!=='xu3bor2','Retired AI goal '+p.file);if(!seen.has(n)){const deps=trees.tech1.get(n);check(Array.isArray(deps)&&deps.every(v=>seen.has(v)),p.file+' missing prerequisites '+n);check([...(producers.get(n)||[])].some(v=>seen.has(v)),p.file+' missing producer '+n);}seen.add(n);}}
const validation={errors,constructorButtons:r.constructorConversions.length,cubes:r.changes.length,aiPlans:aiReport.profiles.length,files:r.files.length,startingFleetsUnchanged:true,runtimeVerified:false};
l.fs.writeFileSync(l.repo+'/reports/pending-constructor-cube-validation.json',JSON.stringify(validation,null,2));if(errors.length)throw Error(JSON.stringify(errors));
const configs=['fed','borg','kling','rom','card','dominion','breen','bajoran','species8472'].map(n=>l.index.get(n+'.odf')),startHashes=configs.map(f=>[f,hash(l.fs.readFileSync(f))]);
const backup='D:/Xaramada-Modwork/backups/constructor-cube-upgrades-'+new Date().toISOString().replace(/[:.]/g,'-'),saved=[];
for(const x of r.files)for(const[label,base]of[['live',l.root],['repository',l.repo+'/bajor/overlay']]){const dst=l.p.join(base,x.relativePath),old=l.p.join(backup,label,x.relativePath),exists=l.fs.existsSync(dst);if(exists){l.fs.mkdirSync(l.p.dirname(old),{recursive:true});l.fs.copyFileSync(dst,old);}saved.push({dst,old,exists});}
try{for(const x of r.files){const data=l.fs.readFileSync(l.p.join(r.stage,x.relativePath));for(const base of[l.root,l.repo+'/bajor/overlay']){const dst=l.p.join(base,x.relativePath);l.fs.mkdirSync(l.p.dirname(dst),{recursive:true});if(l.fs.existsSync(dst))l.fs.chmodSync(dst,0o666);l.fs.writeFileSync(dst,data);check(hash(l.fs.readFileSync(dst))===x.stagedSHA256,'Copy mismatch '+dst);}}if(errors.length)throw Error(JSON.stringify(errors));}catch(e){for(const x of saved)if(x.exists)l.fs.copyFileSync(x.old,x.dst);else if(l.fs.existsSync(x.dst))l.fs.unlinkSync(x.dst);throw e;}
for(const[f,h]of startHashes)if(hash(l.fs.readFileSync(f))!==h)throw Error('Starting fleets changed');
r.applied=true;r.status='applied to armadaIII';r.appliedAt=new Date().toISOString();r.backup=backup;r.runtimeVerified=false;l.fs.writeFileSync(reportPath,JSON.stringify(r,null,2));
const s=JSON.parse(l.fs.readFileSync(l.repo+'/status.json','utf8'));s.current='APPLIED: own starbases on Basic Constructors; Borg Specialist removed, its3 buildings moved to Advanced Constructor; +35% starting/max crew on18 Borg cubes;20 free T1-to-T2/T2-to-T3 upgrade buttons using native NX conversion. No downgrade buttons; Breen/Ferengi single constructors unchanged.45 AI plans pass dependency checks. Restored working starting fleets unchanged; in-game upgrade test pending.';s.updated=r.appliedAt;l.fs.writeFileSync(l.repo+'/status.json',JSON.stringify(s,null,2));l.fs.appendFileSync(l.repo+'/build.log','\n['+r.appliedAt+'] '+s.current+' Backup:'+backup+'\n');
console.log(JSON.stringify({appliedFiles:r.files.length,upgradeButtons:r.constructorConversions.length,crewChanges:r.changes.length,aiPlansChecked:aiReport.profiles.length,backup,startingFleetsChanged:false},null,2));
