const fs=require('fs'),p=require('path'),lib=require('./odf-lib.cjs');
const original='D:/Startrek Armada II install/Activision/Star Trek Armada II',stamp=Date.now(),reports=[];
function walk(d){return fs.readdirSync(d,{withFileTypes:true}).flatMap(x=>x.isDirectory()?walk(p.join(d,x.name)):[p.join(d,x.name)]);}
function read(f){return fs.readFileSync(f,'latin1');}
const originals=new Map(walk(original+'/odf').filter(f=>/\.odf$/i.test(f)).map(f=>[p.basename(f).toLowerCase(),f]));
const sods=new Map(fs.readdirSync(original+'/SOD').map(f=>[f.toLowerCase(),f]));
const textures=new Map(walk(original+'/Textures').map(f=>[p.basename(f).replace(/\.[^.]+$/,'').toLowerCase(),f]));
for(let root of ['D:/armadaIII']){
 let idx=new Map(walk(root+'/odf').filter(f=>/\.odf$/i.test(f)).map(f=>[p.basename(f).toLowerCase(),f]));
 function props(n,seen=new Set()){if(seen.has(n)||!idx.has(n))return {};seen.add(n);let t=read(idx.get(n)),v={};for(let m of t.matchAll(/^\s*#include\s+"([^"]+)"/gmi))Object.assign(v,props(m[1].toLowerCase(),seen));for(let m of t.matchAll(/^\s*(\w+)\s*=\s*(.*?)\s*(?:\/\/.*)?$/gm))v[m[1].toLowerCase()]=m[2].replace(/^"|"$/g,'');return v;}
 function save(rel,data){let out=root+'/'+rel,b='D:/Xaramada-Modwork/backups/projectile-station-'+stamp+'/'+p.basename(root)+'/'+rel;fs.mkdirSync(p.dirname(b),{recursive:true});if(fs.existsSync(out)){if(!fs.existsSync(b))fs.copyFileSync(out,b);fs.chmodSync(out,0o666);}fs.mkdirSync(p.dirname(out),{recursive:true});fs.writeFileSync(out,data,typeof data==='string'?'latin1':undefined);let overlay='D:/aramada/'+(root.endsWith('armadaIII')?'bajor/overlay/':'overlay/')+rel;fs.mkdirSync(p.dirname(overlay),{recursive:true});fs.copyFileSync(out,overlay);}
 let keys=new Set(),lines=new Map();for(let f of fs.readdirSync(root+'/Sprites').filter(f=>/\.spr$/i.test(f))){for(let m of read(root+'/Sprites/'+f).matchAll(/^\s*([\w.]+)\s+(\S+)\s+([-\d][^\r\n]*)/gm)){keys.add(m[1].toLowerCase());lines.set(m[1].toLowerCase(),m[2]+' '+m[3]);}}
 let missing=[];for(let [n,f]of idx){let v=props(n);if(/torpedo/i.test(v.classlabel||'')&&v.sprite&&!keys.has(v.sprite.toLowerCase()))missing.push({unit:n,sprite:v.sprite});}
 let weapon=read(root+'/Sprites/weapon.spr');let names=[...new Set(missing.map(x=>x.sprite))];
 for(let n of names){weapon+='\r\n// Recovery: missing projectile effect; use installed stock photon artwork.\r\n@reference=128\r\n@tmaterial=additive\r\n'+n+' Wphoton 0 0 32 32 @anim=tex4x4\r\n';}
 save('Sprites/weapon.spr',weapon);
 let restored=[],skipped=[];
 // Explicit base-game station names. Added shipyards, DS9, Omega and new-faction buildings are excluded.
 const stock=/^(?:[fbkrc](?:base|mining|yard|yard2|resear|resear2|upgrade|turret|turret2|sensor|orbital|trade|trading|repair|super)|8472_(?:mothership|mother|research|advancedresearch|turret|sensor))\.odf$/i;
 for(let [n,f]of idx){if(!stock.test(n)||!originals.has(n))continue;let source=originals.get(n),ot=read(source),m=ot.match(/^\s*baseName\s*=\s*"([^"]+)"/mi),model=(m?m[1]:p.basename(n,'.odf')).toLowerCase(),sod=sods.get(model+'.sod');if(!sod){skipped.push({unit:n,reason:'Original model absent'});continue;}
  let alias='xvstock_'+p.basename(n,'.odf'),buf=fs.readFileSync(original+'/SOD/'+sod),t=read(f),low=buf.toString('latin1').toLowerCase();
  // Private model aliases prevent restoring stock art from altering added buildings that share a model.
  save('SOD/'+alias+'.sod',buf);t=t.replace(/^\s*baseName\s*=.*$/gmi,'');t+='\r\nbaseName = "'+alias+'"\r\n';
  let hp=[...new Set([...ot.matchAll(/^\s*(\w*hardpoints\d*)\s*=\s*([^\r\n]+)/gmi)].map(m=>m[1].toLowerCase()))];
  for(let key of hp){let re=new RegExp('^\\s*'+key+'\\s*=.*$','gmi'),value=ot.match(new RegExp('^\\s*'+key+'\\s*=\\s*([^\\r\\n]+)','mi'))[1];t=t.replace(re,'');t+='\r\n'+key+' = '+value+'\r\n';}
  for(let [stem,tex]of textures)if(stem.length>=4&&low.includes(stem))save(p.relative(original,tex),fs.readFileSync(tex));
  save(p.relative(root,f),t);restored.push({unit:n,model:sod,privateAlias:alias});
 }
 reports.push({root,missingProjectileDefinitions:missing,addedSpriteAliases:names,restoredStations:restored,skipped,runtimeTested:false,baseline:'Original supplied installation; not certified clean vanilla'});
}
fs.writeFileSync('D:/aramada/reports/projectile-station-recovery.json',JSON.stringify(reports,null,2));
let message=reports.map(r=>r.root+': '+r.missingProjectileDefinitions.length+' missing projectile references repaired; '+r.restoredStations.length+' base-game station models restored').join('; ')+'. Shipyard III and added buildings retained. Crash retest required.';
fs.appendFileSync('D:/aramada/build.log','\n['+new Date().toISOString()+'] '+message+'\n');let status=JSON.parse(fs.readFileSync('D:/aramada/status.json','utf8').replace(/^\uFEFF/,''));status.current=message;fs.writeFileSync('D:/aramada/status.json',JSON.stringify(status,null,2));console.log(message);


