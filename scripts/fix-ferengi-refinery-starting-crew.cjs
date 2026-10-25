const l=require('./odf-lib.cjs'),cp=require('node:child_process');
const running=cp.execFileSync('powershell',['-NoProfile','-Command',"@(Get-CimInstance Win32_Process -Filter \"Name='Armada2.exe' OR Name='Armada.exe'\").Count"],{encoding:'utf8'}).trim();if(Number(running))throw Error('Game running; no files changed.');
const backup='D:/Xaramada-Modwork/backups/ferengi-refinery-crew-'+new Date().toISOString().replace(/[:.]/g,'-'),rows=[];
for(const name of ['xfgdref','xbgdref']){
 const file=l.index.get(name+'.odf'),d=l.properties(file),miner=l.properties(l.index.get(d.freightername.toLowerCase()+'.odf')),minerCrew=Number(miner.crewcost),total=100+minerCrew;
 if(minerCrew!==100||Number(d.maximumcrew)!==200)throw Error('Unexpected crew baseline '+name);
 const original=l.read(file),text=original.replace(/^([ \t]*crewCost[ \t]*=[ \t]*)[^\r\n]*/gmi,'$1'+total);
 if(text===original)throw Error('No crew change '+name);
 const remove=t=>t.replace(/^[ \t]*crewCost[ \t]*=[^\r\n]*/gmi,'');if(remove(text)!==remove(original))throw Error('Unexpected change '+name);
 const rel=l.p.relative(l.root,file),b=l.p.join(backup,rel);l.fs.mkdirSync(l.p.dirname(b),{recursive:true});l.fs.copyFileSync(file,b);l.fs.chmodSync(file,0o666);l.fs.writeFileSync(file,text,'latin1');const mirror=l.p.join(l.repo,'bajor/overlay',rel);l.fs.mkdirSync(l.p.dirname(mirror),{recursive:true});l.fs.copyFileSync(file,mirror);
 const after=l.properties(file);if(Number(after.crewcost)-minerCrew!==100||after.maximumcrew!==d.maximumcrew)throw Error('Crew verification failed '+name);
 rows.push({unit:name,oldCrewCost:Number(d.crewcost),newCrewCost:total,automaticMiner:d.freightername,minerCrew,expectedRemainingCrew:100,maximumCrew:200});
}
const report={applied:true,backup,refineries:rows,runtimeVerified:false};l.fs.writeFileSync(l.repo+'/reports/ferengi-refinery-crew-fix.json',JSON.stringify(report,null,2)+'\n');const f=l.repo+'/status.json',s=JSON.parse(l.fs.readFileSync(f,'utf8').replace(/^\uFEFF/,''));s.current='Ferengi refinery crew fix applied to both price variants: 200 construction crew covers the automatic 100-crew miner and leaves 100 aboard; maximum crew remains 200. Other stats and prices unchanged. Gameplay confirmation pending.';l.fs.writeFileSync(f,JSON.stringify(s,null,2));l.fs.appendFileSync(l.repo+'/build.log','\n[Ferengi refinery crew] Both variants now budget 200 crew: 100 for automatic miner and 100 remaining on refinery. Backup '+backup+'. Awaiting gameplay confirmation.\n');console.log(JSON.stringify(report));
