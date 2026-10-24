const l=require('./odf-lib.cjs'),crypto=require('node:crypto');
const previous=JSON.parse(l.fs.readFileSync(l.repo+'/reports/basic-constructor-starbases-staged.json','utf8'));
const stage=previous.stage,hash=b=>crypto.createHash('sha256').update(b).digest('hex'),files=new Map();
for(const c of previous.changes){
 const live=l.p.join(l.root,c.relativePath);
 if(hash(l.fs.readFileSync(live))!==c.liveSHA256)throw Error('Live baseline changed: '+c.relativePath);
 files.set(c.relativePath,{relativePath:c.relativePath,liveSHA256:c.liveSHA256,stagedSHA256:c.stagedSHA256});
}
function stageText(rel,t){
 const live=l.p.join(l.root,rel),out=l.p.join(stage,rel);const bytes=Buffer.from(t.replace(/\r?\n/g,'\r\n'),'latin1');
 l.fs.mkdirSync(l.p.dirname(out),{recursive:true});l.fs.writeFileSync(out,bytes);
 files.set(rel,{relativePath:rel,liveSHA256:hash(l.fs.readFileSync(live)),stagedSHA256:hash(bytes)});
}
const props=new Map([...l.index].map(([n,f])=>[n.slice(0,-4),l.properties(f)]));
const items=d=>Object.entries(d).filter(([k])=>/^builditem\d+$/.test(k)).sort((a,b)=>+a[0].slice(9)-+b[0].slice(9)).map(([,v])=>v.toLowerCase());
const move=items(props.get('xu3bor2')),current=items(props.get('bconst2')),merged=[...new Set([...current,...move])];
if(merged.length>14)throw Error('Advanced constructor menu overflow');
let f=l.index.get('bconst2.odf'),t=l.read(f).replace(/^\s*buildItem\d+\s*=[^\r\n]*/gmi,'');
merged.forEach((n,i)=>t+='\nbuildItem'+i+' = "'+n+'"\n');stageText(l.p.relative(l.root,f).replaceAll('\\','/'),t);
const producers=[];
for(const [name,d]of props){
 const menu=items(d);if(!menu.includes('xu3bor2'))continue;
 const updated=menu.filter(n=>n!=='xu3bor2');const file=l.index.get(name+'.odf');let text=l.read(file).replace(/^\s*buildItem\d+\s*=[^\r\n]*/gmi,'');
 updated.forEach((n,i)=>text+='\nbuildItem'+i+' = "'+n+'"\n');stageText(l.p.relative(l.root,file).replaceAll('\\','/'),text);producers.push(name);
}
for(const tree of ['tech1','earlytech','fulltech','nosci','nospweap','nosuper']){
 const rel='techtree/'+tree+'.tt';let text=l.read(l.p.join(l.root,rel)).split(/\r?\n/).map(line=>{
  const parts=line.split('//'),v=parts[0].trim().split(/\s+/);if(v[0]?.toLowerCase()==='xu3bor2.odf')return '';
  if(v.length>2&&v[0].toLowerCase().endsWith('.odf')&&+v[1]>0&&v.slice(2).some(n=>n.toLowerCase()==='xu3bor2.odf'))return [v[0],v[1],...v.slice(2).map(n=>n.toLowerCase()==='xu3bor2.odf'?'bconst2.odf':n)].join(' ')+(parts[1]?' //'+parts[1]:'');
  return line;
 }).join('\n')+'\nxu3bor2.odf -1\n';stageText(rel,text);
}
const ai=[];
for(const file of l.fs.readdirSync(l.root+'/AI/AIPs').filter(n=>n.endsWith('.aip'))){
 const rel='AI/AIPs/'+file,text=l.read(l.root+'/'+rel);if(!/^\s*"xu3bor2"\s*,/m.test(text))continue;
 if(!/^\s*"bconst2"\s*,/m.test(text))throw Error('AI needs Advanced Constructor: '+file);
 stageText(rel,text.split(/\r?\n/).filter(line=>!/^\s*"xu3bor2"\s*,/.test(line)).join('\n'));ai.push(file);
}
for(const c of files.values())if(hash(l.fs.readFileSync(l.root+'/'+c.relativePath))!==c.liveSHA256)throw Error('Live file changed');
const report={status:'staged only; not applied',stage,movedFrom:'xu3bor2',movedTo:'bconst2',buildings:move,advancedMenu:merged,removedProductionFrom:producers,aiPlans:ai,files:[...files.values()],includesEarlierOwnStarbaseT1Stage:true,liveGameFilesChanged:false,iconsChanged:false,startsChanged:false};
l.fs.writeFileSync(l.repo+'/reports/borg-specialist-removal-staged.json',JSON.stringify(report,null,2));
const status=JSON.parse(l.fs.readFileSync(l.repo+'/status.json','utf8'));status.current='STAGED ONLY: own starbases on Basic Constructors; Borg Transwarp Hub, Borg Ferengi Contract Yard and Central Unicomplex moved to Advanced Constructor. Extra Borg Temporal Specialist removed from production, tech and AI. Live game and working starting fleets unchanged while testing continues.';status.updated=new Date().toISOString();l.fs.writeFileSync(l.repo+'/status.json',JSON.stringify(status,null,2));l.fs.appendFileSync(l.repo+'/build.log','\n['+new Date().toISOString()+'] '+status.current+' Stage:'+stage+'\n');
console.log(JSON.stringify({moved:move,to:'Borg Advanced Constructor',menuEntries:merged.length,productionMenus:producers,aiPlans:ai.length,stagedFiles:files.size,liveGameFilesChanged:false},null,2));
