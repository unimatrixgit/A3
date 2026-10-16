const fs=require('fs'),p=require('path');
const R='D:/armadaIII',S='D:/aramada/bajor';
fs.mkdirSync(S,{recursive:true});
const walk=d=>fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(p.join(d,e.name)):[p.join(d,e.name)]);
const idx=new Map(walk(R+'/odf').filter(f=>/\.odf$/i.test(f)).map(f=>[p.basename(f).toLowerCase(),f]));
const read=f=>fs.readFileSync(f,'latin1');
function write(rel,t){let f=R+'/'+rel;fs.mkdirSync(p.dirname(f),{recursive:true});if(fs.existsSync(f))fs.chmodSync(f,0o666);fs.writeFileSync(f,t,'latin1');let out=S+'/overlay/'+rel;fs.mkdirSync(p.dirname(out),{recursive:true});fs.writeFileSync(out,t,'latin1');}
function props(n,seen=new Set()){if(seen.has(n))return {};seen.add(n);let f=idx.get(n+'.odf');if(!f)return {};let t=read(f),v={};for(let m of t.matchAll(/^\s*#include\s+"([^"]+)"/gmi))Object.assign(v,props(m[1].replace(/\.odf$/i,''),seen));for(let m of t.matchAll(/^\s*(\w+)\s*=\s*(.*?)\s*(?:\/\/.*)?$/gm))v[m[1].toLowerCase()]=m[2].replace(/^"|"$/g,'');return v;}
const units=[
 ['bjconst','fconst','Militia Construction Tender','ships',['bjbase','bjmining','bjyard','bjyard2','bjyard3','bjresear','bjturret']],
 ['bjfreight','ffreight','Bajoran Resource Freighter','ships',[]],
 ['bjscout','fscout','Bajoran Scout Vessel','ships',[]],
 ['bjinterceptor','fdestroy','Bajoran Interceptor','ships',[]],
 ['bjassault','fcruise1','Bajoran Assault Vessel','ships',[]],
 ['bjtransport','fantares','Bajoran Antares Transport','ships',[]],
 ['bjnerys','fdestroy','Colonel Kira Nerys - Command Interceptor','ships',[]],
 ['bjbase','fbase','Bajoran Militia Headquarters','stations',['bjconst','bjfreight','bjscout']],
 ['bjmining','fmining','Bajoran Resource Processing','stations',['bjfreight']],
 ['bjyard','fyard','Militia Shipyard I','stations',['bjscout','bjinterceptor','bjtransport']],
 ['bjyard2','fyard2','Militia Shipyard II','stations',['bjassault']],
 ['bjyard3','fyard2','Militia Command Shipyard III','stations',['bjnerys']],
 ['bjresear','fresear','Bajoran Engineering Institute','stations',[]],
 ['bjturret','fturret','Bajoran Defense Emplacement','stations',[]]
];
let spr=read(R+'/Sprites/gui_global.spr'),report=[];
for(let [n,parent,title,folder,menu]of units){let f=idx.get(parent+'.odf');if(!f)throw Error('Missing template '+parent);let v=props(parent),t=read(f).replace(/^\s*(?:secondary)?buildItem\d+\s*=.*$/gmi,'');t+='\r\nrace = "bajoran"\r\nunitName = "'+title+'"\r\ntooltip = "'+title+'"\r\nverboseTooltip = "'+title+'. Bajoran Militia. TV-inspired game adaptation."\r\nbaseName = "'+(v.basename||parent)+'"\r\n';menu.forEach((x,i)=>t+='buildItem'+i+' = "'+x+'"\r\n');if(n==='bjnerys')t+='isHero = 1\r\nmaxHealth = 650\r\ndilithiumCost = 350\r\nmetalCost = 100\r\ncrewCost = 90\r\nbuildTime = 40\r\n';write('odf/'+folder+'/'+n+'.odf',t);let m=spr.match(new RegExp('^\\s*b_'+parent+'\\s+(.+)$','mi'));if(m)spr+='\r\n@reference=64\r\n@tmaterial=default\r\nb_'+n+' '+m[1]+'\r\n';report.push({odf:n,parent,title,model:v.basename||parent,artwork:'compatible existing model; custom Bajoran art pending'});}
write('Sprites/gui_global.spr',spr);
let race=read(R+'/odf/other/fed.odf').replace(/^\s*(?:minimalUnits|standardUnits|superUnits|ctfUnits)\d+\s*=.*$/gmi,'');race+='\r\nname = "bajoran"\r\ndisplayKey = "Bajoran Militia"\r\ninstantActionSlot = 7\r\ninterfaceConfiguration = "gui_bajoran.cfg"\r\ninterfaceSprites = "gui_bajoran.spr"\r\nstandardUnits1 = "bjconst.odf"\r\nstandardUnits2 = "bjconst.odf"\r\nstandardUnits3 = "bjbase.odf"\r\nstandardUnits4 = "bjscout.odf"\r\nstandardUnits5 = "bjnerys.odf"\r\nminimalUnits1 = "bjconst.odf"\r\nminimalUnits2 = "bjnerys.odf"\r\nsuperUnits1 = "bjconst.odf"\r\nsuperUnits2 = "bjbase.odf"\r\nsuperUnits3 = "bjnerys.odf"\r\n';write('odf/other/bajoran.odf',race);
let races=read(R+'/odf/other/races.odf').replace(/numberOfRaces\s*=\s*10/,'numberOfRaces = 11');races+='\r\nrace10 = "bajoran.odf"\r\n';write('odf/other/races.odf',races);
write('odf/other/breen.odf',read(R+'/odf/other/breen.odf').replace(/instantActionSlot\s*=\s*7/,'instantActionSlot = -1'));
write('misc/gui_bajoran.cfg',read(R+'/misc/gui_fed.cfg'));
write('Sprites/gui_bajoran.spr',read(R+'/Sprites/gui_federation.spr'));
for(let name of ['tech1.tt','earlytech.tt','fulltech.tt','nosci.tt','nosuper.tt','nospweap.tt']){let t=read(R+'/techtree/'+name);for(let [n]of units){let deps=name==='fulltech.tt'||n==='bjbase'||n==='bjconst'?[]:[n==='bjnerys'?'bjyard3.odf':'bjbase.odf'];t+='\r\n'+n+'.odf '+deps.length+' '+deps.join(' ')+'\r\n';}write('techtree/'+name,t);}
const ai=['bjbase','bjconst','bjconst','bjmining','bjfreight','bjfreight','bjyard','bjscout','bjinterceptor','bjinterceptor','bjyard2','bjassault','bjresear','bjyard3','bjnerys'];
for(let suffix of ['build_list','instant_action_build_list','offensive_list','defensive_list','endgame_list'])write('AI/AIPs/bajoran_'+suffix+'.aip','#include "aipdef.h"\r\nint checkTechnologyAvailable = 1;\r\nWay_Better_Build_List_Element the_build_list[MAX_ELEMENTS] = {\r\n'+ai.map((x,i)=>'"'+x+'", 1, '+(i<6?0:1)+', -1, 0,').join('\r\n')+'\r\n};\r\n');
fs.writeFileSync(S+'/manifest.json',JSON.stringify({root:R,hero:'Kira Nerys',units:report,selection:'Bajor uses slot 7 in this separate copy; Breen retained but not selectable',runtimeTested:false,artworkComplete:false,sources:['https://memory-alpha.fandom.com/wiki/Bajoran_interceptor','https://memory-alpha.fandom.com/wiki/Bajoran_vessel',"https://memory-alpha.fandom.com/wiki/Kira%27s_interceptor"]},null,2));
fs.appendFileSync('D:/aramada/build.log','\nBajoran prototype installed in D:/armadaIII: 14 units, Kira starting hero, three yards, economy, AI, tech. Custom artwork and runtime test pending.\n');
console.log('Bajoran prototype installed: '+report.length+' units. Custom artwork pending; runtime untested.');
