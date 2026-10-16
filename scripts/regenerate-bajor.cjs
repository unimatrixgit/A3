// Stages a complete faction configuration without touching either running game.
const fs=require('fs'),p=require('path');
const root='D:/armadaIII',repo='D:/aramada',stage='D:/Xaramada-Modwork/bajor-rebuild';
const walk=d=>fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(p.join(d,e.name)):[p.join(d,e.name)]),read=f=>fs.readFileSync(f,'latin1');
const idx=new Map(walk(root+'/odf').filter(f=>/\.odf$/i.test(f)).map(f=>[p.basename(f).toLowerCase(),f]));
function props(n,seen=new Set()){if(seen.has(n)||!idx.has(n))return {};seen.add(n);let t=read(idx.get(n)),v={};for(let m of t.matchAll(/^\s*#include\s+"([^"]+)"/gmi))Object.assign(v,props(m[1].toLowerCase(),seen));for(let m of t.matchAll(/^\s*(\w+)\s*=\s*(.*?)\s*(?:\/\/.*)?$/gm))v[m[1].toLowerCase()]=m[2].replace(/^"|"$/g,'');return v;}
function set(t,k,value){t=t.replace(new RegExp('^\\s*'+k+'\\s*=.*$','gmi'),'');return t+'\r\n'+k+' = '+value+'\r\n';}
function clean(t){let lines=t.replace(/\r\n|\r/g,'\n').split('\n'),last=new Map();lines.forEach((l,i)=>{let m=l.match(/^\s*(\w+)\s*=/);if(m)last.set(m[1].toLowerCase(),i);});return lines.filter((l,i)=>{let m=l.match(/^\s*(\w+)\s*=/);return !m||last.get(m[1].toLowerCase())===i;}).join('\r\n');}
function save(rel,t){let f=stage+'/'+rel;fs.mkdirSync(p.dirname(f),{recursive:true});fs.writeFileSync(f,clean(t),'latin1');}
const definitions=[
 ['bjconst','fconst','Militia Construction Tender','ships','construction',0,'Extrapolated utility tender'],
 ['bjfreight','ffreight','Bajoran Resource Freighter','ships','freighter',1,'TV Bajoran freighter / transport family'],
 ['bjscout','fscout','Bajoran Scout Vessel','ships','scout',2,'TV multi-role Bajoran vessel'],
 ['bjinterceptor','fdestroy','Bajoran Interceptor','ships','destroyer',3,'TV interceptor'],
 ['bjassault','fassault','Bajoran Assault Vessel','ships','assault',4,'TV multi-role assault vessel'],
 ['bjtransport','fantares','Bajoran Antares Transport','ships','transport',5,'TV Antares transport family'],
 ['bjnerys','fdestroy','Colonel Kira Nerys - Command Interceptor','ships','hero',6,"TV Kira's command interceptor"],
 ['bjbase','fbase','Bajoran Militia Headquarters','stations','base',7,'Extrapolated Bajoran orbital headquarters'],
 ['bjmining','fmining','Bajoran Resource Processing Facility','stations','mining',8,'Extrapolated industrial station'],
 ['bjyard','fyard','Militia Shipyard I','stations','yard',9,'Extrapolated open-frame construction dock'],
 ['bjyard2','fyard2','Militia Shipyard II','stations','yard2',10,'Extrapolated advanced construction dock'],
 ['bjyard3','fyard2','Militia Command Shipyard III','stations','yard3',11,'Extrapolated command construction dock'],
 ['bjresear','fresear','Bajoran Engineering Institute','stations','research',12,'Extrapolated research station'],
 ['bjturret','fturret','Bajoran Defense Emplacement','stations','turret',13,'Extrapolated local defense'],
 ['bjraider','fdanube','Bajoran Sub-Impulse Raider','ships','raider',2,'TV sub-impulse raider, adapted for map travel'],
 ['bjlightship','fscout','Bajoran Lightship','ships','lightship',2,'TV solar-sail vessel, civilian survey adaptation'],
 ['bjcolony','fcolony','Bajoran Colonial Transport','ships','colony',5,'Extrapolated transport-family colony ship'],
 ['bjcargo','fcargo','Bajoran Merchant Transport','ships','cargo',1,'Extrapolated transport-family trade ship'],
 ['bjrepair','fsrepair','Bajoran Engineering Support Vessel','ships','repair',0,'Extrapolated repair tender'],
 ['bjcruiser','fcruise1','Bajoran Militia Cruiser','ships','cruiser',4,'Extrapolated enlarged assault-vessel hull'],
 ['bjtorpedo','fcruise2','Bajoran Torpedo Cruiser','ships','torpedo',4,'Extrapolated assault hull with torpedo pods'],
 ['bjfrigate','ffrigate','Bajoran Militia Frigate','ships','frigate',3,'Extrapolated interceptor escort family'],
 ['bjartillery','fcruise3','Bajoran Long-Range Defense Vessel','ships','artillery',4,'Extrapolated standoff assault hull'],
 ['bjbattle','fbattle','Bajoran Militia Battleship','ships','battleship',4,'Extrapolated heavy assault-family flagship'],
 ['bjspecial','fspecial','Bajoran Science Support Vessel','ships','special',12,'Extrapolated sensor/engineering support hull'],
 ['bjsuper','fbattle','Bajoran Strategic Command Vessel','ships','super',6,'Extrapolated heavy command hull, not a canon class'],
 ['bjresear2','fresear2','Bajoran Advanced Research Institute','stations','research2',12,'Extrapolated advanced research station'],
 ['bjupgrade','fupgrade','Bajoran Systems Upgrade Center','stations','upgrade',12,'Extrapolated systems engineering station'],
 ['bjsensor','fsensor','Bajoran Sensor Array','stations','sensor',12,'Extrapolated long-range sensor installation'],
 ['bjorbital','forbital','Bajoran Orbital Processing Facility','stations','orbital',8,'Extrapolated planetary metal facility'],
 ['bjtrading','ftrading','Bajoran Trade Center','stations','trading',7,'Extrapolated merchant orbital hub'],
 ['bjturret2','fturret2','Bajoran Torpedo Defense Emplacement','stations','turret2',13,'Extrapolated heavy defense'],
 ['bjsuperlab','fresear2','Bajoran Strategic Research Center','stations','superlab',12,'Extrapolated strategic command research']
];
const units=definitions.map(([odf,parent,title,folder,role,iconCell,design])=>({odf,parent,title,folder,role,iconCell,design,model:odf}));
for(let n of [1,2,3,4,5,6,7,8,9,11,12,13,14,15,16,21,22,23,24,25]){if(!idx.has('fedpod'+n+'.odf'))continue;units.push({odf:'bjpod'+n,parent:'fedpod'+n,title:'Bajoran '+({1:'Tactical Systems',2:'Shield Modulation',3:'Sensor Countermeasures',4:'Defensive Systems',5:'Tachyon Detection',6:'Engineering Support',7:'Advanced Deflector',8:'Advanced Sensors',9:'Command Systems',11:'Weapons II',12:'Shields II',13:'Sensors II',14:'Engines II',15:'Life Support II',16:'Support Systems',21:'Weapons III',22:'Shields III',23:'Sensors III',24:'Engines III',25:'Life Support III'}[n]||'Research'),folder:'stations',role:'pod',iconCell:12,design:'Extrapolated technology pod',model:'bjpod'+n});}
const unitIndex=new Map(units.map(u=>[u.odf,u]));
const menus={bjconst:['bjbase','bjmining','bjyard3','bjyard','bjyard2','bjresear','bjresear2','bjupgrade','bjsensor','bjorbital','bjtrading','bjturret','bjturret2','bjsuperlab'],bjbase:['bjconst','uconst','bjfreight','bjcargo','bjrepair','bjcolony','bjscout'],bjmining:['bjfreight'],bjyard:['bjscout','bjinterceptor','bjraider','bjtransport','bjcolony','bjlightship','bjassault'],bjyard2:['bjcruiser','bjtorpedo','bjfrigate','bjartillery','bjbattle','bjspecial'],bjyard3:['bjnerys','bjsuper','bjbattle','bjspecial'],bjresear:['bjpod1','bjpod2','bjpod3','bjpod4','bjpod5','bjpod16'],bjresear2:['bjpod6','bjpod7','bjpod8','bjpod9'],bjupgrade:['bjpod11','bjpod12','bjpod13','bjpod14','bjpod15'],bjtrading:['bjcargo'],bjsuperlab:['bjpod6','bjpod9']};
const dependencies={bjconst:[],bjbase:[],uconst:[],bjfreight:['bjmining'],bjcargo:['bjtrading'],bjrepair:['bjyard'],bjcolony:['bjyard','bjresear'],bjscout:['bjbase'],bjinterceptor:['bjyard'],bjraider:['bjyard'],bjtransport:['bjyard'],bjlightship:['bjyard'],bjassault:['bjyard','bjresear'],bjcruiser:['bjyard2'],bjtorpedo:['bjyard2','bjresear'],bjfrigate:['bjyard2'],bjartillery:['bjyard2','bjresear2'],bjbattle:['bjyard2','bjupgrade'],bjspecial:['bjyard2','bjresear2'],bjsuper:['bjyard3','bjsuperlab'],bjnerys:['bjyard3'],bjmining:[],bjyard:['bjbase'],bjresear:['bjbase','bjyard'],bjyard2:['bjyard','bjresear'],bjyard3:['bjyard','bjresear'],bjresear2:['bjyard2','bjresear'],bjupgrade:['bjresear','bjresear2'],bjsensor:['bjbase'],bjorbital:['bjbase'],bjtrading:['bjbase'],bjturret:['bjbase'],bjturret2:['bjresear'],bjsuperlab:['bjresear2','bjyard2']};
for(let u of units.filter(u=>u.role==='pod')){let n=+u.odf.replace('bjpod','');dependencies[u.odf]=n>=21?['bjupgrade','bjpod'+(n-10)]:n>=11&&n<=15?['bjupgrade']:n<=5||n===16?['bjresear']:['bjresear2'];}
const originalTech=new Map([...read(root+'/techtree/tech1.tt').matchAll(/^\s*(\S+\.odf)\s+(-?\d+)([^\r\n]*)/gmi)].map(m=>[m[1].toLowerCase(),m[3].trim().split(/\s+/).filter(Boolean)]));
let specialWeapons=new Map();
for(let u of units){let existing=idx.get(u.odf+'.odf'),source=existing||idx.get(u.parent+'.odf');if(!source)throw Error('Missing source '+u.parent);let t=read(source),v=props(p.basename(source).toLowerCase());
 t=t.replace(/^\s*(?:secondary)?buildItem\d+\s*=.*$/gmi,'');
 for(let [k,val]of Object.entries({unitName:'"'+u.title+'"',tooltip:'"'+u.title+'"',verboseTooltip:'"'+u.title+'. '+u.design+'."',race:'"bajoran"',baseName:'"'+u.model+'"',ScaleSOD:u.role==='pod'?'0.2':'1.0'}))t=set(t,k,val);
 for(let [i,n]of (menus[u.odf]||[]).entries())t+='\r\nbuildItem'+i+' = "'+n+'"\r\n';
 if(u.odf==='bjupgrade')for(let [i,n]of [21,22,23,24,25].entries())t+='\r\nsecondaryBuildItem'+i+' = "bjpod'+n+'"\r\n';
 if(u.role==='hero')t=set(set(t,'isHero','1'),'label','"Colonel Kira Nerys"');
 if(u.role==='lightship'){t=t.replace(/^\s*weapon\d+\s*=.*$/gmi,'');t=set(set(t,'canAttack','0'),'transporter','0');t=set(t,'verboseTooltip','"Bajoran solar lightship. Civilian survey vessel; unarmed. Game adaptation of the TV lightship."');}
 if(u.role==='super'&&!existing){for(let key of ['maxHealth','dilithiumCost','metalCost','crewCost','officerCost','buildTime'])if(+v[key.toLowerCase()]>0)t=set(t,key,String(Math.round(+v[key.toLowerCase()]*1.3)));}
 // Clone special-weapon tech names, so Bajor never requires a Federation research pod.
 if(u.folder==='ships'&&u.role!=='lightship')for(let [key,name]of Object.entries(v)){if(!/^weapon\d+$/.test(key))continue;let w=idx.get(name.toLowerCase()+'.odf');if(!w||props(name.toLowerCase()+'.odf').special!=='1')continue;let clone='xbj_'+name.toLowerCase();specialWeapons.set(clone,{source:name,deps:(originalTech.get(name.toLowerCase()+'.odf')||[]).map(x=>x.replace(/^fedpod/i,'bjpod').replace(/^f(?:resear2|resear|upgrade)\.odf$/i,x=>x.replace(/^f/,'bj')))});t=set(t,key,'"'+clone+'"');}
 save('odf/'+u.folder+'/'+u.odf+'.odf',t);
}
for(let [name,w]of specialWeapons){save('odf/weapons/'+name+'.odf','#include "'+w.source+'.odf"\r\n');dependencies[name]=w.deps.map(d=>d.replace(/\.odf$/i,''));}
for(let name of fs.readdirSync(root+'/techtree').filter(n=>/\.tt$/i.test(n))){let t=read(root+'/techtree/'+name);for(let [n,deps]of Object.entries(dependencies)){t=t.replace(new RegExp('^\\s*'+n+'\\.odf\\s+.*$','gmi'),'');let d=name==='fulltech.tt'?[]:deps;t+='\r\n'+n+'.odf '+d.length+(d.length?' '+d.map(x=>x+'.odf').join(' '):'')+'\r\n';}save('techtree/'+name,t);}
let race=read(root+'/odf/other/bajoran.odf').replace(/^\s*(?:standardUnits|minimalUnits|superUnits)\d+\s*=.*$/gmi,'');let starts={standardUnits:['bjconst','bjconst','bjbase','bjscout','bjnerys'],minimalUnits:['bjconst','bjnerys'],superUnits:['bjconst','bjconst','bjbase','bjnerys']};for(let [key,list]of Object.entries(starts))list.forEach((n,i)=>race+='\r\n'+key+(i+1)+' = "'+n+'.odf"\r\n');save('odf/other/bajoran.odf',race);
const ai=[['bjbase',1,1],['bjmining',1,0],['bjfreight',2,0],['bjyard',1,2],['bjconst',2,0],['bjinterceptor',4,0],['bjresear',1,0],['bjassault',3,0],['bjcolony',1,0],['bjorbital',1,0],['bjtrading',1,0],['bjcargo',2,0],['bjturret',2,0],['bjsensor',1,0],['bjyard2',1,3],['bjcruiser',3,0],['bjtorpedo',2,0],['bjfrigate',2,0],['bjrepair',1,0],['bjresear2',1,4],['bjupgrade',1,5],['bjpod11',1,0],['bjpod12',1,0],['bjbattle',3,0],['bjspecial',1,0],['bjartillery',2,0],['bjyard3',1,6],['bjnerys',1,0],['bjsuperlab',1,0],['bjsuper',1,0],['bjpod21',1,0],['bjpod22',1,0],['bjfreight',4,0],['bjcruiser',6,0],['bjbattle',6,0]];
for(let suffix of ['build_list','instant_action_build_list','offensive_list','defensive_list','endgame_list'])save('AI/AIPs/bajoran_'+suffix+'.aip','#include "aipdef.h"\r\nint checkTechnologyAvailable = 1;\r\nWay_Better_Build_List_Element the_build_list[MAX_ELEMENTS] =\r\n{\r\n'+ai.map(([n,count,tech])=>'"'+n+'", '+count+', 0, '+count+', '+tech+',').join('\r\n')+'\r\n};\r\n');
let next={root,hero:'Kira Nerys',units,dependencies,menus,ai,specialWeapons:[...specialWeapons.keys()],startingUnits:starts,stage,applied:false,runtimeTested:false,sourcePolicy:'TV designs where available; other roles explicitly extrapolated.',sources:['https://memory-alpha.fandom.com/wiki/Bajoran_interceptor','https://memory-alpha.fandom.com/wiki/Bajoran_vessel','https://memory-alpha.fandom.com/wiki/Bajoran_raider','https://memory-alpha.fandom.com/wiki/Bajoran_lightship']};fs.writeFileSync(repo+'/bajor/rebuild-manifest.json',JSON.stringify(next,null,2));
let s=JSON.parse(fs.readFileSync(repo+'/status.json','utf8').replace(/^\uFEFF/,''));s.current='Bajoran expanded configuration staged: '+units.filter(u=>u.folder==='ships').length+' ship roles, '+units.filter(u=>u.folder==='stations'&&u.role!=='pod').length+' buildings, '+units.filter(u=>u.role==='pod').length+' research pods, Universal Assembler production, five new AI profiles, and tech entries. Model regeneration and validation in progress; not applied yet.';let step=s.steps.find(x=>x.label==='Bajoran rebuild: full ship/building roster and Universal Assembler');if(step)step.done=true;fs.writeFileSync(repo+'/status.json',JSON.stringify(s,null,2));fs.appendFileSync(repo+'/build.log','\n['+new Date().toISOString()+'] '+s.current+'\n');console.log(s.current);
