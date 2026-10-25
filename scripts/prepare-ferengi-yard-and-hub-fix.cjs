const l=require('./odf-lib.cjs'),crypto=require('node:crypto');
const reportfile=l.repo+'/reports/ferengi-miner-size-prepared.json',pack=JSON.parse(l.fs.readFileSync(reportfile,'utf8'));if(pack.status!=='PREPARED - NOT APPLIED')throw Error('Combined patch is not pending.');
const P=JSON.parse(l.fs.readFileSync(l.repo+'/reports/ferengi-yard-audit-before.json','utf8')),pending=new Map(),moved=['mrc022','mrc023','mrc024'],hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const entries=d=>Object.entries(d).filter(([k])=>/^builditem[0-9]+$/.test(k)).sort((a,b)=>Number(a[0].slice(9))-Number(b[0].slice(9))).map(([,v])=>v);
function put(t,k,v){return t.replace(new RegExp('^[ \\t]*'+k+'[ \\t]*=[^\\r\\n]*','gmi'),'')+'\r\n'+k+' = '+v+'\r\n';}
function writeMenu(n,items){if(items.length>14)throw Error('Menu overflow '+n);let t=l.read(P[n].file).replace(/^[ \t]*buildItem[0-9]+[ \t]*=[^\r\n]*/gmi,'');for(let i=0;i<items.length;i++)t+='\r\nbuildItem'+i+' = "'+items[i]+'"\r\n';pending.set(l.p.relative(l.root,P[n].file).replace(/\\/g,'/'),t);P[n]={...P[n]};for(const k of Object.keys(P[n]))if(/^builditem[0-9]+$/.test(k))delete P[n][k];items.forEach((v,i)=>P[n]['builditem'+i]=v);}
for(const n of ['byard3','mryborg'])writeMenu(n,entries(P[n]).filter(n=>!moved.includes(n)));
writeMenu('xbgmerc',[...new Set(entries(P.xbgmerc).concat(moved))]);
let checked=0;
for(const[n,d]of Object.entries(P)){
 if(d.classlabel!=='shipyard')continue;checked++;
 if(/ferengi/i.test(d.unitname||''))continue;
 const bad=entries(d).filter(x=>{const ship=P[x.toLowerCase()];return ship&&(ship.race==='ferengi'||/ferengi/i.test(ship.unitname||'')||/^(xfg|xbg)/.test(x));});
 if(bad.length)throw Error('Ferengi ships still in non-Ferengi yard '+n+': '+bad.join(','));
}
for(const tree of ['tech1','earlytech','fulltech','nosci','nosuper','nospweap']){
 const rel='techtree/'+tree+'.tt',original=l.read(l.p.join(l.root,rel));let t=original;
 for(const unit of moved){const re=new RegExp('^'+unit+'\\.odf[ \\t]+[^\\r\\n]*','gmi');if(!re.test(t))throw Error('Missing technology '+unit+' '+tree);re.lastIndex=0;t=t.replace(re,unit+'.odf '+(tree==='fulltech'?'0':'1 xbgmerc.odf')+' // Mirror Ferengi: Ferengi Contract Yard');}
 if(t!==original)pending.set(rel,t);
}
// Restore the exact pre-redesign model binding and its working GUI entries.
const before=JSON.parse(l.fs.readFileSync(l.repo+'/reports/resource-science-all-before.json','utf8')),model=before.hub.basename||'hub',hubRel=l.p.relative(l.root,P.hub.file).replace(/\\/g,'/');
if(!l.fs.existsSync(l.root+'/SOD/'+model+'.sod'))throw Error('Original hub model missing');pending.set(hubRel,put(l.read(P.hub.file),'baseName','"'+model+'"'));
const backup=JSON.parse(l.fs.readFileSync(l.repo+'/reports/resource-science-redesign-applied.json','utf8')).backup,oldSprite=l.read(l.p.join(backup,'Sprites/gui_global.spr'));let sprite=l.read(l.root+'/Sprites/gui_global.spr');
const keys=['b_hub',...Array.from({length:5},(_,i)=>'hubw'+(i+1))];
for(const key of keys){const match=oldSprite.match(new RegExp('^'+key+'[ \\t]+[^\\r\\n]*','mi'));if(!match)throw Error('Original hub sprite missing '+key);const pos=oldSprite.indexOf(match[0]),prefix=oldSprite.slice(0,pos),refs=[...prefix.matchAll(/^@reference[ \t]*=[ \t]*(\d+)/gmi)],mats=[...prefix.matchAll(/^@tmaterial[ \t]*=[ \t]*(\S+)/gmi)];sprite=sprite.replace(new RegExp('^'+key+'[ \\t]+[^\\r\\n]*','gmi'),'');sprite+='\r\n@reference='+refs.at(-1)[1]+'\r\n@tmaterial='+(mats.at(-1)?.[1]||'default')+'\r\n'+match[0]+'\r\n';}
pending.set('Sprites/gui_global.spr',sprite);
const files=[];
for(const[rel,t]of pending){const dest=l.p.join(pack.stage,'overlay',rel);l.fs.mkdirSync(l.p.dirname(dest),{recursive:true});l.fs.writeFileSync(dest,t,'latin1');files.push({unit:rel,file:rel,sourceHash:hash(l.fs.readFileSync(l.p.join(l.root,rel))),stagedHash:hash(l.fs.readFileSync(dest))});}
pack.additionalFiles=files;pack.yardFix={moved,removedFrom:['byard3','mryborg'],destination:'xbgmerc',allShipyardsAudited:checked,ferengiOnlyInFerengiShipyards:true,shipStatsChanged:false};pack.hubRestore={model,restoredGuiKeys:keys};l.fs.writeFileSync(reportfile,JSON.stringify(pack,null,2)+'\n');l.fs.writeFileSync(pack.stage+'/manifest.json',JSON.stringify(pack,null,2)+'\n');
const report={status:pack.status,files:files.length,...pack.yardFix,hubRestore:pack.hubRestore};l.fs.writeFileSync(l.repo+'/reports/ferengi-yard-hub-fix-prepared.json',JSON.stringify(report,null,2)+'\n');
l.fs.appendFileSync(pack.stage+'/README.md','\nAlso moves the three Borg-priced mirror Ferengi heroes from byard3 and dormant mryborg to xbgmerc, updates all six technology trees, audits every shipyard, and restores the Transwarp Hub model and GUI from before its redesign. No heroes or yards are newly enabled.\n');
const sf=l.repo+'/status.json',s=JSON.parse(l.fs.readFileSync(sf,'utf8').replace(/^\uFEFF/,''));s.current='Combined patch prepared: miners -45%, four Ferengi orbitals matched to other orbitals, mirror Ferengi moved into Ferengi Contract Yard, and original Borg Transwarp Hub model/icons restored. All shipyards audited. NOT APPLIED.';l.fs.writeFileSync(sf,JSON.stringify(s,null,2));l.fs.appendFileSync(l.repo+'/build.log','\n[Ferengi yard / hub fix] Prepared migration of three mirror Ferengi heroes to xbgmerc; audited '+checked+' shipyards; staged original hub restoration. NOT APPLIED.\n');console.log(JSON.stringify(report));
