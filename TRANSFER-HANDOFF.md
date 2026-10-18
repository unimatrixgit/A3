# Armada III checkpoint — 18 October 2026

## Update at current checkpoint
User confirmed Cardassian home-base mining WORKS. Resumed Last Man Standing. Implemented RescueCore.lua, NativeAdapter.lua, nine-faction rescue config/definitions and entry point under modes/last-man-standing. Twenty offline Lua 5.1 tests pass (13 rules +7 mocked-engine adapter); Lupa installed only in D:/Xaramada-Modwork/tools/lua-tests. Safe-site Scenario.lua is deliberately disabled/unassigned; full rescue mode is NOT installed or gameplay-verified.

User then closed game. Installed all25 staged AI economy profiles AND six files for a separate native mission loader smoke test. Backup D:/Xaramada-Modwork/backups/ai-final-loader-test-20261018-085031,31-file manifest. All45AI profiles pass sequential checks. The previous sections calling25profiles uninstalled are now superseded.

Loader test is in the Single Player tutorial/miscellaneous mission list, labelled Last Man Standing - Loader Test. Map LastManStandingTest.bzn is a COPY of native a2_fed01.bzn; original map untouched. Verified typed-string records adjust both serialized lengths; EmptyMission fixed64 script/rule/title fields replaced with mmm_loader.dll/empty/title; old native campaign DSL/DRL links removed in copied map. Existing campaign menu entries preserved. Mission source modes/last-man-standing/Last Man Standing Loader Test.lua; stage D:/Xaramada-Modwork/last-man-standing/loader-test; report reports/last-man-standing-loader-test.json. Script logs setup/update/entity finder/player race/map bounds/constructor and starbase anchors to LastManStanding-LoaderTest.log in game working directory. It does NOT grant resources or spawn rescues. Next step: load this diagnostic mission and inspect log/crash dump. Exact native MMM compatibility remains untested.

Potential follow-up checks: MMM include returns are not assumed; modules set LMS globals then return for unit tests. Adapter only queries configured player slots to avoid null race pointers. Deployment rollback failures return indeterminate and consume rescue to prevent duplication. Core needs an additional test for indeterminate/re-entrant cases; native map placement/victory lifecycle still unimplemented. stage-last-man-standing-prototype.py currently regenerates config as plain return tables, so update generator to retain LMSRescueConfig/LMSNativeDefinitions globals before rerunning. Keep live game unchanged while user plays.

Live game: D:/armadaIII only. Never modify D:/Xaramada. Repository: D:/aramada; GitHub unimatrixgit/armada2, main. Last published commit 55dbfb8; subsequent installed work is not all published. Read AGENTS.md. Keep sources/ in the ChatGPT project read-only.

## Latest installed patch
Cardassian AI constructors were travelling across the map to place mining stations. User confirmed constructors, not freighters. Five Cardassian build profiles had twenty cmining/corbital directives using expansion bases 1/2. Changed only those resource-building directives to home base 0. Report reports/cardassian-local-mining.json; stage D:/Xaramada-Modwork/cardassian-local-mining; backup D:/Xaramada-Modwork/backups/cardassian-local-mining-20261018-084014. Source hashes checked before installation. All 45 faction build profiles pass sequential producer/prerequisite audit. Await gameplay report: native resource placement can still select distant sites when local resources are unavailable.

Earlier Cardassian economy patch is installed: metal/dilithium, two freighters and basic destroyers before advanced research. Its later expansion assignments caused the latest issue and are now corrected.

## Recent installed content
- All 40 Borg ship costs use ORIGINAL basic Cube anchor 550 dilithium / 150 metal / 2 officers. reports/borg-uniform-costs.json; scripts/apply-borg-original-cube-costs.py. Not the superseded 350/350 baseline.
- Transwarp Prototype brenborg: four beam banks, two normal torpedoes plus large-sphere bm4phot launcher (.375-second refire), green and blue beams, sphere regeneration, transwarp F5, native tech capture, two captured slots, self-destruct; 3000 energy /30 regen. No structure changed for that request.
- All 29 unique ships in byard/byard2/byard3 have transwarp, correct beam (green cubes, blue others) and another special. Missing distinct abilities received regeneration. Existing green on non-cubes retained. Reports/borg-yard-abilities.json. GUI aliases added for 33 new abilities plus four prototype aliases.
- Shield adaptation remains restricted to Scout Cube and Locutus variants. No blue assimilation added to cubes.
- 22 starbase variants maximumCrew 2000; starting crew/costs preserved. Borg Scout crew150. Orbital mining station has two extra weapon banks.
- User confirmed tooltip crash fix works: bdestroy2 had verboseTooltip without tooltip. Added short title. Latest dump Armada2.exe.30252.dmp has null lookup at0x481cc0 via tooltip caller0x4e7325. Report borg-interceptor-tooltip-crash-hotfix.json. Decode EXCEPTION ThreadContext, not the post-crash thread context. inspect-latest-crash-callers.py shows correct parsing.

## Staged, NOT installed
D:/Xaramada-Modwork/all-ai-economy-final contains 25 profiles for Federation/Klingon/Romulan/Breen/Bajoran: economy-first openings and replaceable universal builders. reports/all-ai-economy-final.json; scripts/stage-all-ai-economy-final.py. No errors in staged dependency checks. Federation fyard0 must precede fyard. Keep Borg/Cardassian/Dominion/8472 unchanged. Ask for game closure when ready, back up, then install. Do not overwrite current Cardassian fix with an older stage.

## Active development: seven LOCAL game modes
First prove Last Man Standing coded and working, then deliver remaining six modes in one combined patch. modes/game-modes.json is design-only, not playable modes.
1. Last Man Standing: once per AI per match, losing last constructor while structures remain triggers one faction hero, nine escorts, one constructor and rebuilding resources at another safe valid location. Must detect actual transition, exclude humans, persist used flag through save/load.
2. Stronghold: completed standard base and basic fleet.
3. Siege: defend escalating waves.
4. Border War: outpost/light fleet expansion.
5. Hero Command: protect faction hero.
6. King of the Wormhole: central control scoring.
7. Kobayashi Maru: deliberate no-win civilian rescue, evaluation instead of conventional victory.
Add lore briefings and sources. No new loader or mode is installed. No playable Lua mode has been written yet.

Mission scan:72 compiled PE files disguised .dsl/.drl. Found resource-injection and reinforcement functions. Native DSL exports ScriptInit and ScriptExtendInterface. Reports/mission-trigger*.json. events.dat only provides notifications, not spawning logic.

Real scripting route found: Megadroid Mission Mod1.0.1 downloaded/extracted to D:/Xaramada-Modwork/last-man-standing/research/mmm-extracted/mmm, NOT installed. Official legacy HTTP download works; HTTPS hostname certificate is wrong (do not disable TLS validation). Cached documentation research/structure.html and api/index.json (169+ reference pages plus descriptive pages). Author states stock A2 support and Instant Action scripting support; exact executable compatibility still needs testing.

MMM map requirements: script file mmm_loader.dll, title matching Lua/pack, mission map type. Entity.add(odf,player,Vector); EntityFinder(...):find(); GameObject.odf/player/aiControlled; Player(number).isAI/resources; Map.min/max. Entity.valid must be checked before dereference. Save/Load APIs store persistent state on map and require mmm_holder/mapper ODFs. Example scripts bundled. mshell.set uses dash-separated campaigns; do not assume fifth menu slot is supported. Lua test runtime Lupa not installed. Fetch exact API lifecycle and resource setters before coding adapter.

Stronghold scan currently only text editor handle declarations; not a complete binary BZN/ownership audit. Race does not prove team ownership. Need inspect binary mission map ownership and positions.

## Release tasks after feature completion
- Dependency-aware cleanup: archive recoverably, never delete solely because absent from build menus. Check missions/maps/SOD textures/sprites/weapons/ordnance/sounds/events and dynamic aliases. Preserve credits. No cleanup performed yet.
- Mod installer EXE requiring existing Armada II; no commercial game executable redistribution. Inno/NSIS compiler not located yet. No installer built.
- Website with GitHub, wiki, downloads, news, changelog and easy admin. Per-change source URL/author/reused items/our modifications required. Readmes must accompany installer. No website created yet.
- Sites skill already read at C:/Users/thoma/.codex/plugins/cache/openai-curated-remote/sites/1.0.1/skills/sites/SKILL.md and presentation-led design reference. Read local preview reference before preview. Native tool complete schemas are in ALL_TOOLS entry descriptions. No Site ID exists. New sites private by default; persist ID immediately and keep repository credential only in memory/stdin.
- Luna readme explicitly requires k_merse permission to modify/re-release/include. Honor asset distribution terms; no contacting authors is authorized. Other source readmes are under D:/Xaramada-Modwork/content-expansion.
- Bajoran archive matching remains TEXTURES-ONLY, no model/stats/scale changes; pending.

User plays while we stage/test separately; ask when concrete update is ready. Do not overwrite running game files. No PC shutdown. Save checkpoints if credits run out; do not promise automatic session transfer. Progress page http://127.0.0.1:8766/ reads D:/aramada/status.json and build.log.

Python: C:/Users/thoma/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe
Node: C:/Users/thoma/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe
Crash libraries: D:/Xaramada-Modwork/tools/crash-analysis. SOD utilities: D:/Xaramada-Modwork/tools/stau/src/sod_utils.
