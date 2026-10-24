# Starting-fleet rollback and AI adjustment

All9 faction starting definitions were restored from the backup preceding the extra-constructors patch, at the user's request after a match-load crash. This removes the extra starting Advanced/Breen/Ferengi constructors and restores the previous scouts/fleets.

The AI repairs are retained.45 faction plans were regenerated and passed producer/research-order validation against the restored starting fleets. Advanced constructors are now acquired through their yards rather than assumed to exist at match start. Dominion still develops Breen through normal production; Bajor acquires its Ferengi contractor through its contract yard.

The Windows report records an access violation at Armada2.exe offset0x00038038 at2026-10-24 04:16:35 Europe/Brussels. This confirms a crash but does not establish that starting units caused it. A new-match test after rollback is needed.
