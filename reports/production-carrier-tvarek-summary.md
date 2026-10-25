# Production, carrier and T'Varek patch

## Interior production and Spacedock

Audited 71 active conventional ship producers. The 29 redesigned yards now use
the actual bay centre as the production hardpoint. Existing internal points
were retained on other structures; missing or external points received an
internal hardpoint. Species 8472, maps, starting fleets and Recycler were not
modified. All four Federation Spacedock door pairs now have animation tracks;
the original SOD contained tracks for only Box01 and Box02. Meshes, materials,
station costs and combat values were preserved. Backups precede each deployment.

## Dominion carrier

The carrier has a Launch Jem'Hadar Fighter production button, using native
mobile-Starbase production context with ship movement/selection flags. Each
launch builds a player-owned carrier fighter in six seconds for 25 dilithium,
10 metal and five crew. The fighter retains the existing Jem'Hadar combat model
and weapons. No unverified neutral-owner summon weapon or executable change is
used. Ordinary production provides ownership; game control, carrier movement
and launch departure remain unverified in-game.

Mechanism reference: [Typhon and Valkyrie on ArmadaFiles](http://armadafiles.com/files/armada-2/ships/federation/tng-ds9-voy-and-future/typhon-and-valkyrie/details).
Only the native production approach was studied; no models, textures, sounds,
physics files or scripts were imported from that package.

## Federation hero

U.S.S. T'Varek is buildable at Archer Legacy Yard. Its custom low-poly SOD follows
the user's reference: pointed forward hull, central spine, twin heavy cannons,
annular aft warp frame and transverse stern structure. Uses existing Federation
material assets, build/queue/status art and a Federation hero badge. Archer
Legacy Yard was enlarged to fit the new model and retains internal production.

| Statistic | Value |
| --- | --- |
| Health/shield pool | 8,000 |
| Shield regeneration | 80 |
| Crew / maximum crew | 240 / 240 |
| Special energy / regeneration | 2,500 / 25 |
| Cost | 1,000 dilithium + 450 metal |
| Build time | 90 seconds |
| Weapon layout | 2 heavy particle cannons, 8 beam emitters, 4 torpedo tubes |
| Special abilities | Corbomite Reflector, Transphasic Torpedo, Self Destruct |

Emitter pairs share banks. Normal single-bank damage estimates total 188.3 DPS,
compared with 189.3 for the existing Enterprise-D hero; this is an estimate, not
an in-game damage measurement. Ability research follows existing Federation
weapon requirements; the existing hero transphasic ability retains its current
unlock. Unit availability follows its producing yard in restricted modes.

## Validation

All 40 AI profiles were dependency-ordered again, including carrier/fighter and
Federation hero targets. Production-point/door/hero inspection passed 197 checks;
the combined static validation passed 62,134 checks. Installed/source file
hashes are verified at publication. Results-screen portraits were added for
the new units. A fresh-match gameplay test remains necessary.
