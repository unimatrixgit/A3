# ArmadaFiles Bajoran graphics search

Scanned 170 ship/station listing pages and all 1,481 linked detail pages; no fetch failures. Full role mappings and compatibility findings are in reports/armadafiles-bajor-texture-search.json.

Relevant downloads (stored outside the game at D:/Xaramada-Modwork/armadafiles-bajor):
- Bajoran Ship Pack: impulse fighter, assault vessel, freighter. https://armadafiles.com/files/armada-2/ships/bajoran-ship-pack-v10/details
- Bajoran Raider with hardpoints: model/hardpoint update without texture files. https://armadafiles.com/files/armada-2/ships/other/bajoran-raider-with-hps/details
- Bajoran Starbase v1 and v2: asteroid-based starbases. https://armadafiles.com/files/armada-2/stations/other/bajoran-starbase/details and https://armadafiles.com/files/armada-2/stations/other/bajoran-starbase-20/details

Credits: Ship Pack by mishkaco, converted by -=WiCKeD=-HARKER; hardpoint update by adm_tyler; starbases by CanadianBorg. Original readmes remain with extracted downloads. Third-party textures/models are not republished in this repository.

No game assets replaced: these models have different texture layouts; current generated Bajor models share a common atlas. Texture-only replacement cannot selectively map their unique source skins onto current geometry. Await scope choice before changing the shared atlas or model/material files. Preserve stats, research and current working DS9 starbase/metal station.

## Selected adaptation installed

User chose option 1: models unchanged, shared texture-only adaptation. New normal and assimilated atlases were generated with the built-in image tool using downloaded Bajoran hull textures as style/panel references while preserving the current four-tile UV layout. This is an adaptation, not a direct copy of incompatible source skins. Only Textures/RGB/bjrhull.tga and bjrhull_B.tga changed. All 2,233 protected ODF/tech/model/icon files matched their pre-update hashes. DS9 textures unaffected. See reports/bajoran-armadafiles-textures-apply.json; original textures backed up locally.
