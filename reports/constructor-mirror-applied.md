# Applied constructor, mirror yard and resource patch

Applied only to D:/armadaIII. Source files mirrored to D:/aramada/bajor/overlay. File validation passed; gameplay has not been tested.

## Constructor roles

T1: mining, standard yards, research and upgrade facilities. T2: defenses, hero/Omega and Mirror Universe yards. T3: all eight main faction starbases, faction special structures and Ferengi facilities. Extra T3 variants preserve overflow. Legacy constructor files remain compatible aliases. Constructors carry no combat weapons. All Borg constructors retain Transwarp Drive, 1,000 special energy and10 energy recharge per second.

Standard constructor prices: T1 125 dilithium/25 metal, T2 200/100, T3 300/200. Starting crew150; build times20/30/40 seconds. Ferengi constructors cost500 latinum; Borg-priced Ferengi constructors cost300 dilithium/200 metal. Species8472 constructors use biomatter. Existing hulls, model proportions and worker-bee systems are preserved.

## Starbase prices

All strategic conventional starbases cost1,500 dilithium +1,500 metal, with150 starting crew and unchanged maximum crew. Other resource costs are zero. Species8472 retains its biomatter economy. Heavy weapons platforms, tactical arrays, special shipyards and ships implemented through the starbase engine class are excluded from this price change.

## Mirror Universe

59 counterparts are built through11 normal shipyards, including two Federation yards. Ordinary production gives the building player ownership. The failed summon abilities and mirror-research menus are removed from gameplay; their dormant definitions are disabled in all six technology trees. Native abilities remain. Mirror ships retain double normal damage,75% health and125% model size. Their resource prices and build times are125% of the corresponding original hero. Hugh uses the battle-pack cube; the Queen counterpart retains its sphere model. No starting fleets were changed.

## Resource research

Two tiers unlock new equipment variants: +50% and +100% over the base extraction rate. Existing units do not upgrade retroactively. Normal Ferengi research covers dilithium/metal/latinum; Borg contracts cover dilithium/metal only. Research costs900/1350 latinum, or the same value split60% dilithium and40% metal for Borg contracts.

Species8472 has its own Biomatter Metabolism Institute, built by T1. It uses Chiletrek's Species8472 Pack07 research station/pod models and textures under unique filenames. Research costs900/1350 biomatter and unlocks enhanced Collectors on the Active Embryo. Biomatter mining yield and extraction conversion improve50%/100%; other mining beams and storage capacities are unchanged. No Ferengi facilities or units were added to8472.

## AI and interface

45 faction skirmish/strategy build lists order the correct constructors before their buildings. Eligible factions use the Ferengi contract, service and research facilities; Borg plans use the Borg-priced catalog and omit latinum research/collectors. Every faction builds its mirror yards and a counterpart from each. Icons distinguish constructor tiers, mirror production and resource research tiers.

## Applied constructor menus

### federation — T1 (`fconst`)

- San Fransisco Class (`fyard0`)
- Algol Class (`fyard`)
- Sacramento Class (`fyard2`)
- Kiluauea Class (`fmining`)
- Spear Class (`forbital`)
- Iroquois Class (`ftrading`)
- Blue Ridge Class (`fresear`)
- Sirius Class (`fresear2`)
- Mars Class (`fupgrade`)
- Subspace Relay (`fsensor`)
- Remmla class (`fremmeler`)
- Argus Array (`fargus`)

### federation — T2 (`fconst2`)

- Enterprise Legacy Yard (`xflegacyyard`)
- Mark III (`fturret`)
- Mark VI (`fturret2`)
- Cyclone Defense Station (`fhwp`)
- Laforge's Shipyard (`fyard3`)
- Section 31 Shipyard (`s31yard`)
- Omega Research Laboratory (`xfomegalab`)
- mryfeda (`mryfeda`)
- mryfedb (`mryfedb`)

### federation — T3 (`xfuconst`)

- Nexus (`bbase`)
- SpaceDock (`fbase`)
- Starbase (`kbase`)
- Starbase (`rbase`)
- Terok Nor (`cbase`)
- Dominion Cloning Facility/Starbase (`dbase`)
- Breen Starbase (`brbase`)
- Deep Space 9 (`bjbase`)
- Regula class (`fregula`)
- Deep Space 9 (`fds9`)
- Spartan Class (`foutpost`)
- Darius Class (`fbase2`)
- Midas Array (`fmidas`)

### federation — T3 (`xu3fed2`)

- Jupiter Station (`fjupiter`)
- Manheim Class (`fsuperbl`)

### borg — T1 (`bconst`)

- Assembly Matrix (`byard`)
- Detection Array (`bsensor`)
- Resource Processing Node (`bmining`)
- Modification Center (`bresear`)
- Technology Node (`bresear2`)
- Adv. Assembly Matrix (`byard2`)
- Orbital Base (`bbase2`)
- Recycler (`brecycle`)
- Ship Upgrade Facility (`bupgrade`)

### borg — T2 (`bconst2`)

- Energy Cannon (`bturret`)
- Torpedo Turret (`bturret2`)
- Advanced Assimilated Matrix (`byard3`)
- Oblivion Defense Nexus (`bhwp`)
- Omega Research Laboratory (`xbomegalab`)
- Borg Tactical Battle Array (`xbtarray`)
- mryborg (`mryborg`)

### borg — T3 (`xbuconst`)

- Nexus (`bbase`)
- SpaceDock (`fbase`)
- Starbase (`kbase`)
- Starbase (`rbase`)
- Terok Nor (`cbase`)
- Dominion Cloning Facility/Starbase (`dbase`)
- Breen Starbase (`brbase`)
- Deep Space 9 (`bjbase`)
- Transwarp Gate (`bsuperbl`)
- Auto Assimilator (`bassturr`)
- Technology Assimilator (`btechass`)
- Harvester Station (`xbharvest`)
- Assimilation Station (`xbassimst`)

### borg — T3 (`xu3bor2`)

- Borg Transwarp Hub (`hub`)
- Mercenary Ferengi Contract Yard (`xbgmerc`)
- Central Unicomplex (`unicomplex`)

### klingon — T1 (`kconst`)

- Shipyard (`kyard`)
- Sensor Array (`ksensor`)
- Dilithium Refinery (`kmining`)
- Weapons Center (`kresear`)
- Gre'thor Armory (`kresear2`)
- Imperial Shipyard (`kyard2`)
- Orbital Processing Facility (`korbital`)
- Trading Station (`ktrading`)
- Imperial Research Institute (`kupgrade`)

### klingon — T2 (`kconst2`)

- Disruptor Cannon (`kturret`)
- Torpedo Turret (`kturret2`)
- Kahless' Forge (`kyard3`)
- Imperial Shipyard (`kimpyard`)
- Klingon HWP (`khwp`)
- mrykling (`mrykling`)

### klingon — T3 (`xkuconst`)

- Nexus (`bbase`)
- SpaceDock (`fbase`)
- Starbase (`kbase`)
- Starbase (`rbase`)
- Terok Nor (`cbase`)
- Dominion Cloning Facility/Starbase (`dbase`)
- Breen Starbase (`brbase`)
- Deep Space 9 (`bjbase`)
- Shockwave Station (`ksuperbl`)
- Imperial Starbase (`kimpbase`)
- Ty'Go'Kor (`kbase2`)
- Mercenary Ferengi Contract Yard (`xfgmerc`)
- Outpost (`koutpost`)

### romulan — T1 (`rconst`)

- Shipyard (`ryard`)
- Spy Satellite (`rsensor`)
- Mining Facility (`rmining`)
- Covert-Ops Facility (`rresear`)
- Tal Shiar Facility (`rresear2`)
- Advanced Shipyard (`ryard2`)
- Orbital Processing Facility (`rorbital`)
- Trading Station (`rtrading`)
- Tal Shiar Sensor Array (`rtsens`)
- Sela's Research (`xselaresearch`)
- Star Empire Research Institute (`rupgrade`)

### romulan — T2 (`rconst2`)

- Plasma Cannon (`rturret`)
- Torpedo Turret (`rturret2`)
- Raptor's Talon Shipyard (`ryard3`)
- Heavy Weapons Platform (`rhwp`)
- mryrom (`mryrom`)

### romulan — T3 (`xruconst`)

- Nexus (`bbase`)
- SpaceDock (`fbase`)
- Starbase (`kbase`)
- Starbase (`rbase`)
- Terok Nor (`cbase`)
- Dominion Cloning Facility/Starbase (`dbase`)
- Breen Starbase (`brbase`)
- Deep Space 9 (`bjbase`)
- Phoenix Facility (`rsuperbl`)
- Tal Shiar HQ (`rbase2`)
- Mercenary Ferengi Contract Yard (`xfgmerc`)

### cardassian — T1 (`cconst`)

- Shipyard (`cyard`)
- Sensor Array (`csensor`)
- Mining Station (`cmining`)
- Military Research Center (`cresear`)
- Advanced Research Station (`cresear2`)
- Advanced Shipyard (`cyard2`)
- Advanced Robotics Institute (`cardassian_super_station`)
- Orbital Processing Facility (`corbital`)
- Trading Station (`ctrading`)
- Dominion Shipyard (`domyard`)
- Research Institute (`cupgrade`)

### cardassian — T2 (`xcconst2`)

- Defense Turret (`cturret`)
- Heavy Plasma Turret (`cturret2`)
- Obsidian Command Yard (`cyard3`)
- Vekor-class Defense Station (`chwp`)
- Obsidian Order Shipyard (`cobyard`)
- mrycard (`mrycard`)

### cardassian — T3 (`xcuconst`)

- Nexus (`bbase`)
- SpaceDock (`fbase`)
- Starbase (`kbase`)
- Starbase (`rbase`)
- Terok Nor (`cbase`)
- Dominion Cloning Facility/Starbase (`dbase`)
- Breen Starbase (`brbase`)
- Deep Space 9 (`bjbase`)
- Dominion Starbase (`dombase`)
- Dominion Oupost (`domabase`)
- Nor Class Station (`cstation`)
- Mercenary Ferengi Contract Yard (`xfgmerc`)

### dominion — T1 (`dconst`)

- Dominion Shipyard (`dyard`)
- Dominion Sensor Satellite (`dsensor`)
- Mining Station (`dmining`)
- Dominion Research Station (`dresear`)
- Dominion Advanced Science Station (`dresear2`)
- Dominion Advanced Shipyard (`dyard2`)
- Orbital Mining Facility (`dorbital`)
- Trading Station (`dtrading`)
- Dominion Ship Upgrade Center (`dupgrade`)

### dominion — T2 (`xdconst2`)

- Dominion Phaser Turret (`dturret`)
- Dominion Torpedo Turret (`dturret2`)
- Dominion Dreadnought Construction Yard (`dsuperbl`)
- Nova Cannon (`dturret3`)
- Founders' Command Yard (`dyard3`)
- mrydom (`mrydom`)

### dominion — T3 (`xduconst`)

- Nexus (`bbase`)
- SpaceDock (`fbase`)
- Starbase (`kbase`)
- Starbase (`rbase`)
- Terok Nor (`cbase`)
- Dominion Cloning Facility/Starbase (`dbase`)
- Breen Starbase (`brbase`)
- Deep Space 9 (`bjbase`)
- Dominion Artificial Wormhole Creator (`zsuperbl`)
- Mercenary Ferengi Contract Yard (`xfgmerc`)

### breen — T1 (`brconst`)

- Breen Shipyard (`bryard`)
- Breen Mining Station (`brmining`)
- Breen Research Facility (`brresear`)
- Breen Science Station (`brresear2`)
- Breen Advanced Shipyard (`bryard2`)
- Breen Orbital Processing Facility (`brorbital`)

### breen — T2 (`xbrconst2`)

- Thot's Command Dock (`bryard3`)
- mrybreen (`mrybreen`)

### breen — T3 (`xbruconst`)

- Nexus (`bbase`)
- SpaceDock (`fbase`)
- Starbase (`kbase`)
- Starbase (`rbase`)
- Terok Nor (`cbase`)
- Dominion Cloning Facility/Starbase (`dbase`)
- Breen Starbase (`brbase`)
- Deep Space 9 (`bjbase`)
- Mercenary Ferengi Contract Yard (`xfgmerc`)

### bajoran — T1 (`bjconst`)

- Militia Shipyard I (`bjyard`)
- Militia Shipyard II (`bjyard2`)
- Bajoran Resource Processing Facility (`bjmining`)
- Bajoran Orbital Processing Facility (`bjorbital`)
- Bajoran Trade Center (`bjtrading`)
- Bajoran Engineering Institute (`bjresear`)
- Bajoran Advanced Research Institute (`bjresear2`)
- Bajoran Systems Upgrade Center (`bjupgrade`)
- Bajoran Sensor Array (`bjsensor`)

### bajoran — T2 (`xbjconst2`)

- Bajoran Defense Emplacement (`bjturret`)
- Bajoran Torpedo Defense Emplacement (`bjturret2`)
- Bajoran Cyclone Defense Station (`bjhwp`)
- Dahkur Command Shipyard (`bjyard3`)
- mrybajor (`mrybajor`)

### bajoran — T3 (`xbjuconst`)

- Nexus (`bbase`)
- SpaceDock (`fbase`)
- Starbase (`kbase`)
- Starbase (`rbase`)
- Terok Nor (`cbase`)
- Dominion Cloning Facility/Starbase (`dbase`)
- Breen Starbase (`brbase`)
- Deep Space 9 (`bjbase`)
- Prophets' Command Sanctuary (`bjsuperlab`)
- Bajoran Asteroid Outpost (`xbjoutpost`)
- Mercenary Ferengi Contract Yard (`xfgmerc`)

### species8472 — T1 (`8472_passive`)

- Shipyard (`714syard`)
- Transmuter (`8472_transmuter`)
- Enhancer (`8472_basicresearch`)
- Biogenesis Core (`8472_advancedresearch`)
- Metogenesis Core (`8472_shipupgraderesearch`)
- Fluidic Gate (`8472_fluidicgate`)
- Mine (`8472_mine`)
- xsbiolab (`xsbiolab`)

### species8472 — T2 (`714const`)

- Beam Turret (`714turr`)
- Advanced Hatchery (`xhs_yard3`)
- Sentinel (`8472_sentinel`)
- mry8472 (`mry8472`)

### species8472 — T3 (`xsuconst`)

- Nexus (`bbase`)
- SpaceDock (`fbase`)
- Starbase (`kbase`)
- Starbase (`rbase`)
- Terok Nor (`cbase`)
- Dominion Cloning Facility/Starbase (`dbase`)
- Breen Starbase (`brbase`)
- Deep Space 9 (`bjbase`)
- Mother (`8472_mothership`)

### ferengi — T3 (`xfgconst`)

- Nexus (`bbase`)
- SpaceDock (`fbase`)
- Starbase (`kbase`)
- Starbase (`rbase`)
- Terok Nor (`cbase`)
- Dominion Cloning Facility/Starbase (`dbase`)
- Breen Starbase (`brbase`)
- Deep Space 9 (`bjbase`)
- Mercenary Ferengi Contract Yard (`xfgmerc`)
- Mercenary Ferengi Service Yard (`xfgserv`)
- Ferengi Commerce Institute (`xfgresearch`)
- Mercenary Ferengi Advanced Metal Orbital (`xfgmetal2`)
- mryfer (`mryfer`)

### ferengi — T3 (`xu3fer2`)

- xfgmetal3 (`xfgmetal3`)

### borg_ferengi — T3 (`xbgconst`)

- Nexus (`bbase`)
- SpaceDock (`fbase`)
- Starbase (`kbase`)
- Starbase (`rbase`)
- Terok Nor (`cbase`)
- Dominion Cloning Facility/Starbase (`dbase`)
- Breen Starbase (`brbase`)
- Deep Space 9 (`bjbase`)
- Mercenary Ferengi Contract Yard (`xbgmerc`)
- Mercenary Ferengi Service Yard (`xbgserv`)
- Ferengi Commerce Institute (`xbgresearch`)
- Mercenary Ferengi Advanced Metal Orbital (`xbgmetal2`)
- xbgmetal3 (`xbgmetal3`)

## Validation

259 ODFs, 216 models, 130 build buttons, six technology trees and45 AI plans checked. No new validation errors. Existing source warnings remain:

- fbyard: unchanged source hardpoint absent: build (buildhardpoint)
- fbyard: unchanged source hardpoint absent: hp01 (weaponhardpoints1)
- fbyard: unchanged source hardpoint absent: hp02 (weaponhardpoints2)
- fbyard: unchanged source hardpoint absent: hp03 (weaponhardpoints3)
- fbyard: unchanged source hardpoint absent: hp04 (weaponhardpoints4)
- fentc: pre-existing damagesm texture reference
- kbase: unchanged source hardpoint absent: build (buildhardpoint)
- mrc012: pre-existing damagesm texture reference
- mrc037: pre-existing damagesm texture reference
- xhfgarrett: pre-existing damagesm texture reference

Backup: D:\Xaramada-Modwork\backups\constructor-mirror-20261024-035048
