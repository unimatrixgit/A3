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


## 2026-10-18 save lifecycle investigation (latest)
All tests were in D:/ArmadaLab. Fresh-process native reload reproduced missing Lua startup. Read-only process inspection: profile guard 0, interface pointer present, MMM ScriptInit flag 0. Native AiMission::PostLoad skips Init_Action_Scripts on saved loads.
A guarded, backed-up private DLL experiment called ScriptInit on interface binding: flag became 1, but native LoadScriptUtils cleared the input callback to zero. A second private experiment suppressed that reset: the callback remained and the HUD printed the API PASS fresh-start result, NOT LOAD PASS. Therefore callback recovery and lifecycle classification both need work. Both temporary binary experiments have been reverted to prior exact hashes.
Added setup helper detection to Last Man Standing.lua so an unexpected fresh-start dispatch cannot reset spent rescue flags. Seven new entry lifecycle tests pass; 31 total Lua 5.1 regression tests pass. This source guard is not yet in-game verified. Scenario remains disabled.
Reports: lms-save-lifecycle-findings.json, native-save-lifecycle.json, mmm-resume-registration-experiment.json, native-callback-reset-experiment.json. The read-only state reader is scripts/read-sandbox-loader-state.py. A GUI exit of the first loader experiment generated Armada2.exe.31884.dmp (12:08); investigate unload stability too. No live-game changes. Game closed at checkpoint.
Next: implement a narrowly scoped callback restoration path (do NOT ship globally skipping the engine reset), verify actual saved values, then review rescue sites and test real rescue transitions. Remaining six modes, installer, cleanup, website and provenance remain unfinished.


### Scoped follow-up (supersedes provisional callback conclusion)
A new guarded .lms section retained only an exact active MMM callback (GetModuleHandleA base + 0x20a0), leaving stock resets for other callbacks. Read-only process inspection confirmed the nonzero callback after saved-game load. However, neither LOAD PASS nor FAIL appeared with the staged helper-detection probe, including after ship selection. All complete staged scripts parse under Lua 5.1. This experiment also was reverted to the original sandbox executable hash; loader interface-binding experiment reverted too. Do not claim callback preservation alone restores Lua execution. Trace MMM callback/mission bootstrap next. All 31 offline tests remain passing.
