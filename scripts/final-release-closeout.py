from pathlib import Path
import json,csv,urllib.request,datetime
exec(Path('D:/aramada/scripts/audit-faction-starts-and-maps.py').read_text().split('results=[]')[0])
rows=[];production={x['target']for x in json.loads((repo/'reports/final-production-assets.json').read_text())['rows']}
for n,p in idx.items():
 if p.parent.name.lower()!='ships':continue
 d=props(n);rows.append({'file':n,'name':d.get('unitname',''),'race':d.get('race',''),'hero':d.get('ishero','0'),'buildable':n.removesuffix('.odf')in production,'model':d.get('basename',n.removesuffix('.odf'))})
with(repo/'reports/installed-ship-roster.csv').open('w',newline='',encoding='utf-8')as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(repo/'reports/installed-ship-roster-summary.json').write_text(json.dumps({'shipsInventoried':len(rows),'buildableShipDefinitions':sum(x['buildable']for x in rows),'scope':'Installed inventory only; does not establish coverage of every ship appearing in every film/episode.','runtimeVerified':False},indent=2))
summary='''# Current release — 17 October 2026

Only D:/armadaIII is modified. D:/Xaramada stays untouched. Heroes are buildable only; no faction-start heroes.

## Installed
- Bajoran full roster, custom artwork and icons, Federation-matched base/research properties, repair/decommission and AI fixes.
- Species 8472 and Dominion AI production recoveries; all nine factions have reachable research facilities.
- Borg Nexus six disruptor banks/two torpedo launchers. Two crewed assimilation stations with blue/green badges, automatic and manual beam controls, silent station audio workaround. Assimilation Station starts with 200 crew, maximum 1000, and produces the assimilated Federation repair ship.
- Sixteen cubes have passive cloak detection and technology-assimilation controls. Captured-special caps: normal1, tactical2, larger3–4, Omega5–6. Shield adaptation only on Scout/Locutus/Omega Locutus. Blue auto-assimilation remains removed from cubes.
- Special-energy budgets calculated by supported active/captured ability count; both new stations2500 capacity/25 regeneration. Omega Borg Cube costs1248 dilithium/1248 metal.
- Technology Assimilator and Transwarp Hub available on second Borg constructor; two Borg builder types retained.
- Riker Galaxy-X hero in Laforge's Shipyard: five offensive banks and cloak, existing installed model; original hero preserved.
- Locutus voice assets and Cooper bioship fallback installed. Exact STO Cooper recordings are not verified.
- Thirteen additional eight-player maps installed across the two batches, with zero map overwrites. Four latest maps use restored legacy aliases and current original environment art. Eight other catalogue candidates are finally excluded: four FleetOps requirements, four with fewer than eight verified starts.

## Current verification
- 2098 ODF definitions,1396 includes,1463 explicit weapon references: no missing references.
- 595 unique production targets across842 menu entries: required models/build icons resolve. Planetary shields use the native effect.
- 30 research/upgrade facilities across9 factions reachable; no menu overflow in checked paths.
- 40 non-Bajor AI profiles: reference checks pass. 34 non-Bajor heroes/8 yards: command/event links pass.206 checked audio files have native PCM formats.
- User reports all functions working and no other bugs found after testing. Exact per-feature test coverage was not specified. Static checks do not prove gameplay or every map's loading.

## Preserved limits
Stock automatic station recrewing is not implemented: no supported automatic-start setting was verified. Use Recrew command. Foreign captured-special HUD overlaps and full six-special Omega HUD remain unverified, despite the resolved built-in adaptation/technology button collision. Station beam audio is deliberately silent to prevent lingering toggle sounds.

A complete catalogue and implementation of every ship ever shown in every Trek film/episode is not finished. The installed roster CSV is the authoritative current inventory; do not label it exhaustive canon coverage.

Binary game assets and audio stay local; GitHub contains source, configuration and reports. No PC shutdown is scheduled.
'''
(repo/'CURRENT-RELEASE.md').write_text(summary,encoding='utf-8')
remaining='''# Remaining work — reconciled 17 October 2026

## Implemented work
All concrete configuration/artwork fixes in CURRENT-RELEASE.md are installed in D:/armadaIII. No validated patch is waiting for application. User reports all functions working. Four further maps and compatibility aliases installed during final cleanup. Historical crashes, provisional graphics batches and starting-hero tasks are superseded; do not rerun their installers.

## Verification still pending
- Load/play each of the13 added maps; no runtime loading claim is made.
- Measure full Omega captured-special HUD behavior; file capacity alone cannot guarantee every button displays.
- Explicit before/after research-effect measurements and exact voice playback coverage were not supplied. Preserve the user's general success report without inventing detailed results.

## Unsupported or broader unfinished scope
- Automatic station recrew: no verified stock auto-start mechanism. Manual recrew remains available.
- Exhaustive every-film/episode ship catalogue/models: current installed inventory exists, but exhaustive coverage is not established. This is a separate large content expansion, not a completed item.
- Exact STO Cooper voice: conditional request unresolved; existing fallback remains. No actor imitation generated.

## Closed/superseded
- Hero reinforcement calls: removed at user's request; do not restore.
- Starting heroes: removed at user's request; keep heroes buildable only.
- Unstable old Bajor art batches: superseded by installed working roster/art.
- Eight excluded map candidates are not pending stock installation: four require FleetOps, four lack eight verified starts. Do not relabel them eight-player compatible.
- Do not shut down the PC. Current target D:/armadaIII only; D:/Xaramada untouched.
'''
(repo/'REMAINING-WORK.md').write_text(remaining,encoding='utf-8');(repo/'MORNING-HANDOFF.md').write_text('# Handoff\n\nRead CURRENT-RELEASE.md and REMAINING-WORK.md for current state. Historical handoff content was replaced because it described superseded heroes, cube abilities, and incomplete patches now installed.\n\nLatest user confirmation: all functions working/no other bugs found; exact feature coverage unspecified. Latest cleanup adds four maps and legacy aliases. All current static checks passed. No PC shutdown.\n',encoding='utf-8')
sfile=repo/'status.json';s=json.loads(sfile.read_text(encoding='utf-8-sig'));s['historicalFeatures']=s.get('historicalFeatures',[])+s.get('features',[]);s['features']=[{'id':'current-installation','title':'Current configuration and artwork','steps':[{'label':'Apply approved fixes','done':True},{'label':'Backups and installation checks','done':True},{'label':'User reports working functions','done':True}]},{'id':'final-diagnostics','title':'Final diagnostics','steps':[{'label':'ODF references','done':True},{'label':'Production icons and models','done':True},{'label':'Research reachability and AI','done':True},{'label':'Hero command audio references','done':True}]},{'id':'map-catalogue-closeout','title':'Eight-player map catalogue','steps':[{'label':'Check72 source archives','done':True},{'label':'Install13 additional maps','done':True},{'label':'Classify8 incompatible/non-eight maps','done':True},{'label':'Gameplay test every added map','done':False}]},{'id':'broader-canon-expansion','title':'Broader ship catalogue','steps':[{'label':'Refresh installed inventory','done':True},{'label':'Verify exhaustive TV/film ship coverage','done':False}]}];s['current']='Final cleanup installed four additional maps and3 compatibility aliases, no overwrites/environment replacements. Current diagnostics pass:2098 ODFs,595 production targets,30 tech facilities,40 AI profiles,34 hero command sets. User reports functions working. Release notes reconciled; broader catalogue, exact Cooper voice and runtime-specific limits remain documented.';s['steps']=[{'label':a['title']+': '+v['label'],'done':v['done']}for a in s['features']for v in a['steps']];sfile.write_text(json.dumps(s,indent=2),encoding='utf-8')
with(repo/'build.log').open('a')as log:log.write('\nCloseout: four maps/three aliases installed,14 new files and no overwrite. Full static diagnostics pass; current release docs/tasks reconciled. Runtime and broader content limits explicitly retained.\n')
try:
 with urllib.request.urlopen('http://127.0.0.1:8766/',timeout=5)as response:print('Live dashboard HTTP',response.status)
except Exception as e:print('Dashboard check failed:',str(e))
print('Refreshed roster',len(rows),'ships; release/handoff/remaining work reconciled.')
