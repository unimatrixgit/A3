# Drozana commerce package — 28 October 2026

Installed only in D:/armadaIII; original Xaramada and ArmadaLab untouched.

- Drozana Commerce Exchange: original K7-family-inspired station model, Ferengi-operated trading facility. Built by xfgconst after xfgmerc.
- Assimilated Drozana Foundry: Borg-only xbgconst construction option, requires xbgmerc and byard2. Nine combat conversions: Federation, Klingon, Romulan, Cardassian, Dominion, Borg, Bajoran, Breen and Ferengi. No Species 8472. These are craft/CraftProcess attack vessels, never cargo ships.
- Each conversion retains its source faction freighter hull with added Borg machinery, two beams, one torpedo, blue Auto-Assimilator, Transwarp and sphere Regeneration. Existing borpod1/3/4 research still governs those abilities.
- 3,000 special energy, 85/s regeneration: three-ability capacity baseline and sustain budget with 20% headroom. Sustained-use assumptions: blue beam50/s, regeneration80/30s, transwarp1000/60s.
- Standard trade cargo values doubled at their original definitions. No ship-specific 3x bonus, per the user's uniform2x choice. Station commission unchanged.
- Player-buildable Ferengi trade ship xfgtrade capacity1000, twice native500. This replaces its previous modded1500 setting.
- Native per-ship handling patch doubles only xfgtrade LoadCargo/UnloadCargo transfer amounts. ODF name matching is case-insensitive with optional directory and .odf extension; other ships and station-wide handling rates unchanged. 64 x86-emulated selector, transfer, register, flags and stack tests passed; real game testing pending.
- Engine patch detours: LoadCargo0x4ae1c0, UnloadCargo0x4ae440; name lookup via existing GameObjectClass::GetOdfName0x4ce370. New .fgdock code section; original routine addresses preserved. The installed original executable is backed up. Full executable is not committed: the generator recreates it from the verified local base binary.

Design references: [Drozana Station, STO Wiki](https://sto.fandom.com/wiki/Drozana_Station), [official STO Drozana lore reference](https://www.playstartrekonline.com/en/news/article/11084713). New station geometry and Borg fittings were authored locally; no STO model was extracted. Hulls/textures use the installation's existing faction assets; source freighter ODFs are recorded in manifest.json.

Visual/model/reference/technology checks and native hook emulation passed. Installation hashes verified. No gameplay success is claimed until tested.
