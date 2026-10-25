# Approved faction visual refresh

This package implements the approved yard, heavy-platform material, shared-core orbital and Ferengi refinery concepts. Original concept sheets and generation prompts are saved here. Faction materials were generated with the built-in image generation tool and are saved in artwork/iconian-battle-array/v1/faction-materials-source.png. Actual game meshes and their model-based icons are produced by scripts/stage-approved-visual-refresh.py.

The pack refreshes 112 model definitions: 40 constructor files including dormant compatibility aliases, 30 yards, 13 orbitals, 2 refineries, 2 Ferengi research stations, and 25 material updates including heavy platforms, research pods and special-purpose yards. It does not add 40 active constructor types or re-enable retired yards. No starting fleets change.

Normal gameplay fields, scale, footprint, construction time, costs, ability energy and production menus are preserved for the visual updates. Exceptions explicitly requested by the user are the Ferengi constructor split, new refinery, and orbital weapons described below. Existing tiered miners and resource-contract research are retained.

## Ferengi constructors

| Unit | Cost | Crew | Build time | Buildings |
| --- | --- | --- | --- | --- |
| Basic Constructor | 500 Latinum | 150 | 40 s | Contract Yard, Service Yard, Commerce Institute, metal orbitals I/II, Dilithium Exchange |
| Advanced Constructor | 700 Latinum | 150 | 55 s | All eight conventional faction starbases and Iconian Battle Array |
| Borg-priced Basic Constructor | 300 dilithium / 200 metal | 150 | 40 s | Same industry functions, using Borg-priced versions |
| Borg-priced Advanced Constructor | 420 dilithium / 280 metal | 150 | 55 s | All eight conventional faction starbases and Borg-priced Ferengi Iconian array |

Both constructor types are offered by the appropriate Ferengi Service Yard. The original Basic Constructor remains at its existing Contract Yard entry. Breen remains a single-constructor subrace. All other active faction tiers are unchanged.

The Dilithium Exchange uses the native MiningStation class and a dedicated Ferengi model. It costs 400 Latinum, or 240 dilithium / 160 metal for the Borg-priced version. Starting crew is 100, maximum crew 200, and construction time 60 seconds. It handles dilithium and points to the appropriate existing tiered Ferengi collector.

All four Ferengi metal orbital variants keep gOrbitalBeam in weapon slot 1, with its original mining hardpoint. Slots 2–4 add two existing Ferengi cruiser beams and one photon launcher, using new dedicated model anchors.

AI profiles already using Ferengi service yards gain the secondary constructor and refinery. All six standard technology trees register the new units, with the normal Ferengi Iconian array moved to the Advanced Constructor prerequisite. Borg variants do not charge Latinum or offer Latinum-only collectors.

## Model compatibility and checks

New mesh exports use the native diffuse texture-layer flag, 256-pixel RGB textures, and small draw meshes. Source skeleton names and animation channels are preserved. Fifteen legacy models had ODF references to absent hardpoints; named centre fallback anchors were added without changing gameplay fields. The repair list is recorded in the patch manifest.

Build icons are rendered from each exported model and retain function badges, category colouring and prominent HWP labels. Portraits use individual full-image RGB textures rather than transparent atlas masks.

Validation passed 14,211 static checks. Installed file hashes are checked against the staged manifest. These checks do not establish gameplay success. In-game construction, mining, docking, repair, research, abilities and AI operation still need testing.
