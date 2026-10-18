# Separate game development checkpoint

All further game changes and tests target **D:/ArmadaLab**. The independent copy was moved there from the longer sandbox path. No hard links or junctions are used. D:/armadaIII was not modified during this continuation; D:/Xaramada remains excluded.

## Verified

- The loader reached a playable mission and displayed its Lua update message.
- 24 Lua 5.1 offline tests pass, including uncertain rollback, reentrant deployment and exclusion of research pods/terrain from structure counts.
- Static references: 2151 ODFs (including two MMM save helpers), 1410 includes, 1566 weapon links, no missing references detected.
- All 45 faction AI build plans pass the sequential producer/prerequisite audit. This is not runtime AI proof.

## Findings and current test

The legacy executable crashed at startup with the development process's inherited environment. A shortened process-local PATH allowed startup. `scripts/start-sandbox-game.ps1` repeats this without changing Windows/user settings.

The first loader probe retained a2_fed01R.drl. A later dump, Armada2.exe.31884.dmp, faults at 0x6df43fe inside that module (base 0x6df0000), with the original campaign DSL also loaded. Removing both rules links instead caused the earlier native menu fault at 0x547b1b before MMM loaded (Armada2.exe.9052.dmp).

The next probe therefore uses the stock **mp-regular** header rules in the existing first Federation campaign slot, with the original campaign DRL removed and MMM as script. It is local testing only. Its map and Lua file are applied in ArmadaLab, but runtime results are **unverified**. Desktop control reported `foreground window did not report a process id`; the last agent-launched test process was stopped after saving this state.

Launch with `scripts/start-sandbox-game.ps1`, select the first Federation campaign mission, then inspect the HUD for `LMS API PASS` or its exact failing stage. The API probe checks snapshots, one owned constructor creation/removal and a Save/Load stream round-trip. It does not test disk save/load or the full rescue mechanic.

## Safety and remaining work

`scripts/apply-sandbox-probe.py` refuses installation while any Armada2 process is running, backs up overwritten files, and only writes into ArmadaLab. Preserve its Development/backups directory.

Full Last Man Standing gameplay still needs a verified map, reviewed safe resource sites, AI rescue transition, once-only behavior and disk save/load. Its Scenario.lua remains disabled. Only after it works should the other six modes be completed together, as requested.

Release cleanup, redistributable installer, website and remaining texture/provenance work are unfinished. Do not distribute ArmadaLab: it contains the user's private commercial game runtime. Do not mark all tasks complete or deploy these tests to the live game.


## Superseding runtime results
The later Instant Action probe passed discovery, owned spawn/removal and save-state writing after correcting MMM stock detection. Native disk save, same-process reload and fresh-process reload succeeded. See `reports/lms-runtime-api-results.json` and `reports/mmm-stock-detection-fix.json`. Lua resume confirmation is still unresolved, so full rescue persistence is not verified. Current test copy remains D:/ArmadaLab.
