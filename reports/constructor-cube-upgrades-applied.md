# Applied constructor upgrades and cube crew patch

Applied to D:/armadaIII only. Backup: D:/Xaramada-Modwork/backups/constructor-cube-upgrades-2026-10-24T02-57-26-423Z

- Basic Constructors can build their own faction starbase. Existing icons reused.
- Borg Temporal Specialist removed from all production, technology and AI lists. Transwarp Hub, Borg Ferengi Contract Yard and Central Unicomplex are on the Borg Advanced Constructor.
- All18 Borg cube definitions have35% more starting and maximum crew, rounded to whole crew. Weapons, hulls and energy unchanged.
-20 native NX-style single-ship upgrade buttons implement Basic to Advanced to Temporal for the main factions and compatibility variants. Each upgrade consumes its source constructor and converts to the next type. Free; no special-energy or research requirement. One fusion-type button per constructor; downgrade buttons were dropped at the user's selection.
- Breen and Ferengi remain single-constructor subraces.
- Restored starting fleets are byte-identical to the working baseline. No event loader or extra starting units added.

All20 buttons have sprite references, distinct slots/hotkeys and valid source-model hardpoints. All45 AI build lists pass sequential technology/producer checks after the Borg changes. Applied files match their staged and repository hashes. Actual in-game button visibility and conversion behavior remain untested.
