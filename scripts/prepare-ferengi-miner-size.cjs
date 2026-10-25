const l=require('./odf-lib.cjs'),crypto=require('node:crypto');
const stage=l.repo+'/patches/ferengi-miner-size-20261025',rows=[];
for(const[n,file]of l.index){
 const d=l.properties(file);if(!/^(xfg|xbg)/.test(n)||d.classlabel!=='freighter')continue;
 const old=l.read(file),oldScale=Number(String(d.scalesod??1).replace(/[fF]$/,'')),newScale=Number((oldScale*.55).toPrecision(12));
 const text=old.replace(/^[ \t]*ScaleSOD[ \t]*=[^\r\n]*/gmi,'')+'\r\nScaleSOD = '+newScale+'\r\n';
 const strip=t=>t.split(/\r?\n/).filter(x=>x.trim()&&!/^[ \t]*ScaleSOD[ \t]*=/i.test(x)).join('\n');if(strip(old)!==strip(text))throw Error('Unexpected gameplay change '+n);
 const rel=l.p.relative(l.root,file).replace(/\\/g,'/'),out=l.p.join(stage,'overlay',rel);l.fs.mkdirSync(l.p.dirname(out),{recursive:true});l.fs.writeFileSync(out,text,'latin1');
 rows.push({unit:n,file:rel,oldScale,newScale,sourceHash:crypto.createHash('sha256').update(l.fs.readFileSync(file)).digest('hex'),stagedHash:crypto.createHash('sha256').update(l.fs.readFileSync(out)).digest('hex')});
}
if(rows.length!==8)throw Error('Unexpected miner count '+rows.length);
const report={status:'PREPARED - NOT APPLIED',factor:.55,reductionPercent:45,stage,miners:rows,gameplayFieldsChanged:false,runtimeVerified:false};l.fs.writeFileSync(stage+'/manifest.json',JSON.stringify(report,null,2)+'\n');l.fs.writeFileSync(stage+'/README.md','# Ferengi miner size patch\n\nPrepared, not applied. Eight mining freighter definitions, including Dilithium and Latinum tiers and Borg-priced counterparts, are scaled to 55% of their current size (ScaleSOD 1.5 to 0.825). All other ODF fields are unchanged. Trading freighters and repair ships are excluded. The apply script checks the closed game and baseline hashes, then backs up the live files before deployment.\n');l.fs.mkdirSync(l.repo+'/reports',{recursive:true});l.fs.writeFileSync(l.repo+'/reports/ferengi-miner-size-prepared.json',JSON.stringify(report,null,2)+'\n');
const sf=l.repo+'/status.json',s=JSON.parse(l.fs.readFileSync(sf,'utf8').replace(/^\uFEFF/,''));s.current='Prepared 45% visual size reduction for all eight Ferengi mining freighter variants. Scale 1.5 to 0.825. Mining, capacity, prices, crew and abilities unchanged. Not applied.';l.fs.writeFileSync(sf,JSON.stringify(s,null,2));l.fs.appendFileSync(l.repo+'/build.log','\n[Ferengi miner size] Prepared eight files at 55% of current size; gameplay unchanged. NOT APPLIED.\n');console.log(JSON.stringify({status:report.status,miners:rows.length,oldScale:1.5,newScale:.825,stage}));
