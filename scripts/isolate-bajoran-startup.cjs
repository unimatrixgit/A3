const fs=require('fs'),p=require('path'),crypto=require('crypto');
const root='D:/armadaIII',repo='D:/aramada',backup='D:/Xaramada-Modwork/backups/bajor-startup-isolation-'+Date.now();
const read=f=>fs.readFileSync(f,'latin1');
const value=(t,k)=>t.match(new RegExp('^[ \\t]*'+k+'[ \\t]*=[ \\t]*([^\\r\\n]+)','mi'))?.[1];
function set(t,k,v){return t.replace(new RegExp('^[ \\t]*'+k+'[ \\t]*=[^\\r\\n]*(?:\\r?\\n)?','gmi'),'').trimEnd()+'\r\n'+k+' = '+v+'\r\n';}
let changes=[];
for(const [rel,source,model]of [['odf/ships/bjconst.odf','odf/ships/fconst.odf','fconst'],['odf/ships/bjscout.odf','odf/ships/fscout.odf','fscout'],['odf/ships/bjnerys.odf','odf/ships/fdestroy.odf','fdestroy'],['odf/stations/bjbase.odf','odf/stations/fbase.odf','xvstock_fbase']]){
 const old=read(root+'/'+rel);let t=read(root+'/'+source);
 t=t.replace(/^[ \t]*buildItem\d+[ \t]*=[^\r\n]*(?:\r?\n)?/gmi,'');
 for(const m of old.matchAll(/^[ \t]*(buildItem\d+)[ \t]*=[ \t]*([^\r\n]+)/gmi))t=set(t,m[1],m[2]);
 for(const key of ['unitName','tooltip','verboseTooltip','dilithiumCost','metalCost','latinumCost','biomatterCost','crewCost','officerCost','buildTime']){let v=value(old,key);if(v!==undefined)t=set(t,key,v);}
 t=set(t,'race','"bajoran"');t=set(t,'baseName','"'+model+'"');
 if(rel.includes('bjnerys'))for(const m of old.matchAll(/^[ \t]*(event\w+)[ \t]*=[ \t]*([^\r\n]+)/gmi))t=set(t,m[1],m[2]);
 if(rel.includes('bjbase'))t=set(t,'possibleCraftNames','"Deep Space 9"');
 changes.push({rel,source,model,text:t});
}
const rel='odf/other/bajoran.odf';let t=read(root+'/'+rel);t=set(t,'interfaceConfiguration','"gui_fed.cfg"');t=set(t,'interfaceSprites','"gui_federation.spr"');changes.push({rel,text:t});
for(const c of changes){if(c.text.split(/\r?\n/).some(l=>l.split('//')[0].split('"').length%2===0))throw Error('Quote error '+c.rel);const f=root+'/'+c.rel,b=backup+'/'+c.rel;fs.mkdirSync(p.dirname(b),{recursive:true});fs.copyFileSync(f,b);fs.chmodSync(f,0o666);fs.writeFileSync(f,c.text,'latin1');let overlay=repo+'/bajor/overlay/'+c.rel;fs.mkdirSync(p.dirname(overlay),{recursive:true});fs.writeFileSync(overlay,c.text,'latin1');c.sha256=crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');delete c.text;}
const r={target:root,backup,changes,diagnostic:true,ds9VisualTemporarilyReplaced:true,rosterAiTechPreserved:true,runtimeVerified:false};fs.writeFileSync(repo+'/reports/bajor-startup-isolation.json',JSON.stringify(r,null,2));
const s=JSON.parse(fs.readFileSync(repo+'/status.json','utf8').replace(/^\uFEFF/,''));s.current='Applied 5-file Bajoran startup isolation patch in D:/armadaIII. Four starting unit types now use existing Federation definitions with Bajoran identity, costs and build menus; faction uses existing Federation interface. DS9 temporarily uses the standard starbase model. Full Bajoran roster/AI/tech unchanged. Original files backed up. Test a new Bajoran match; crash recovery is NOT confirmed.';s.lastCompleted={task:'Bajoran startup isolation patch',time:new Date().toISOString(),runtimeVerified:false};fs.writeFileSync(repo+'/status.json',JSON.stringify(s,null,2));fs.appendFileSync(repo+'/build.log','\n['+new Date().toISOString()+'] '+s.current+'\n');console.log(JSON.stringify(r));
