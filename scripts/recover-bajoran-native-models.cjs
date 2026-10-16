const fs=require('fs'),p=require('path'),root='D:/armadaIII',repo='D:/aramada',stamp=Date.now(),backup='D:/Xaramada-Modwork/backups/bajor-native-model-recovery-'+stamp;
const walk=d=>fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(p.join(d,e.name)):[p.join(d,e.name)]),idx=new Map(walk(root+'/odf').filter(f=>/\.odf$/i.test(f)).map(f=>[p.basename(f).toLowerCase(),f])),read=f=>fs.readFileSync(f,'latin1');
function props(n,seen=new Set()){if(!idx.has(n)||seen.has(n))return{};seen.add(n);let t=read(idx.get(n)),v={};for(let m of t.matchAll(/^\s*#include\s+"([^"]+)"/gmi))Object.assign(v,props(m[1].toLowerCase(),seen));for(let m of t.matchAll(/^[ \t]*(\w+)[ \t]*=[ \t]*(.*)$/gm))v[m[1].toLowerCase()]=m[2].trim().replace(/^"|"$/g,'');return v;}
const set=(t,k,v)=>t.replace(new RegExp('^[ \\t]*'+k+'[ \\t]*=.*$','gmi'),'').trimEnd()+'\r\n'+k+' = '+v+'\r\n';
let m=JSON.parse(fs.readFileSync(repo+'/bajor/rebuild-manifest.json','utf8').replace(/^\uFEFF/,'')),changes=[];
for(let u of [...m.units,{odf:'xbjuconst',parent:'fconst',folder:'ships'}]){
 if(u.odf==='bjbase')continue;
 let native=props(u.parent+'.odf'),model=native.basename||u.parent;if(!fs.existsSync(root+'/SOD/'+model+'.sod'))throw Error('Compatible model absent '+model);
 let rel='odf/'+u.folder+'/'+u.odf+'.odf',file=root+'/'+rel,before=read(file),t=set(before,'baseName','"'+model+'"');
 t=set(t,'ScaleSOD',native.scalesod||'1.0');
 // Proxies use the source unit's hardpoint layout; retain weapon/stat definitions.
 for(let[k,v]of Object.entries(native))if(k.includes('hardpoint')&&v.trim())t=set(t,k,v.startsWith('"')?v:'"'+v+'"');
 // Values containing multiple quoted hardpoints were already parsed with only outer quotes removed.
 for(let[k,v]of Object.entries(native))if(k.includes('hardpoint')&&v.trim()){let normalized='"'+v.replace(/^"|"$/g,'')+'"';t=set(t,k,normalized);}
 let normalize=x=>x.replace(/^[ \t]*(?:baseName|ScaleSOD|\w*hardpoints?\d*)[ \t]*=.*$/gmi,'').replace(/\s+/g,'');
 if(normalize(before)!==normalize(t))throw Error('Non-visual property changed '+u.odf);
 let bak=backup+'/'+rel;fs.mkdirSync(p.dirname(bak),{recursive:true});fs.copyFileSync(file,bak);fs.chmodSync(file,0o666);fs.writeFileSync(file,t,'latin1');let over=repo+'/bajor/overlay/'+rel;fs.mkdirSync(p.dirname(over),{recursive:true});fs.writeFileSync(over,t,'latin1');changes.push({unit:u.odf,model,scale:native.scalesod||'1.0',rel});
}
let report={target:root,backup,changes,scope:'Only model, scale and attachment references changed; no fleet/tech/AI/cost rollback. DS9 retains its existing model.',hypothesis:'New Bajoran SOD assets are suspected from repeated load crashes when Bajor is included; native proxies isolate that hypothesis.',customAssetsPreservedIn:'D:/Xaramada-Modwork/bajor-rebuild',runtimeVerified:false};fs.writeFileSync(repo+'/reports/bajor-native-model-recovery.json',JSON.stringify(report,null,2));
let s=JSON.parse(fs.readFileSync(repo+'/status.json','utf8').replace(/^\uFEFF/,''));s.current='Crash recovery applied in D:/armadaIII: swapped 53 Bajoran ship/building/builder visual definitions to existing game models, keeping DS9, the full roster, costs, tech and AI. Custom SOD assets preserved in staging. Latest crash repeats c0000005 at 000d162c during a match including Bajor; cause is still being isolated. Fresh-match test required before calling the crash fixed.';let f=s.features.find(f=>f.id==='bajor_models');if(f)f.steps.forEach((x,i)=>{if(i>=3)x.done=false;});s.steps=s.features.flatMap(f=>f.steps.map(x=>({label:f.title+': '+x.label,done:x.done})));fs.writeFileSync(repo+'/status.json',JSON.stringify(s,null,2));fs.appendFileSync(repo+'/build.log','\n['+new Date().toISOString()+'] '+s.current+'\n');console.log(JSON.stringify({changed:changes.length,backup,costAndGameplayDefinitionsPreserved:true}));
