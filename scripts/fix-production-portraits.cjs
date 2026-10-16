const fs=require('fs'),p=require('path'),stamp=Date.now(),reports=[];
const walk=d=>fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(p.join(d,e.name)):[p.join(d,e.name)]),read=f=>fs.readFileSync(f,'latin1');
for(let root of ['D:/armadaIII']){
 let idx=new Map(walk(root+'/odf').filter(f=>/\.odf$/i.test(f)).map(f=>[p.basename(f).toLowerCase(),f]));
 function props(n,seen=new Set()){if(!idx.has(n)||seen.has(n))return {};seen.add(n);let t=read(idx.get(n)),v={};for(let m of t.matchAll(/^\s*#include\s+"([^"]+)"/gmi))Object.assign(v,props(m[1].toLowerCase(),seen));for(let m of t.matchAll(/^\s*(\w+)\s*=\s*(.*?)\s*(?:\/\/.*)?$/gm))v[m[1].toLowerCase()]=m[2].replace(/^"|"$/g,'');return v;}
 let targets=new Set();for(let f of idx.values())for(let m of read(f).matchAll(/^\s*(?:secondary)?buildItem\d+\s*=\s*"([^"]+)"/gmi))targets.add(m[1].toLowerCase().replace(/\.odf$/,'')+'.odf');
 let file=root+'/Sprites/gui_global.spr',spr=read(file),entries=new Map(),ref=256,mat='default',tex=new Set(walk(root+'/Textures').map(f=>p.basename(f).toLowerCase()));
 for(let l of spr.split(/\r?\n/)){let r=l.match(/^\s*@reference=(\S+)/),m=l.match(/^\s*@tmaterial=(\S+)/);if(r)ref=r[1];if(m)mat=m[1];let e=l.match(/^\s*([\w.]+)\s+(\S+)\s+([-\d].*)$/);if(e)entries.set(e[1].toLowerCase(),{texture:e[2],tail:e[3],ref,mat});}
 const valid=e=>e&&tex.has(e.texture.toLowerCase()+'.tga');let changes=[],fallbacks=[],checked=[],errors=[];
 function put(key,e,unit){spr=spr.replace(new RegExp('^\\s*'+key+'\\s+.*$','gmi'),'');spr+='\r\n@reference='+e.ref+'\r\n@tmaterial='+e.mat+'\r\n'+key+' '+e.texture+' '+e.tail+'\r\n';entries.set(key,e);changes.push({unit,key,texture:e.texture});}
 for(let n of targets){if(!idx.has(n))continue;let v=props(n),name=p.basename(n,'.odf'),model=(v.basename||name).toLowerCase(),names=[...new Set([name,model])],icon=names.map(x=>entries.get('b_'+x)).find(valid);if(!valid(icon)){errors.push({unit:n,error:'No valid build-button source'});continue;}
  let ancestors=[...read(idx.get(n)).matchAll(/^\s*#include\s+"([^"]+)"/gmi)].map(m=>p.basename(m[1],'.odf').toLowerCase());
  for(let alias of names){if(!valid(entries.get('b_'+alias)))put('b_'+alias,icon,n);for(let i=1;i<=5;i++){let key=alias+'w'+i;if(valid(entries.get(key)))continue;let source=[...names,...ancestors].map(x=>entries.get(x+'w'+i)).find(valid);if(!valid(source)){source={...icon,mat:'default'};fallbacks.push({unit:n,key,source:'matching build icon'});}put(key,source,n);}}
  checked.push(n);
 }
 let backup='D:/Xaramada-Modwork/backups/production-portraits-'+stamp+'/'+p.basename(root)+'.spr';fs.mkdirSync(p.dirname(backup),{recursive:true});fs.copyFileSync(file,backup);fs.chmodSync(file,0o666);fs.writeFileSync(file,spr,'latin1');let out='D:/aramada/'+(root.endsWith('armadaIII')?'bajor/overlay/':'overlay/')+'Sprites/gui_global.spr';fs.writeFileSync(out,spr,'latin1');
 for(let n of checked){let v=props(n);for(let name of new Set([p.basename(n,'.odf'),(v.basename||p.basename(n,'.odf')).toLowerCase()]))for(let i=1;i<=5;i++)if(!valid(entries.get(name+'w'+i)))errors.push({unit:n,key:name+'w'+i});}
 reports.push({root,checked:checked.length,changes,fallbacks,errors,runtimeVerified:false});
}
fs.writeFileSync('D:/aramada/reports/production-portraits.json',JSON.stringify(reports,null,2));let message=reports.map(r=>r.root+': '+r.checked+' buildable units checked, '+r.changes.length+' production/wireframe sprite links added, '+r.errors.length+' unresolved').join('; ')+'. Original wireframes reused where present; matching build-icon artwork fills absent wireframes. Restart game to reload; production queue visual test pending.';let s=JSON.parse(fs.readFileSync('D:/aramada/status.json','utf8').replace(/^\uFEFF/,''));s.current=message;fs.writeFileSync('D:/aramada/status.json',JSON.stringify(s,null,2));fs.appendFileSync('D:/aramada/build.log','\n['+new Date().toISOString()+'] '+message+'\n');console.log(message);

