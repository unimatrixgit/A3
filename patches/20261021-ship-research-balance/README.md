# Ship research and cost balance — 21 October 2026

Applied only to D:/armadaIII at the user’s request. ArmadaLab and Xaramada were not modified.

349 faction ships audited. All 601 non-utility special-weapon slots now have faction-owned research requirements in normal research modes. Existing valid research is retained; eight additional Special Systems Research items cover the remaining abilities. Forty local-game AI profiles schedule this research after the producing facility. These items are in each faction’s advanced research facility, except Breen’s regular research facility.

Mining, repair, tractor and colony equipment stays available, as requested. Full/free-tech presets stay unlocked; no-special presets disable special abilities. Campaign-specific technology trees are unchanged. Research gates for passive detection still need in-game verification.

347 ship prices reviewed; 303 ships changed in resources or crew. The Sovereign resource total550 and crew700, and the original basic Borg Cube550 dilithium/150 metal and crew800, are anchors. Combat prices reflect nominal durability, sustained weapon output, range and ability count; maxShots is treated as burst length rather than simultaneous barrels. Utility roles use shared price/complement tiers. CrewCost also controls starting crew. Explicit maximumCrew values, crewless Species8472 biology, ship officer costs, build times, combat statistics and visuals are retained. Scripted Q/flag helpers are excluded from fleet-price changes.

All seven heavy weapon platforms have crewCost0, maximumCrew0 and officerCost16 (previously8). Other platform stats/prices are unchanged.

See ship-prices.csv for the complete before/after list and manifest.json for file hashes, research paths and backups. The installed validator checks 391 files, all ability gates, faction pod producers, button aliases, native model attachments, prices, crew/officer values and AI list limits. It reports no file-level issues. Balance and actual research behavior are not yet gameplay verified.

Artwork and sounds are unchanged; new research and shared-ability buttons reuse existing installed sprite definitions and models. No new external assets were downloaded for this patch.
