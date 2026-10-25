const l=require('./odf-lib.cjs'),cp=require('node:child_process'),crypto=require('node:crypto');
const running=cp.execFileSync('powershell',['-NoProfile','-Command',"@(Get-CimInstance Win32_Process -Filter \"Name='Armada2.exe' OR Name='Armada.exe'\").Count"],{encoding:'utf8'}).trim();
if(Number(running))throw Error('Game is still running; no files changed.');
const stamp=new Date().toISOString().replace(/[:.]/g,'-'),backup='D:/Xaramada-Modwork/backups/dil-refinery-size-'+stamp;
const rows=[],prepared=[];
const number=v=>Number(String(v).replace(/[fF]$/,''));
function put(t,k,v){return t.replace(new RegExp('^[ \\t]*'+k+'[ \\t]*=[^\\r\\n]*','gmi'),'')+'\r\n'+k+' = '+Number(v.toPrecision(12))+'\r\n';}
for(const[n,file]of l.index){
 const before=l.properties(file);
 if(before.classlabel!=='mining'||!/dilithium/i.test(before.resourcescanhandle||''))continue;
 const rel=l.p.relative(l.root,file).replace(/\\/g,'/'),old=l.read(file),fields={ScaleSOD:number(before.scalesod??1)*.75};
 for(const k of ['footprintBuffer','eastBuffer','westBuffer','northBuffer','southBuffer'])if(before[k.toLowerCase()]!==undefined)fields[k]=number(before[k.toLowerCase()])*.75;
 let text=old;for(const[k,v]of Object.entries(fields)){if(!Number.isFinite(v))throw Error('Invalid scale '+n);text=put(text,k,v);}
 const allowed=new Set(Object.keys(fields).map(k=>k.toLowerCase()));
 function stripped(t){return t.split(/\r?\n/).filter(line=>!/^\s*$/.test(line)&&!allowed.has((line.match(/^[ \t]*(\w+)[ \t]*=/)||[])[1]?.toLowerCase())).join('\n');}
 if(stripped(old)!==stripped(text))throw Error('Unexpected gameplay change '+n);
 prepared.push({file,rel,text});rows.push({unit:n,name:before.unitname,oldScale:number(before.scalesod??1),newScale:fields.ScaleSOD,fields});
}
if(prepared.length!==11)throw Error('Unexpected refinery count '+prepared.length);
for(const o of prepared){const b=l.p.join(backup,o.rel);l.fs.mkdirSync(l.p.dirname(b),{recursive:true});l.fs.copyFileSync(o.file,b);}
for(const o of prepared){l.fs.chmodSync(o.file,0o666);l.fs.writeFileSync(o.file,o.text,'latin1');const mirror=l.p.join(l.repo,'bajor/overlay',o.rel);l.fs.mkdirSync(l.p.dirname(mirror),{recursive:true});l.fs.copyFileSync(o.file,mirror);const after=l.properties(o.file),row=rows.find(r=>r.unit===l.p.basename(o.file).toLowerCase());if(Math.abs(number(after.scalesod)-row.newScale)>1e-9)throw Error('Scale verification failed '+o.rel);}
const report={applied:true,factor:.75,backup,refineries:rows,gameplayStatsChanged:false,runtimeVerified:false};
l.fs.writeFileSync(l.repo+'/reports/dil-refinery-size-reduction.json',JSON.stringify(report,null,2)+'\n');
const sf=l.repo+'/status.json',s=JSON.parse(l.fs.readFileSync(sf,'utf8').replace(/^\uFEFF/,''));s.current='All 11 refinery definitions reduced by 25%, with proportionate placement footprints. Includes both Ferengi price variants and the 8472 equivalent. Costs, crew, mining rates, capacities and weapons unchanged. File checks passed; gameplay testing pending.';l.fs.writeFileSync(sf,JSON.stringify(s,null,2));
l.fs.appendFileSync(l.repo+'/build.log','\n[Refinery size] Applied 25% reduction to 11 refineries and placement buffers; backup '+backup+'. Gameplay fields unchanged.\n');console.log(JSON.stringify(report));
