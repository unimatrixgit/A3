# Faction Universal constructors

Applied only to `D:/armadaIII`. There are eight faction versions; Species 8472 has none and is not present in their starbase lists. The legacy `uconst.odf` remains as a compatibility definition but no producer builds it.

The standard Borg Assembler and its faction Universal Assembler are the two Borg builder types. Recycler is in the standard menu. Technology Assimilator, Ship Upgrade Facility and Omega Lab are delegated to the Borg Universal Assembler. Other constructors' entries beyond the conservative 13-item limit are similarly delegated to their faction version.

Models preserve existing faction hulls, textures, damage nodes, lights and hardpoints, adding four fabrication-pod/strut meshes. Bajor uses the regenerated copper tender design as its prototype. Buttons and portraits are rendered from those exact model variants. These are gameplay adaptations, not screen-canon designs. In-game visibility, construction placement and AI behaviour require a fresh-match test.

Definitions, technology entries and 40 faction skirmish profiles are included in `bajor/overlay`. Asset files derived from installed models/textures are excluded from Git; the local game contains them. Generation requires a matching installation, NumPy/Pillow and the external stau SOD serializer. The scripts use absolute local paths and staging; review before reuse. The larger Bajoran rebuild is a separate staged release.

The Borg starbase button belongs only to the standard Assembler. Borg Universal has seven other faction starbases plus its three advanced Borg facilities, with no overlap between the two menus.
