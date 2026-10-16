const {fs,p,root,repo,walk,read,save,log}=require('./odf-lib.cjs');
const stage='D:/Xaramada-Modwork/staging',bi=stage+'/bi2files/MAINDIR',gh=stage+'/ghost/Ghosts_Comp_mod/Star Trek Armada II',up=stage+'/upgrade';
const oldTrees=new Map(walk(root+'/techtree').filter(f=>/\.tt$/i.test(f)).map(f=>[p.basename(f).toLowerCase(),read(f)]));
const originalSprites=read(root+'/Sprites/gui_global.spr'),universal=read(root+'/odf/ships/uconst.odf');
let count=0;
function copyTree(src,dest,filter=()=>true){if(!fs.existsSync(src))return;for(let f of walk(src)){let rel=p.relative(src,f);if(!filter(rel,f))continue;let out=p.join(dest,rel);fs.mkdirSync(p.dirname(out),{recursive:true});if(fs.existsSync(out))fs.chmodSync(out,0o666);fs.copyFileSync(f,out);count++;}}
for(let dir of ['textures','SOD','sounds'])copyTree(up+'/'+dir,root+'/'+dir);log('PACK: graphics textures/effects installed; original executable retained.');
for(let dir of ['odf','sod','textures','sounds','bitmaps','ai'])copyTree(bi+'/'+dir,root+'/'+dir);
log('PACK: six-race expansion assets and ODFs installed.');
for(let dir of ['odf','SOD','Textures','sounds','bitmaps'])copyTree(gh+'/'+dir,root+'/'+dir);
copyTree(gh+'/AI',root+'/AI',rel=>/^f|[/\\]f/i.test(rel));
log('PACK: Federation collection, ship models, weapons, physics and DS9 installed.');
function entries(t){let map=new Map();for(let line of t.split(/\r?\n/)){let m=line.match(/^\s*([^\s/]+\.odf)\s+(-?\d+)(?:\s|$)/i);if(m)map.set(m[1].toLowerCase(),line.trim());}return map;}
for(let [name,old]of oldTrees){let merged=entries(old);for(let source of [bi,gh]){let file=source+'/techtree/'+name;if(fs.existsSync(file))for(let [key,line]of entries(read(file)))merged.set(key,line);}let head=old.split(/\r?\n/).filter(l=>/^\s*#include/i.test(l));let text='// Xaramada merged technology tree. Source credits: Borg Incursion 2, Ghost, original installation.\r\n'+head.join('\r\n')+'\r\n'+[...merged.values()].join('\r\n')+'\r\n';save(root+'/techtree/'+name,text);}
// Sprite files retain their own @reference/material directives; add only missing entries.
function mergeSprites(base,extra){let keys=new Set(base.split(/\r?\n/).map(l=>l.trim().split(/\s+/)[0]));let context=[],added=[];for(let line of extra.split(/\r?\n/)){let s=line.trim();if(s.startsWith('@')){context=context.filter(x=>x.split('=')[0]!==s.split('=')[0]);context.push(s);}else if(s&&!/^(#|\/\/)/.test(s)){let key=s.split(/\s+/)[0];if(!keys.has(key)){added.push(...context,line);keys.add(key);}}}return base+'\r\n// Xaramada merged additions\r\n'+added.join('\r\n')+'\r\n';}
let sprite=originalSprites;for(let source of [up,bi,gh]){let dir=['sprites','Sprites'].map(x=>source+'/'+x).find(fs.existsSync);if(dir)for(let f of walk(dir)){let dest=root+'/Sprites/'+p.basename(f);if(p.basename(f).toLowerCase()==='gui_global.spr')sprite=mergeSprites(sprite,read(f));else if(!fs.existsSync(dest))save(dest,read(f));}}
save(root+'/Sprites/gui_global.spr',sprite);save(root+'/odf/ships/uconst.odf',universal);
// Preserve the installed game interfaces; pack-specific interface references are not required for ship assets.
for(let n of ['borg','fed','kling','rom','card','species8472']){let original='D:/Startrek Armada II install/Activision/Star Trek Armada II/odf/other/'+n+'.odf';if(fs.existsSync(original))save(root+'/odf/other/'+n+'.odf',read(original));}
fs.writeFileSync(repo+'/reports/pack-merge.json',JSON.stringify({filesCopied:count,packs:['Armada II Upgrade Project 2.0.0 graphics/effects','Borg Incursion 2 ship expansion','Ghost Federation ship collection'],originalExecutablePreserved:true,originalRaceInterfacesPreserved:true},null,2));
let status=JSON.parse(fs.readFileSync(repo+'/status.json','utf8').replace(/^\uFEFF/,''));status.steps[4].done=true;status.steps[5].done=true;status.current='Ship collections and DS9 installed. Reapplying custom fleet features, then adding faction heroes and Omega research.';fs.writeFileSync(repo+'/status.json',JSON.stringify(status,null,2));log('DONE: '+count+' pack files copied; technology trees merged; universal constructor retained.');
