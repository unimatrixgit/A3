const fs=require('node:fs'),p=require('node:path');
const root='D:/Xaramada',repo='D:/aramada',backup='D:/Xaramada-Modwork/backups/custom-features';
const walk=d=>fs.readdirSync(d,{withFileTypes:true}).flatMap(x=>x.isDirectory()?walk(p.join(d,x.name)):[p.join(d,x.name)]);
const files=walk(root+'/odf').filter(x=>/\.odf$/i.test(x)),index=new Map(files.map(x=>[p.basename(x).toLowerCase(),x]));
const read=x=>fs.readFileSync(x,'latin1');
function save(file,text){let rel=p.relative(root,file),bak=p.join(backup,rel);fs.mkdirSync(p.dirname(bak),{recursive:true});if(fs.existsSync(file)&&!fs.existsSync(bak))fs.copyFileSync(file,bak);fs.mkdirSync(p.dirname(file),{recursive:true});if(fs.existsSync(file))fs.chmodSync(file,0o666);fs.writeFileSync(file,text,'latin1');let out=p.join(repo,'overlay',rel);fs.mkdirSync(p.dirname(out),{recursive:true});fs.copyFileSync(file,out);}
function properties(file,seen=new Set()){if(!file||seen.has(file))return {};seen.add(file);let t=read(file),v={};for(let m of t.matchAll(/^\s*#include\s+"([^"]+)"/gmi))Object.assign(v,properties(index.get(m[1].toLowerCase()),seen));for(let m of t.matchAll(/^\s*([a-z][a-z0-9_]*)\s*=\s*(.*?)\s*(?:\/\/.*)?$/gmi))v[m[1].toLowerCase()]=m[2].replace(/^"|"$/g,'');return v;}
const log=m=>{let line='['+new Date().toISOString()+'] '+m;fs.appendFileSync(repo+'/build.log',line+'\n');console.log(line)};

module.exports={fs,p,root,repo,backup,walk,files,index,read,save,properties,log};
