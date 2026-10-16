# Armada II — Xaramada and Armada III

Personal Star Trek Armada II mod configuration and repair scripts.

- `overlay/`: configuration changes for `D:\Xaramada`.
- `bajor/overlay/`: configuration changes for `D:\armadaIII`, including the Bajoran prototype.
- `scripts/`: build, repair, audit and live-status tools. Many scripts use these local drive paths; review before running elsewhere.
- `reports/`: file-validation reports. `runtimeVerified: false` means gameplay has not been verified.

This is not a standalone game. Retail game binaries and third-party model, texture, map and audio assets are excluded. A matching licensed installation and the asset packs below are required. Do not apply every historical repair script in sequence: some intentionally supersede earlier changes.

Current Armada III files include faction heroes, Shipyard III, Borg abilities, faction Universal constructors and 25 local eight-player maps. The full Bajoran test package is installed: 19 ship roles, 14 buildings, 20 research pods, five skirmish AI profiles, all technology modes, model-rendered buttons and original synthetic Kira/Sela command lines. Picard's existing game recordings are used by Kira's Enterprise-E reinforcement. Deep Space 9 uses the installed DS9 model at a measured scale of 0.8858; Cardassian headquarters is named Terok Nor. Non-TV station names and Bajoran ship roles are explicitly game adaptations.

The faction hero reinforcement popup is a shared stock mobile producer with a wormhole arrival effect. It uses normal construction costs and 15-second production. It is not a QuantumEffect special weapon, whose summoned units are hardcoded to Team 0. The Bajoran Command Sanctuary uses the stock override weapon, restricted to enemy stations, with a 999999-second control duration and a 5000-energy cost. The hero yard follows it in the Bajoran Universal constructor menu and shares its prerequisites.

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
