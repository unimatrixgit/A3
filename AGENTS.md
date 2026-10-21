# Active mod target

Latest user instruction (2026-10-21): apply the ship research/cost and crewless heavy-platform update only to D:/armadaIII. Do not mirror this patch into ArmadaLab or Xaramada. Push approved source changes to the DuneGit origin. This explicit deployment request supersedes the older lab-only staging restriction below for this work.

Latest user instruction (2026-10-18): execute all further development and runtime testing in the independent game folder `D:/ArmadaLab`. Do not apply further experimental patches to the live `D:/armadaIII` installation. Save checkpoints for the user's return. This staging restriction supersedes the earlier live-target instruction below until the user requests deployment.

The user has explicitly restricted future game modifications to `D:/armadaIII`.
`D:/Xaramada` was restored to the supplied original installation on 2026-10-16 and must not be modified.
Historical scripts may contain loops targeting both folders. Do not execute them unchanged.
Back up current armadaIII files before replacing them. Preserve existing stats when changing artwork.
Keep `status.json` and `build.log` truthful; file validation is not in-game verification.

Hero ships are buildable only. Do not add heroes to standard, minimal, super, CTF or other starting fleets. This latest user instruction supersedes earlier one-starting-hero requirements and historical starter scripts. Keep hero production and voice events intact.

Borg cubes must not carry the blue Auto-Assimilator weapon (xacassim/gborgbor). Keep green holding/assimilation, transwarp and remaining weapons in their existing relative order with matching hardpoints; no empty weapon slots. Do not rerun historical beam-addition scripts unchanged.

Shield adaptation/remodulation is now restricted to Scout Cube (bscout) and Locutus variants (blocutus, xoblocutus). Do not restore it to other cubes. This supersedes historical all-cubes adaptation scripts.

## Repository destination
User instruction (2026-10-18): use https://www.dunerealms.com/git/unimatrix/A3/projects from now on. Git clone/push remote: https://www.dunerealms.com/git/unimatrix/A3.git . Do not push to previous GitHub destinations unless the user requests it.

