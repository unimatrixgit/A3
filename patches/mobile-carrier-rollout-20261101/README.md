# Mobile carrier and Atlantis beta rollout

Prepared and validated; NOT INSTALLED. Automatic approval review rejected the live deployment command with the generic reason "blocked by policy". The earlier Dominion carrier controller fix is installed separately.

- Voyager, Intrepid, X-refit and Mirror Voyager gain Delta Flyer production, retaining the Flyer's existing requirements.
- Negh'Var, Hutet, Diamond and Bajoran battleship gain scout/interceptor hangars. These are gameplay extrapolations, not TV carrier canon.
- Downloaded Romulan Kryonyx carrier is added to yard III and produces Talon scouts.
- Atlantis is built by Federation MK III at slot 12. Midas moves to MK II slot 12, keeping both builder menus within fourteen entries.
- Atlantis produces Puddle Jumpers and Aurora-class Alteran battleships. All three use Ancient drones with separate damage values.
- Atlantis abilities: Wormhole Drive, ZPM Improvement (Sovereign Corbomite Reflector), cloak, Naquadaq Overdrive. All four have zero research prerequisites and no resource unlock cost. Special energy remains required.
- Four abilities: 4,000 energy capacity and 40/second regeneration. Existing transwarp, Corbomite, cloak and Klingon Weapon Enhancer icons are reused.
- Naquadaq Overdrive uses the native DeathChant/TimedHyper effect: damage modifier 17.5 restores 40 base drone damage to the original 700 for 15 seconds. Cost 1,000 energy; 60-second firing cooldown. Runtime self-application, timing and damage still require verification.
- Breen and Ferengi excluded. Species 8472 retains its existing mobile mothership.

## Sources and credits

- [Atlantis 2.0](http://armadafiles.com/files/armada-2/stations/stargate/atlantis-20/details): ColdDarkParanoia.
- [Puddle Jumper 2.0](http://armadafiles.com/files/armada-2/ships/stargate/puddle-jumper-20/details): complete original readme retained under `docs/third-party/mobile-carriers-20261101/jumper`.
- [Aurora](http://armadafiles.com/files/armada-2/ships/stargate/aurora/details): Greathor; original credits retained.
- [Kryonyx](http://armadafiles.com/files/armada-2/ships/romulan/kryonyx-class-carrier/details): Bryan, textures by Cleeve; original readme retained.
- Existing Armada II assets supply the faction ships, voices, controller classes and special abilities.

## Validation and installation state

All 112 staged files passed the saved checks for references, models, native hardpoints, textures, sound decoding, technology paths, producer limits and source hashes. The GUI sprite file preserves the existing bytes and appends only new unit/ability entries. No runtime pass is claimed.

The rejected installation command made no live changes. Before any future installation, close the game, rerun validation against the current installation, back up every replaced live and repository-overlay file, and verify installed hashes against the manifest. Do not overwrite changed live files without rebasing the stage.

Test each carrier separately: match load, movement, stationary/moving production, launch position, combat and save/load. For Atlantis also test cloak/decloak, Wormhole Drive, ZPM Improvement and the Overdrive duration and self-only damage effect. One successful Atlantis test does not establish that every faction carrier works.
