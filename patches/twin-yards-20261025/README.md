# Standalone faction yard and station patch

Native standalone producers replace the cancelled attached-Nexus experiment. One queue per complete station. Species 8472 and Borg Recycler stay unchanged.

## Compact connected yard revision

All 29 production yards and 10 service-dock definitions now use larger faction
centres with closer bays, textured structural bridges and cylindrical conduits.
Higher-tier centres have additional command hulls; special Federation yards
have distinct auxiliary structures. Every Borg yard uses one assembly bay.

The 34 Borg roster entries are allocated once across the minimum three
14-slot yards: Assembly Matrix 14; Tactical Assembly Matrix 9; Omega
Assimilation Yard 11. Locutus now uses the command yard. The command yard
remains available in No Superweapons mode for Locutus; forbidden Omega ships
remain disabled. Technology prerequisites and 40 AI profiles were checked.

Production-bay sizes use conservative ship-model bounding spans with 25%
clearance allowance. Undecodable legacy SODs use documented estimates in
`../compact-yard-preview/staging-report.json`. Footprints scale with the
model and launch points sit beyond the new bay. These are static estimates;
in-game ship emergence, clearance and repair behaviour still need testing.
Ship stats, Species 8472, HWP models and the Recycler are unchanged by this
revision. Actual staged model renders are in `../compact-yard-preview/`.

The Bajoran revision uses Cardassian central station architecture and copper
plating. Dahkur has Cardassian open drydocks; Shakaar uses the distinct original
advanced Cardassian yard model with staggered bays and a taller command centre.
The Kendra service dock follows the same refitted architecture. No fighter or
ship meshes are attached as decoration. Rosters, costs and combat stats stay
unchanged; icons, size estimates, footprints and exits follow the new geometry.

## Production yards and service docks

| Faction | Production yards | Repair/recrew/decommission dock |
| --- | --- | --- |
| Federation | Antares Fleet Yard; Copernicus Fleet Yard; McKinley Command Yard; Archer Legacy Yard; Sloan Special Projects Yard; Mars Utopia Planetia Yard I; Mars Utopia Planetia Yard II | Starbase 74 Service Dock |
| Borg | Assembly Matrix; Tactical Assembly Matrix; Omega Assimilation Yard | Collective Regeneration Dock |
| Klingon | B'rel Patrol Forge; Vor'cha Assault Forge; Kahless Command Forge | Qo'noS Refit Dock |
| Romulan | Valdore Patrol Yard; D'deridex Fleet Yard; Tal Shiar Command Yard | Ch'Rihan Restoration Dock |
| Cardassian | Hideki Patrol Foundry; Galor Fleet Foundry; Obsidian Command Foundry | Lakarian Service Dock |
| Dominion | Jem'Hadar Attack Yard; Founder Heavy Yard; Great Link Command Yard | Great Link Restoration Dock |
| Bajoran | Dahkur Militia Yard; Shakaar Command Yard | Kendra Service Dock |
| Breen | Thot Gor Fleet Yard | Confederacy Restoration Dock |
| Ferengi (Latinum) | D'Kora Contract Yard; Nog Industrial Exchange | Nog's Service Exchange |
| Ferengi (Borg prices) | D'Kora Contract Yard; Nog Industrial Exchange | Nog's Service Exchange |

Each production/service model has two visible yard wings and one shared native queue. Production yards have two faction beams and one torpedo, with no repair/recrewing/decommissioning. Service docks have repair, recrewing and decommissioning but no production menus.

Federation centres use Earth Spacedock, with spaced double saucers for hero yards and no biodome. Borg centres use the original vanilla Nexus. Other centres use their faction starbase design; yard wings use the original faction yards. Hero centres are larger, and tier silhouettes vary.

## Research and heavy defence

### Research stations

| Faction | Structures |
| --- | --- |
| Federation | Daystrom Engineering Laboratory; Zimmerman Science Laboratory; Cochrane Systems Institute; Omega Directive Laboratory |
| Borg | Collective Modification Node; Tactical Assimilation Laboratory; Unimatrix Optimisation Centre; Omega Perfection Laboratory |
| Klingon | Qu'Vat Weapons Forge; Gre'thor Armory; Imperial Systems Institute |
| Romulan | Covert-Ops Facility; Tal Shiar Facility; Star Empire Research Institute; Sela's Research |
| Cardassian | Military Research Center; Advanced Research Station; Research Institute |
| Dominion | Founder's Engineering Enclave; Vorta Science Laboratory; Jem'Hadar Systems Centre |
| Bajoran | Kendra Engineering Institute; Celestial Temple Observatory; Bajoran Systems Institute |
| Breen | Confederacy Science Laboratory |
| Ferengi (Latinum) | Nagus Commerce Institute |
| Ferengi (Borg prices) | Nagus Commerce Institute |

### Heavy weapons platforms

| Faction | Structures |
| --- | --- |
| Federation | Cyclone Defense Station |
| Borg | Oblivion Defense Nexus |
| Klingon | Klingon HWP |
| Romulan | Heavy Weapons Platform |
| Cardassian | Vekor-class Defense Station |
| Dominion | Nova Cannon |
| Bajoran | Bajoran Cyclone Defense Station |
| Breen | Thot Gor Heavy Weapons Platform |
| Ferengi (Latinum) | Liquidator Heavy Weapons Platform |
| Ferengi (Borg prices) | Liquidator Heavy Weapons Platform |

Research remains at existing standalone stations, with original pod slots/effects and research costs. HWP redesigns retain existing statistics and production menus; new Ferengi and Breen platforms use the established HWP weapon/cost scheme.

## Build buttons and portraits

Blue: production yards. Green: service docks. Yellow: research. Red: HWP fortresses. All have matching unit build buttons, production-queue icons and full RGB status portraits. Production yard icons do not carry repair badges.

## Construction, technology and AI

Constructor menus include retained yards, the separate service dock and new subrace HWPs where a button is free. Retired duplicate factories are removed from construction and disabled in technology trees. Existing research gates remain, and every attack ship has one assigned producer outside HWP/Unicomplex exemptions. All 40 conventional faction AI profiles are dependency ordered, including Ferengi routes.

## Mining-station scaling

The following models and construction footprints increase by 15%. Mining weapons, resource costs, crew, cargo and rates stay unchanged:

xbgmetal3, xfgmetal3, bbase2, bjmining, bjorbital, bmining, borbital, brmining, brorbital, cmining, corbital, dmining, dorbital, fmining, forbital, kmining, korbital, rmining, rorbital, xbgdref, xbgmetal2, xfgdref, xfgmetal2.

## Next patch: hold

- Attack-unit balance by class: weapons, hull/shields, regeneration, energy, build time and resource costs.
- Queen sphere: ordinary sphere appearance, 25% smaller.
- Move only proven unused assets into `D:/armadaIII/redundant files`; preserve map/mission/script/inheritance dependencies. Map folder untouched.

## Runtime status

Static validation does not prove runtime behaviour. New match loading, yard production/launching, service docking and AI construction require in-game testing.
