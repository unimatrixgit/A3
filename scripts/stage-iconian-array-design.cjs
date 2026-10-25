const l = require('./odf-lib.cjs');
const out = 'D:/aramada/artwork/iconian-battle-array/v1';
l.fs.mkdirSync(out, {recursive:true});
const baseFile = l.index.get('xbtarray.odf');
const base = l.properties(baseFile);
const factions = [
  ['federation', 'gcorbom', 'Corbomite Reflector'],
  ['klingon', 'gplasmac', 'Ion Cannon'],
  ['romulan', 'grcloak', 'Cloak'],
  ['cardassian', 'gcloak', 'Cloak', 'gplasmabank', 'Plasma Bank Overload'],
  ['dominion', 'gdcteam', "Jem'Hadar Warriors"],
  ['bajoran'], ['species8472'], ['breen'], ['ferengi']
];
const variants = factions.map(([race, first, firstName, second, secondName]) => ({
  race, displayName:'Iconian Battle Array',
  specialAbilities:[...(first ? [{odf:first, name:firstName}]:[]), ...(second ? [{odf:second,name:secondName}]:[])],
  transwarp:false,
  visualTheme:'Shared ancient Iconian geometric core, faction-specific hull and integrated yard and dilithium intake',
  status:first ? 'Ability sources verified; awaiting model implementation' : 'Visual concept; no extra faction ability requested'
}));
for (const v of variants) for (const w of v.specialAbilities)
  if (!l.index.has(w.odf+'.odf')) throw Error('Missing ability '+w.odf);
const stats = Object.fromEntries(Object.entries(base).filter(([k]) => !/^(race|basename|unitname|tooltip|verbosetooltip|possiblecraftnames|event|weapon\d+|weaponhardpoints\d+|builditem\d+)/.test(k)));
const spec = {
  status:'DESIGN ONLY - NOT DEPLOYED', source:baseFile,
  name:'Iconian Battle Array', baselineStats:stats,
  conventionalCost:{dilithium:9500,metal:16500,crew:5000},
  baselineWeapons:{beams:6,torpedoes:4},
  excludedBorgAbilities:['xbarraywarp','xbarrayhold'],
  note:'Original Borg Tactical Battle Array remains separate with its original abilities. Clone combat statistics from the Borg baseline; use faction-matched weapons only after verifying equivalent damage and timing. Species 8472 economy and production require a compatible biomatter implementation. No deployment, tech unlocking or extra abilities are implied by this concept.',
  variants,
  integrationChecklist:['Faction constructor production slot','Faction builders and DIL freighter in array production menu','Tech tree availability','Build and queue icons','Full-image status portrait','Ability energy and buttons','Valid model hardpoints','DIL docking and deposit support','No starter changes','Static validation followed by gameplay test']
};
l.fs.writeFileSync(out+'/design-spec.json',JSON.stringify(spec,null,2)+'\n');
l.fs.copyFileSync(baseFile,out+'/borg-baseline.odf.txt');
console.log('Saved Iconian array design specification; no game files changed.');
