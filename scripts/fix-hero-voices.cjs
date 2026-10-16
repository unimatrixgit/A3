const fs=require('fs'),p=require('path');
const roots=['D:/Xaramada','D:/armadaIII'],stamp=Date.now(),reports=[];
function walk(d){return fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(p.join(d,e.name)):[p.join(d,e.name)]);}
for(const root of roots){
 const idx=new Map(walk(root+'/odf').filter(f=>/\.odf$/i.test(f)).map(f=>[p.basename(f).toLowerCase(),f]));
 const audio=new Set(walk(root+'/sounds').map(f=>p.basename(f).toLowerCase()));
 const read=f=>fs.readFileSync(f,'latin1');
 function props(n,seen=new Set()){if(seen.has(n)||!idx.has(n))return {};seen.add(n);let t=read(idx.get(n)),v={};for(let m of t.matchAll(/^\s*#include\s+"([^"]+)"/gmi))Object.assign(v,props(m[1].toLowerCase(),seen));for(let m of t.matchAll(/^\s*(\w+)\s*=\s*(.*?)\s*(?:\/\/.*)?$/gm))v[m[1].toLowerCase()]=m[2].replace(/^"|"$/g,'');return v;}
 let events=read(root+'/events.dat'),blocks=new Map([...events.matchAll(/^\s*(\w+)\s*\{([^{}]*)\}/gm)].map(m=>[m[1].toLowerCase(),m[2]]));
 const actions=['Select','Acknowledge','Attack','Stop','Move','Repair','RedAlert','YellowAlert','GreenAlert','Transport','SelfDestruct','Decommission'];
 let units=[];
 function clips(event,race){let b=blocks.get(event.toLowerCase())||'',out=[];for(let m of b.matchAll(/\bSound\s+(?:<([^>]+)>\s*)?"([^"]+)"/gi)){if((!m[1]||m[1].toLowerCase()===race)&&audio.has(m[2].toLowerCase()))out.push(m[2]);}return [...new Set(out)];}
 function save(rel,text){let dest=root+'/'+rel,bak='D:/Xaramada-Modwork/backups/hero-voices-'+stamp+'/'+p.basename(root)+'/'+rel;fs.mkdirSync(p.dirname(bak),{recursive:true});if(fs.existsSync(dest))fs.copyFileSync(dest,bak);fs.chmodSync(dest,0o666);fs.writeFileSync(dest,text,'latin1');let out='D:/aramada/'+(root.endsWith('armadaIII')?'bajor/overlay/':'overlay/')+rel;fs.mkdirSync(p.dirname(out),{recursive:true});fs.writeFileSync(out,text,'latin1');}
 for(let [n,f]of idx){if(!/[\\/]ships[\\/]/i.test(f))continue;let v=props(n);if(v.ishero!=='1'&&!/^(?:xh.*hero|blocutus|xoblocutus|kmartok|fente|fentd|dweyoun|bjnerys)\.odf$/i.test(n))continue;
  let race=(v.race||'federation').toLowerCase(),voiceRace=(race==='bajoran'||race==='alien')?'federation':race,t=read(f),changes=[];
  for(let a of actions){let original=v['event'+a.toLowerCase()]||'',choices=[original,'Battle'+a,'Scout'+a],selected=[],source='';
   for(let e of choices){if(!e)continue;selected=clips(e,voiceRace);if(selected.length){source=e;break;}}
   // Retain a valid command-specific event; use acknowledgement only where no action-specific audio exists.
   if(!selected.length){for(let e of [v.eventacknowledge||'','BattleAcknowledge','ScoutAcknowledge']){selected=clips(e,voiceRace);if(selected.length){source=e;break;}}}
   if(!selected.length){changes.push({action:a,error:'No available faction audio'});continue;}
   let key='XV_'+p.basename(n,'.odf')+'_'+a;
   events=events.replace(new RegExp('^\\s*'+key+'\\s*\\{[^{}]*\\}\\s*','gmi'),'');
   events+='\r\n'+key+'{\r\nTable\r\n'+selected.map(x=>' Sound "'+x+'"').join('\r\n')+'\r\nSoundPriority 2\r\n}\r\n';
   t=t.replace(new RegExp('^\\s*event'+a+'\\s*=.*$','gmi'),'');t+='\r\nevent'+a+' = "'+key+'"\r\n';changes.push({action:a,source,clips:selected,fallback:source!==original,temporaryGenericVoice:race==='bajoran'});
  }
  save(p.relative(root,f),t);units.push({unit:n,race,commands:changes});
 }
 save('events.dat',events);
 let errors=units.flatMap(u=>u.commands.filter(c=>c.error).map(c=>({unit:u.unit,...c})));
 reports.push({root,units,errors,applied:true,runtimeAudioTested:false});
}
fs.mkdirSync('D:/aramada/reports',{recursive:true});fs.writeFileSync('D:/aramada/reports/hero-voices.json',JSON.stringify(reports,null,2));
let message='Hero voices applied: '+reports.map(r=>r.root+' '+r.units.length+' heroes, '+r.errors.length+' missing command audio').join('; ')+'. Kira uses temporary Federation audio. Restart required for running game.';
fs.appendFileSync('D:/aramada/build.log','\n['+new Date().toISOString()+'] '+message+'\n');let s=JSON.parse(fs.readFileSync('D:/aramada/status.json','utf8').replace(/^\uFEFF/,''));s.current=message+' File references validated; in-game playback not yet tested.';fs.writeFileSync('D:/aramada/status.json',JSON.stringify(s,null,2));console.log(message);

