# AI build-order recovery and standard starts

Applied to D:/armadaIII only. Backups and source copies saved; gameplay is not yet verified.

The previous constructor rewrite inserted advanced yards/Temporal Constructors ahead of the basic yards and research required to obtain them, including before the already-owned starting starbase goal. This patch seeds each plan from the actual starting fleet, opens with economy and basic production, and recursively schedules each missing research prerequisite and a reachable producer before its target. Retired constructor names in technology requirements are redirected to their currently produced equivalents.

All45 faction skirmish/strategy plans passed a separate sequential dependency audit and remain below the200-entry limit. Existing duplicate goals are compacted. Legacy tech-level phase fields are normalized to0; explicit technology-tree prerequisites govern progression. This is a static reachability check, not a demonstration of live AI behavior or resource affordability.

Ferengi and mirror branches remain present. Dominion additionally develops a complete Breen branch using its free starting Breen constructor, including all three Breen yards and its mirror yard.

## Standard starting fleets

| Faction | Fleet |
|---|---|
| federation | fconst, fconst, fconst2, fbase |
| borg | bconst, bconst, bconst2, bbase |
| klingon | kconst, kconst, kconst2, kbase |
| romulan | rconst, rconst, rconst2, rbase |
| cardassian | cconst, cconst, xcconst2, cbase |
| dominion | dconst, dconst, xdconst2, dbase, brconst |
| breen | brconst, brconst, brbase |
| bajoran | bjconst, bjconst, xbjconst2, bjbase, xfgconst |
| species8472 | 8472_passive, 8472_passive, 714const, 8472_mothership |

All main factions except Breen start with2 Basic Constructors,1 Advanced Constructor and1 starbase. Dominion additionally receives1 Breen constructor. Bajor additionally receives1 free Ferengi Temporal Constructor; purchase costs remain unchanged. Breen retains its single constructor type and starts with2 copies plus its starbase. Species8472 uses its existing biological constructor equivalents. Scouts are no longer included in standard starts. Minimal/Super definitions are unchanged. No heroes were added to any starts; icons and ship stats were not edited.

## AI plan sizes

- bajoran_build_list.aip: 96 rows, no dependency-order failures.
- bajoran_defensive_list.aip: 97 rows, no dependency-order failures.
- bajoran_endgame_list.aip: 89 rows, no dependency-order failures.
- bajoran_instant_action_build_list.aip: 105 rows, no dependency-order failures.
- bajoran_offensive_list.aip: 96 rows, no dependency-order failures.
- borg_build_list.aip: 84 rows, no dependency-order failures.
- borg_defensive_list.aip: 85 rows, no dependency-order failures.
- borg_endgame_list.aip: 84 rows, no dependency-order failures.
- borg_instant_action_build_list.aip: 84 rows, no dependency-order failures.
- borg_offensive_list.aip: 84 rows, no dependency-order failures.
- breen_build_list.aip: 52 rows, no dependency-order failures.
- breen_defensive_list.aip: 52 rows, no dependency-order failures.
- breen_endgame_list.aip: 52 rows, no dependency-order failures.
- breen_instant_action_build_list.aip: 52 rows, no dependency-order failures.
- breen_offensive_list.aip: 52 rows, no dependency-order failures.
- cardassian_build_list.aip: 87 rows, no dependency-order failures.
- cardassian_defensive_list.aip: 88 rows, no dependency-order failures.
- cardassian_endgame_list.aip: 87 rows, no dependency-order failures.
- cardassian_instant_action_build_list.aip: 87 rows, no dependency-order failures.
- cardassian_offensive_list.aip: 87 rows, no dependency-order failures.
- dominion_build_list.aip: 92 rows, no dependency-order failures.
- dominion_defensive_list.aip: 93 rows, no dependency-order failures.
- dominion_endgame_list.aip: 92 rows, no dependency-order failures.
- dominion_instant_action_build_list.aip: 92 rows, no dependency-order failures.
- dominion_offensive_list.aip: 92 rows, no dependency-order failures.
- federation_build_list.aip: 83 rows, no dependency-order failures.
- federation_defensive_list.aip: 84 rows, no dependency-order failures.
- federation_endgame_list.aip: 68 rows, no dependency-order failures.
- federation_instant_action_build_list.aip: 126 rows, no dependency-order failures.
- federation_offensive_list.aip: 83 rows, no dependency-order failures.
- klingon_build_list.aip: 99 rows, no dependency-order failures.
- klingon_defensive_list.aip: 100 rows, no dependency-order failures.
- klingon_endgame_list.aip: 99 rows, no dependency-order failures.
- klingon_instant_action_build_list.aip: 99 rows, no dependency-order failures.
- klingon_offensive_list.aip: 99 rows, no dependency-order failures.
- romulan_build_list.aip: 95 rows, no dependency-order failures.
- romulan_defensive_list.aip: 96 rows, no dependency-order failures.
- romulan_endgame_list.aip: 95 rows, no dependency-order failures.
- romulan_instant_action_build_list.aip: 95 rows, no dependency-order failures.
- romulan_offensive_list.aip: 95 rows, no dependency-order failures.
- species8472_build_list.aip: 67 rows, no dependency-order failures.
- species8472_defensive_list.aip: 67 rows, no dependency-order failures.
- species8472_endgame_list.aip: 67 rows, no dependency-order failures.
- species8472_instant_action_build_list.aip: 67 rows, no dependency-order failures.
- species8472_offensive_list.aip: 67 rows, no dependency-order failures.

Backup: D:\Xaramada-Modwork\backups\ai-start-recovery-20261024-041511
