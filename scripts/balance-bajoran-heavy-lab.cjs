const fs=require('fs'),p=require('path'),root='D:/ArmadaLab',stamp=Date.now();
const walk=d=>fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(p.join(d,e.name)):[p.join(d,e.name)]),idx=new Map(walk(root+'/odf').filter(f=>/\.odf$/i.test(f)).map(f=>[p.basename(f).toLowerCase(),f]));
const read=f=>fs.readFileSync(f,'latin1');function props(n,seen=new Set()){if(!idx.has(n)||seen.has(n))return {};seen.add(n);let t=read(idx.get(n)),v={};for(let m of t.matchAll(/^[ \t]*#include[ \t]+"([^"\r\n]+)"/gmi))Object.assign(v,props(m[1].toLowerCase(),seen));for(let m of t.matchAll(/^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)/gm))v[m[1].toLowerCase()]=m[2].split('//')[0].trim().replace(/^"|"$/g,'');return v;}
const ref=props('fbattle.odf'),num=(v,k)=>parseFloat(v[k])||0;let report={root,reference:'fbattle.odf (standard Sovereign, not Enterprise-E hero)',referenceStats:ref,units:[],runtimeVerified:false};
function set(t,k,v){return t.replace(new RegExp('^[ \\t]*'+k+'[ \\t]*=.*$','gmi'),'')+'\r\n'+k+' = '+v+'\r\n';}
function save(rel,t){let f=root+'/'+rel,b='D:/Xaramada-Modwork/backups/bajoran-heavy-lab-'+stamp+'/'+rel;fs.mkdirSync(p.dirname(b),{recursive:true});if(fs.existsSync(f)){fs.copyFileSync(f,b);fs.chmodSync(f,0o666);}fs.mkdirSync(p.dirname(f),{recursive:true});fs.writeFileSync(f,t,'latin1');let out='D:/aramada/lab/overlay/'+rel;fs.mkdirSync(p.dirname(out),{recursive:true});fs.writeFileSync(out,t,'latin1');}
for(let [name,hpFactor,fireFactor,costFactor,timeFactor]of [['bjbattle',0.90,0.90,1,1.10],['bjsuper',1,1,1.15,1.20],['bjnerys',1.15,1.05,1.40,1.50]]){
 let f=idx.get(name+'.odf'),before=props(name+'.odf'),t=read(f),changes={maxHealth:Math.round(num(ref,'maxhealth')*hpFactor),shieldRate:+(num(ref,'shieldrate')*hpFactor).toFixed(4)};
 for(let key of ['maxspecialenergy','specialenergyrate'])if(num(ref,key)>0)changes[key]=+(num(ref,key)*Math.min(hpFactor,1.15)).toFixed(3);
 for(let key of ['dilithiumcost','metalcost','latinumcost','biomattercost','officercost'])changes[key]=Math.ceil(num(ref,key)*costFactor);
 changes.crewCost=name==='bjnerys'?Math.round(num(ref,'crewcost')*1.1):num(ref,'crewcost');changes.buildTime=Math.ceil(num(ref,'buildtime')*timeFactor);
 for(let [key,val]of Object.entries(changes))t=set(t,key,val);
 let banks=[];for(let [key,weapon]of Object.entries(before)){if(!/^weapon\d+$/.test(key))continue;let v=props(weapon.toLowerCase()+'.odf');if(num(v,'special')===1||!v.ordname||!(num(v,'shotdelay')>0))continue;let alias='xlab_'+name+'_'+key,delay=num(v,'shotdelay')/fireFactor;save('odf/weapons/'+alias+'.odf','#include "'+weapon+'.odf"\r\nshotDelay = '+delay.toFixed(6)+'\r\n');t=set(t,key,'"'+alias+'"');banks.push({slot:key,original:weapon,wrapper:alias,oldDelay:num(v,'shotdelay'),newDelay:delay,refireOutputFactor:fireFactor});}
 if(name==='bjnerys')t=set(t,'verboseTooltip','"Kira Nerys command battleship. Lab balance: 15 percent tougher than a standard Sovereign, with a modest weapon bonus."');
 save(p.relative(root,f),t);report.units.push({unit:name,before:{maxHealth:num(before,'maxhealth'),shieldRate:num(before,'shieldrate'),dilithium:num(before,'dilithiumcost'),metal:num(before,'metalcost')},after:changes,banks,hullRatio:hpFactor,nominalWeaponRefireFactor:fireFactor,note:'Weapon timing ratio only; not an engine combat simulation. Hero special abilities retained.'});
}
fs.writeFileSync('D:/aramada/reports/bajoran-heavy-lab-balance.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report.units.map(u=>({unit:u.unit,before:u.before,after:u.after,banks:u.banks.length}))));

