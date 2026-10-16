# Armada II — Xaramada and Armada III

Personal Star Trek Armada II mod configuration and repair scripts.

- `overlay/`: configuration changes for `D:\Xaramada`.
- `bajor/overlay/`: configuration changes for `D:\armadaIII`, including the Bajoran prototype.
- `scripts/`: build, repair, audit and live-status tools. Many scripts use these local drive paths; review before running elsewhere.
- `reports/`: file-validation reports. `runtimeVerified: false` means gameplay has not been verified.

This is not a standalone game. Retail game binaries and third-party model, texture, map and audio assets are excluded. A matching licensed installation and the asset packs below are required. Do not apply every historical repair script in sequence: some intentionally supersede earlier changes.

Current Armada III files include faction heroes, Shipyard III, Borg abilities, faction Universal constructors and 25 local eight-player maps. The full Bajoran test package is installed: 19 ship roles, 14 buildings, 20 research pods, five skirmish AI profiles, all technology modes, model-rendered buttons and original synthetic Kira/Sela command lines. Picard's existing game recordings are used by Kira's Enterprise-E reinforcement. Deep Space 9 uses the installed DS9 model at a measured scale of 0.8858; Cardassian headquarters is named Terok Nor. Non-TV station names and Bajoran ship roles are explicitly game adaptations.

Hero calling has been removed at the user's request, including all experimental unit definitions and technology/GUI references. The original Cardassian science ship and Quantum Singularity Effect were restored from the supplied original installation. The Bajoran Command Sanctuary remains a separate station-takeover ability.

This release passed file/reference, actual model geometry, texture, hardpoint, production reachability, sequential AI dependency, voice registration and deployment-copy checks. Runtime visibility, movement, reinforcement control, AI economy and station takeover still require fresh-match testing. Earlier invisible Bajoran models were replaced in this test package with regenerated geometry and explicit hierarchy; successful gameplay is not yet claimed. The full package backup is recorded in `reports/bajoran-rebuild-apply.json`.

Source assets and credits:
- Armada II Upgrade Project 2.0.0, Freyr and contributors: https://www.gamefront.com/games/armada-2/file/armada-ii-upgrade-project-vanilla-ultimate
- Borg Incursion 2, Major A Payne and credited artists: https://www.gamefront.com/games/armada-2/file/borg-incursion-2
- Ghost's Compilation Mod, Ghost and credited artists: https://www.gamefront.com/games/armada-2/file/ghost-s-compilation-mod

TV reference notes for Bajor are recorded in `bajor/manifest.json`. Gameplay additions beyond on-screen designs are adaptations, not claims of canon.


Active target: only D:\armadaIII. D:\Xaramada was restored to the supplied original installation. Historical reports refer to earlier states.
SOD serialization tooling: https://github.com/Elenterius/stau. Tool is kept outside this repository; install it before running the Python modeling/audit scripts.




Crash recovery: repeated match-load crashes followed the custom Bajoran model release. Active Bajoran definitions now use compatible installed models, with corrected attachments and missing Borg-texture fallbacks. Full gameplay roster, AI, costs and technology remain installed. The custom model staging release is quarantined; do not reapply it. All 53 active unit asset definitions pass structural checks; a repeated match test must confirm recovery. Cooper, new 8472 heroes and Locutus voice additions are paused while investigating this crash.

Additional stability recovery: all ten hero definitions again inherit the normal Craft runtime class. The experimental mobile-producer reinforcement interface is disabled and its installer quarantined. Existing combat weapons and abilities are retained. A fresh Bajoran match must verify loading.

Current loading hotfix: nine malformed ODF entries were repaired, including unmatched quotes in shared special-ship and Borg station definitions and malformed Bajoran attachment strings. Every installed ODF now passes quotation checks; no hero-call references remain. Windows swap settings and the executable were not changed. Runtime recovery requires a new-match test.
