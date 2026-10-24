const l=require('./odf-lib.cjs'),crypto=require('node:crypto');
const prior=JSON.parse(l.fs.readFileSync(l.repo+'/reports/borg-specialist-removal-staged.json','utf8'));
const stage=prior.stage,hash=b=>crypto.createHash('sha256').update(b).digest('hex'),files=new Map(prior.files.map(x=>[x.relativePath,x])),changes=[];
for(const x of files.values())if(hash(l.fs.readFileSync(l.root+'/'+x.relativePath))!==x.liveSHA256)throw Error('Live baseline changed: '+x.relativePath);
function put(t,k,v){return t.replace(new RegExp('^\\s*'+k+'\\s*=[^\\r\\n]*','gmi'),'')+'\r\n'+k+' = '+v+'\r\n';}
for(const [n,file]of l.index){
 const d=l.properties(file);
 if(d.race!=='borg'||!file.toLowerCase().includes('ships')||!/cube|cubus|locutus|hugh/i.test([n,d.unitname,d.tooltip,d.basename].join(' ')))continue;
 const oldCrew=Number(d.crewcost),oldMax=Number(d.maximumcrew??d.crewcost);
 if(!Number.isFinite(oldCrew)||!Number.isFinite(oldMax))throw Error('Invalid crew '+n);
 const crew=Math.round(oldCrew*1.35),max=Math.max(crew,Math.round(oldMax*1.35));
 const rel=l.p.relative(l.root,file).replaceAll('\\','/'),out=l.p.join(stage,rel),live=l.fs.readFileSync(file);
 const text=l.fs.existsSync(out)?l.read(out):live.toString('latin1');
 const updated=put(put(text,'crewCost',crew),'maximumCrew',max);
 l.fs.mkdirSync(l.p.dirname(out),{recursive:true});l.fs.writeFileSync(out,updated,'latin1');
 const oldEntry=files.get(rel);files.set(rel,{relativePath:rel,liveSHA256:oldEntry?.liveSHA256||hash(live),stagedSHA256:hash(l.fs.readFileSync(out))});
 changes.push({unit:n.slice(0,-4),name:d.unitname,oldCrew,newCrew:crew,oldMaximumCrew:oldMax,newMaximumCrew:max});
}
if(changes.length!==18)throw Error('Unexpected cube count: '+changes.length);
for(const x of files.values())if(hash(l.fs.readFileSync(l.root+'/'+x.relativePath))!==x.liveSHA256)throw Error('Live file changed');
const report={status:'staged only; not applied',stage,crewMultiplier:1.35,rounding:'nearest whole crew member',changes,files:[...files.values()],includesOwnStarbaseT1Stage:true,includesBorgSpecialistRemovalStage:true,liveGameFilesChanged:false,startingFleetsChanged:false,iconsChanged:false};
l.fs.writeFileSync(l.repo+'/reports/borg-cube-crew-staged.json',JSON.stringify(report,null,2));
l.fs.writeFileSync(l.repo+'/reports/pending-game-patch-staged.json',JSON.stringify(report,null,2));
const s=JSON.parse(l.fs.readFileSync(l.repo+'/status.json','utf8'));s.current='STAGED ONLY: +35% starting and maximum crew on18 Borg cube definitions, including Scout, Locutus/Hugh, Omega and fusion variants. Includes own starbases on Basic Constructors and the Borg Specialist removal/move to Advanced Constructor. Live game, icons and restored starting fleets unchanged while testing continues.';s.updated=new Date().toISOString();l.fs.writeFileSync(l.repo+'/status.json',JSON.stringify(s,null,2));l.fs.appendFileSync(l.repo+'/build.log','\n['+new Date().toISOString()+'] '+s.current+' Stage:'+stage+'\n');
console.log(JSON.stringify({cubeDefinitions:changes.length,totalStagedFiles:files.size,examples:changes.filter(x=>['bbattle1','bbattle2','blocutus','bscout'].includes(x.unit)),liveGameFilesChanged:false},null,2));
