const fs=require('fs'),p=require('path'),stamp=Date.now(),root='D:/ArmadaLab';
const walk=d=>fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(p.join(d,e.name)):[p.join(d,e.name)]),idx=new Map(walk(root+'/odf').filter(f=>/\.odf$/i.test(f)).map(f=>[p.basename(f).toLowerCase(),f]));
const read=f=>fs.readFileSync(f,'latin1');
function props(n,seen=new Set()){if(seen.has(n)||!idx.has(n))throw Error('Invalid include '+n);seen.add(n);let t=read(idx.get(n)),v={};for(let m of t.matchAll(/^[ \t]*#include[ \t]+"([^"\r\n]+)"/gmi))Object.assign(v,props(m[1].toLowerCase(),seen));for(let m of t.matchAll(/^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)/gm))v[m[1].toLowerCase()]=m[2].split('//')[0].trim().replace(/^"|"$/g,'');return v;}
let files=[],report={dump:'Armada2.exe.30124.dmp',fault:'0x004d162c GameObject::Init, null first weapon class during Shipyard::FinishBuild',unitEvidence:'bjbattle string occurs in crash dump; exact instance/class heap not captured',causeConfirmed:false,mitigation:'Replace inherited cross-directory timing wrappers with self-contained native cannon definitions, short identifiers, and native weapon subfolders',units:[],runtimeVerified:false};
function save(rel,text){let f=root+'/'+rel,b='D:/Xaramada-Modwork/backups/bajoran-weapon-init-lab-'+stamp+'/'+rel;fs.mkdirSync(p.dirname(b),{recursive:true});if(fs.existsSync(f)){fs.copyFileSync(f,b);fs.chmodSync(f,0o666);}fs.mkdirSync(p.dirname(f),{recursive:true});fs.writeFileSync(f,text,'latin1');let out='D:/aramada/lab/overlay/'+rel;fs.mkdirSync(p.dirname(out),{recursive:true});fs.writeFileSync(out,text,'latin1');files.push(rel);}
const numeric=/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?f?$/i;
for(let [unit,alias,factor]of [['bjbattle','bjb',0.9],['bjsuper','bjs',1],['bjnerys','bjn',1.05]]){
 let f=idx.get(unit+'.odf'),ship=read(f),banks=[];
 for(let [slot,parent,suffix,folder]of [[1,'fsovereignphas','phs','Phasers'],[2,'fsovereignphot','tor','Photons']]){
  let v=props(parent+'.odf');if(v.classlabel!=='cannon'||!idx.has(v.ordname.toLowerCase()+'.odf'))throw Error('Invalid native weapon '+parent);v.shotdelay=(parseFloat(v.shotdelay)/factor).toFixed(6);
  let text='// Standalone native cannon definition. No cross-directory includes.\r\n'+Object.entries(v).map(([k,val])=>k+' = '+(numeric.test(val)?val:'"'+val+'"')).join('\r\n')+'\r\n';let name=alias+suffix;save('odf/weapons/'+folder+'/'+name+'.odf',text);
  // Retain compatible definitions for old names too, to avoid leaving a broken referenced file behind.
  save('odf/weapons/xlab_'+unit+'_weapon'+slot+'.odf',text);
  ship=ship.replace(new RegExp('^[ \\t]*weapon'+slot+'[ \\t]*=.*$','gmi'),'')+'\r\nweapon'+slot+' = "'+name+'"\r\n';banks.push({slot,weapon:name,classLabel:v.classlabel,ordName:v.ordname,shotDelay:v.shotdelay});
 }
 save(p.relative(root,f),ship);report.units.push({unit,banks});
}
report.files=[...new Set(files)];fs.writeFileSync('D:/aramada/reports/bajoran-weapon-initialization-fix.json',JSON.stringify(report,null,2));console.log(JSON.stringify({files:report.files.length,units:report.units}));
