const l=require('./odf-lib.cjs'),crypto=require('node:crypto');
const prior=JSON.parse(l.fs.readFileSync(l.repo+'/reports/pending-game-patch-staged.json','utf8')),stage=prior.stage;
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const files=new Map(prior.files.map(x=>[x.relativePath,x]));
for(const x of files.values())if(hash(l.fs.readFileSync(l.root+'/'+x.relativePath))!==x.liveSHA256)throw Error('Live baseline changed '+x.relativePath);
function readRel(rel){const f=l.p.join(stage,rel);return l.read(l.fs.existsSync(f)?f:l.p.join(l.root,rel));}
function write(rel,text){const out=l.p.join(stage,rel),live=l.p.join(l.root,rel),bytes=Buffer.from(text.replace(/\r?\n/g,'\r\n'),'latin1');l.fs.mkdirSync(l.p.dirname(out),{recursive:true});l.fs.writeFileSync(out,bytes);files.set(rel,{relativePath:rel,liveSHA256:l.fs.existsSync(live)?hash(l.fs.readFileSync(live)):null,stagedSHA256:hash(bytes)});}
function put(t,k,v){return t.replace(new RegExp('^\\s*'+k+'\\s*=[^\\r\\n]*','gmi'),'')+'\n'+k+' = '+v+'\n';}
const forms={federation:['fconst','fconst2','xfuconst'],borg:['bconst','bconst2','xbuconst'],klingon:['kconst','kconst2','xkuconst'],romulan:['rconst','rconst2','xruconst'],cardassian:['cconst','xcconst2','xcuconst'],dominion:['dconst','xdconst2','xduconst'],bajoran:['bjconst','xbjconst2','xbjuconst'],species8472:['8472_passive','714const','xsuconst']};
const abilityTemplate=l.read(l.index.get('fnxenttoent.odf'));let sprite=readRel('Sprites/gui_global.spr');
const icon=sprite.match(/^b_fnxenttoent[ \t]+([^\r\n]+)/mi);if(!icon)throw Error('NX conversion icon missing');
const ref=[...sprite.slice(0,icon.index).matchAll(/^@reference\s*=\s*(\d+)/gmi)].at(-1)?.[1];if(!ref)throw Error('NX icon reference missing');
const conversions=[],units=[];
for(const[name,file]of l.index){
 const n=name.slice(0,-4),d=l.properties(file),map=forms[d.race];if(!map||n==='xu3bor2'||/^Ferengi/.test(d.unitname||''))continue;
 const tier=/ Basic Constructor/.test(d.unitname||'')?1:/ Advanced Constructor/.test(d.unitname||'')?2:/ Temporal Constructor/.test(d.unitname||'')?3:0;if(!tier||tier===3)continue;
 if(d.is_starbase==='1')throw Error('Fusion unsafe on a starbase-flagged constructor: '+n);
 const rel=l.p.relative(l.root,file).replaceAll('\\','/');let t=readRel(rel);
 const current=Object.entries(d).filter(([k])=>/^weapon\d+$/.test(k));let bank=Math.max(0,...current.map(([k])=>+k.slice(6)));
 const usedSlots=new Set(current.map(([,w])=>l.properties(l.index.get(w.toLowerCase()+'.odf')).buttonslot));
 const usedKeys=new Set(current.map(([,w])=>l.properties(l.index.get(w.toLowerCase()+'.odf')).hotkeylabel));
 let hp=(d.weaponhardpoints1||d.enginestargethardpoints||d.hulltargethardpoints||'root').replaceAll('"','').split(/\s+/)[0];
 const targets=[['up',map[tier],tier+1]];
 for(const[direction,target,targetTier]of targets){
  const id='xcv_'+n+'_'+(direction==='up'?'u':'d');let slot=1;while(usedSlots.has(String(slot)))slot++;usedSlots.add(String(slot));
  let key=direction==='up'?8:9;while(usedKeys.has('HOTKEY_F'+key))key++;if(key>12)throw Error('No free hotkey '+n);usedKeys.add('HOTKEY_F'+key);
  const targetName=l.properties(l.index.get(target+'.odf')).unitname,title=(direction==='up'?'Upgrade':'Downgrade')+' to '+targetName;
  let w=abilityTemplate;for(const[k,v]of Object.entries({wpnName:JSON.stringify(title),tooltip:JSON.stringify(title),verboseTooltip:JSON.stringify('Converts this constructor into '+targetName+'. Free conversion; no research or special energy required.'),buttonSlot:slot,buttonPriority:5,hotkeyLabel:JSON.stringify('HOTKEY_F'+key),fusedClass:JSON.stringify(target),multiReqClass0:JSON.stringify(n),multiReqMin0:1,fusingMetalCost:0,switchToAttack:0}))w=put(w,k,v);
  write('odf/special_weapons/'+id+'.odf',w);t=put(put(t,'weapon'+(++bank),JSON.stringify(id)),'weaponHardpoints'+bank,JSON.stringify(hp));
  sprite=sprite.replace(new RegExp('^b_'+id+'[ \\t]+[^\\r\\n]*','gmi'),'');sprite+='\n@reference='+ref+'\n@tmaterial=default\nb_'+id+' '+icon[1]+'\n';
  conversions.push({ability:id,source:n,target,targetTier,direction,slot,hotkey:'HOTKEY_F'+key,hardpoint:hp,cost:0,researchRequired:false});
 }
 write(rel,t);units.push(n);
}
if(!conversions.length)throw Error('No conversions staged');
for(const tree of ['tech1','earlytech','fulltech','nosci','nospweap','nosuper']){
 const rel='techtree/'+tree+'.tt';let t=readRel(rel);
 for(const c of conversions){t=t.replace(new RegExp('^\\s*'+c.ability+'\\.odf\\s+[^\\r\\n]*','gmi'),'');t+='\n'+c.ability+'.odf 0\n';}
 write(rel,t);
}
write('Sprites/gui_global.spr',sprite);
const report={...prior,status:'staged only; not applied',files:[...files.values()],constructorConversions:conversions,conversionUnits:units,conversionType:'NX hero native fusingweapon, one source ship, upgrade only',conversionCosts:0,conversionResearchRequired:false,breenAndFerengiUnchanged:true,liveGameFilesChanged:false};
l.fs.writeFileSync(l.repo+'/reports/constructor-conversions-staged.json',JSON.stringify(report,null,2));l.fs.writeFileSync(l.repo+'/reports/pending-game-patch-staged.json',JSON.stringify(report,null,2));
console.log(JSON.stringify({constructors:units.length,buttons:conversions.length,files:files.size,liveGameFilesChanged:false},null,2));
