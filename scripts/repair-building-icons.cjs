const fs=require('fs'),p=require('path'),stamp=Date.now();
const walk=d=>fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(p.join(d,e.name)):[p.join(d,e.name)]);
const read=f=>fs.readFileSync(f,'latin1');let reports=[];
for(let root of ['D:/armadaIII']){
 let idx=new Map(walk(root+'/odf').filter(f=>/\.odf$/i.test(f)).map(f=>[p.basename(f).toLowerCase(),f]));
 function props(n,seen=new Set()){if(seen.has(n)||!idx.has(n))return {};seen.add(n);let t=read(idx.get(n)),v={};for(let m of t.matchAll(/^\s*#include\s+"([^"]+)"/gmi))Object.assign(v,props(m[1].toLowerCase(),seen));for(let m of t.matchAll(/^\s*(\w+)\s*=\s*(.*?)\s*(?:\/\/.*)?$/gm))v[m[1].toLowerCase()]=m[2].replace(/^"|"$/g,'');return v;}
 let file=root+'/Sprites/gui_global.spr',spr=read(file),entries=new Map(),ref=256,mat='default',textures=new Set(walk(root+'/Textures').map(f=>p.basename(f).toLowerCase()));
 for(let l of spr.split(/\r?\n/)){let r=l.match(/^\s*@reference=(\S+)/),m=l.match(/^\s*@tmaterial=(\S+)/);if(r)ref=r[1];if(m)mat=m[1];let e=l.match(/^\s*([\w.]+)\s+(\S+)\s+([-\d].*)$/);if(e)entries.set(e[1].toLowerCase(),{texture:e[2],tail:e[3],ref,mat});}
 const valid=e=>e&&textures.has(e.texture.toLowerCase()+'.tga');let repairs=[],fallbacks=[],checked=[],unresolved=[];
 function add(key,e,unit){if(!valid(e))return false;spr=spr.replace(new RegExp('^\\s*'+key+'\\s+.*$','gmi'),'');spr+='\r\n@reference='+e.ref+'\r\n@tmaterial='+e.mat+'\r\n'+key+' '+e.texture+' '+e.tail+'\r\n';entries.set(key.toLowerCase(),e);repairs.push({unit,key,texture:e.texture});return true;}
 let menus=new Set();for(let f of idx.values())for(let m of read(f).matchAll(/^\s*(?:secondary)?buildItem\d+\s*=\s*"([^"]+)"/gmi))menus.add(m[1].toLowerCase()+'.odf');
 for(let [n,f]of idx){if(!/[\\/]stations[\\/]/i.test(f))continue;let v=props(n),name=p.basename(n,'.odf'),model=(v.basename||name).toLowerCase();
  // Abstract templates, planets and asteroid definitions do not have building buttons.
  if(!menus.has(n)&&(!v.unitname||/^pb_|^as_/i.test(n)||v.classlabel==='planet'))continue;
  if(!menus.has(n)&&/placeholder/i.test(v.unitname||''))continue;
  let unitKey='b_'+name,modelKey='b_'+model,unitIcon=entries.get(unitKey),modelIcon=entries.get(modelKey),choice=valid(modelIcon)?modelIcon:valid(unitIcon)?unitIcon:null;
  if(!choice&&n==='cquantum.odf'){choice=entries.get('b_cupgrade');if(valid(choice))fallbacks.push({unit:n,source:'Cardassian upgrade facility icon',reason:'Dedicated gbcquantum texture absent from installed packs'});}
  if(!valid(choice)){
    const fallbackMap={'8472_basicresearch.odf':['8472_research','8472_mothership'],'borpod25.odf':['borpod15','borpod1'],'fedpod25.odf':['fedpod15','fedpod1'],'klipod25.odf':['klipod15','klipod1'],'fsuperbl.odf':['fresear2','fupgrade'],'ksuperbl.odf':['kresear2','kupgrade'],'rsuperbl.odf':['rresear2','rupgrade'],'rompod9.odf':['rompod8','rompod1']};
    if(/^(?:engine|lifesupport|sensor|shield|weapon)upgradepod2?\.odf$/i.test(n)&&!menus.has(n))continue;
    for(let candidate of fallbackMap[n]||[]){let e=entries.get('b_'+candidate);if(valid(e)){choice=e;fallbacks.push({unit:n,source:candidate,reason:'Dedicated texture missing; matching faction/function fallback'});break;}}
    if(!valid(choice)){unresolved.push({unit:n,model});continue;}
  }
  if(!valid(unitIcon))add(unitKey,choice,n);if(!valid(modelIcon))add(modelKey,choice,n);
  // Link selection wireframes under both names when either existing definition is available.
  for(let i=1;i<=5;i++){let a=name+'w'+i,b=model+'w'+i,ea=entries.get(a),eb=entries.get(b);if(!valid(ea)&&valid(eb))add(a,eb,n);if(!valid(eb)&&valid(ea))add(b,ea,n);}
  checked.push({unit:n,model,icon:entries.get(modelKey)?.texture});
 }
 let backup='D:/Xaramada-Modwork/backups/building-gui-'+stamp+'/'+p.basename(root)+'.spr';fs.mkdirSync(p.dirname(backup),{recursive:true});fs.copyFileSync(file,backup);fs.chmodSync(file,0o666);fs.writeFileSync(file,spr,'latin1');let out='D:/aramada/'+(root.endsWith('armadaIII')?'bajor/overlay/':'overlay/')+'Sprites/gui_global.spr';fs.writeFileSync(out,spr,'latin1');
 reports.push({root,checked:checked.length,repairs,fallbacks,unresolved,runtimeVerified:false});
}
fs.writeFileSync('D:/aramada/reports/building-icon-repairs.json',JSON.stringify(reports,null,2));
let message=reports.map(r=>r.root+': '+r.checked+' named/buildable station definitions checked, '+r.repairs.length+' icon/wireframe links repaired, '+r.unresolved.length+' unresolved').join('; ')+'. Quantum Facility uses matching Cardassian upgrade-facility fallback because dedicated texture is absent. Running game must restart to reload sprites; in-game confirmation pending.';
fs.appendFileSync('D:/aramada/build.log','\n['+new Date().toISOString()+'] '+message+'\n');let status=JSON.parse(fs.readFileSync('D:/aramada/status.json','utf8').replace(/^\uFEFF/,''));status.current=message;fs.writeFileSync('D:/aramada/status.json',JSON.stringify(status,null,2));console.log(message);


