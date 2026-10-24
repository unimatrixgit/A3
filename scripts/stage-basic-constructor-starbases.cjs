const l=require('./odf-lib.cjs'),crypto=require('node:crypto');
const stamp=new Date().toISOString().replace(/[:.]/g,'-');
const stage='D:/Xaramada-Modwork/staged-basic-starbases-'+stamp;
const bases={federation:'fbase',borg:'bbase',klingon:'kbase',romulan:'rbase',cardassian:'cbase',dominion:'dbase',breen:'brbase',bajoran:'bjbase',species8472:'8472_mothership'};
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const sprite=l.read(l.root+'/Sprites/gui_global.spr');
const tech=l.read(l.root+'/techtree/tech1.tt');
const changes=[],already=[];
for(const [name,file]of l.index){
 const d=l.properties(file),base=bases[d.race];
 if(!base||!/(?:^|\s)Basic Constructor(?:$|\s)/.test(d.unitname||''))continue;
 const entries=Object.entries(d).filter(([k])=>/^builditem\d+$/.test(k)).sort((a,b)=>+a[0].slice(9)-+b[0].slice(9));
 if(entries.some(([,v])=>v.toLowerCase()===base)){already.push(name);continue;}
 const slot=entries.length?Math.max(...entries.map(([k])=>+k.slice(9)))+1:0;
 if(slot>=14)throw Error(name+' has no free build slot');
 if(!l.index.has(base+'.odf'))throw Error('Missing starbase '+base);
 const bd=l.properties(l.index.get(base+'.odf'));
 if(!new RegExp('^b_'+base+'\\s','mi').test(sprite)&&!new RegExp('^b_'+(bd.basename||base)+'\\s','mi').test(sprite))throw Error('Missing existing build icon '+base);
 const line=tech.split(/\r?\n/).find(x=>new RegExp('^\\s*'+base+'\\.odf\\s','i').test(x));
 if(!line||/\.odf\s+-1\b/.test(line))throw Error('Disabled/missing starbase tech '+base);
 const old=l.fs.readFileSync(file),text=old.toString('latin1').replace(/\s*$/,'')+'\r\n\r\nbuildItem'+slot+' = "'+base+'"\r\n';
 const rel=l.p.relative(l.root,file).replaceAll('\\','/'),out=l.p.join(stage,rel);
 l.fs.mkdirSync(l.p.dirname(out),{recursive:true});l.fs.writeFileSync(out,text,'latin1');
 if(hash(l.fs.readFileSync(file))!==hash(old))throw Error('Live file unexpectedly changed');
 changes.push({unit:name.slice(0,-4),race:d.race,starbase:base,slot,relativePath:rel,liveSHA256:hash(old),stagedSHA256:hash(l.fs.readFileSync(out))});
}
const report={status:'staged only; not applied',stage,created:new Date().toISOString(),changes,alreadyAvailable:already,existingIconsReused:true,liveGameFilesChanged:false,techTreeChangesRequired:false,startingFleetsChanged:false,aiOrdersChanged:false};
l.fs.writeFileSync(l.repo+'/reports/basic-constructor-starbases-staged.json',JSON.stringify(report,null,2));
const s=JSON.parse(l.fs.readFileSync(l.repo+'/status.json','utf8'));s.current='STAGED ONLY: each faction Basic Constructor gains its own starbase. Existing icons reused; Breen already has its base. Live game files, AI orders and restored starting fleets untouched while testing continues.';s.updated=new Date().toISOString();l.fs.writeFileSync(l.repo+'/status.json',JSON.stringify(s,null,2));
l.fs.appendFileSync(l.repo+'/build.log','\n['+new Date().toISOString()+'] '+s.current+' Stage: '+stage+'\n');
console.log(JSON.stringify({stage,changes:changes.map(x=>({unit:x.unit,starbase:x.starbase,slot:x.slot+1})),alreadyAvailable:already,liveFilesChanged:false},null,2));
