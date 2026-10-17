# Current release — 17 October 2026

Only D:/armadaIII is modified. D:/Xaramada stays untouched. Heroes are buildable only; no faction-start heroes.

## Installed
- Bajoran full roster, custom artwork and icons, Federation-matched base/research properties, repair/decommission and AI fixes.
- Species 8472 and Dominion AI production recoveries; all nine factions have reachable research facilities.
- Borg Nexus six disruptor banks/two torpedo launchers. Two crewed assimilation stations with blue/green badges, automatic and manual beam controls, silent station audio workaround. Assimilation Station starts with 200 crew, maximum 1000, and produces the assimilated Federation repair ship.
- Sixteen cubes have passive cloak detection and technology-assimilation controls. Captured-special caps: normal1, tactical2, larger3–4, Omega5–6. Shield adaptation only on Scout/Locutus/Omega Locutus. Blue auto-assimilation remains removed from cubes.
- Special-energy budgets calculated by supported active/captured ability count; both new stations2500 capacity/25 regeneration. Omega Borg Cube costs1248 dilithium/1248 metal.
- Technology Assimilator and Transwarp Hub available on second Borg constructor; two Borg builder types retained.
- Riker Galaxy-X hero in Laforge's Shipyard: five offensive banks and cloak, existing installed model; original hero preserved.
- Locutus voice assets and Cooper bioship fallback installed. Exact STO Cooper recordings are not verified.
- Thirteen additional eight-player maps installed across the two batches, with zero map overwrites. Four latest maps use restored legacy aliases and current original environment art. Eight other catalogue candidates are finally excluded: four FleetOps requirements, four with fewer than eight verified starts.

## Current verification
- 2098 ODF definitions,1396 includes,1463 explicit weapon references: no missing references.
- 595 unique production targets across842 menu entries: required models/build icons resolve. Planetary shields use the native effect.
- 30 research/upgrade facilities across9 factions reachable; no menu overflow in checked paths.
- 40 non-Bajor AI profiles: reference checks pass. 34 non-Bajor heroes/8 yards: command/event links pass.206 checked audio files have native PCM formats.
- User reports all functions working and no other bugs found after testing. Exact per-feature test coverage was not specified. Static checks do not prove gameplay or every map's loading.

## Preserved limits
Stock automatic station recrewing is not implemented: no supported automatic-start setting was verified. Use Recrew command. Foreign captured-special HUD overlaps and full six-special Omega HUD remain unverified, despite the resolved built-in adaptation/technology button collision. Station beam audio is deliberately silent to prevent lingering toggle sounds.

A complete catalogue and implementation of every ship ever shown in every Trek film/episode is not finished. The installed roster CSV is the authoritative current inventory; do not label it exhaustive canon coverage.

Binary game assets and audio stay local; GitHub contains source, configuration and reports. No PC shutdown is scheduled.
