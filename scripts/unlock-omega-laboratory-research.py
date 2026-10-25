from pathlib import Path
import datetime, hashlib, json, re, shutil, subprocess

repo = Path('D:/aramada')
root = Path('D:/armadaIII')
running = subprocess.run(['powershell', '-NoProfile', '-Command', '@(Get-CimInstance Win32_Process -Filter "Name=\'Armada2.exe\' OR Name=\'Armada.exe\'").Count'], capture_output=True, text=True, check=True)
if int(running.stdout.strip() or '0'):
    raise SystemExit('Game running; patch not applied.')
backup = Path('D:/Xaramada-Modwork/backups') / ('omega-laboratory-research-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
changes = {}
for file in (root / 'techtree').glob('*.tt'):
    before = file.read_bytes()
    text = before.decode('latin1')
    for faction in ('f', 'b'):
        pod = 'x' + faction + 'omegapod.odf'
        lab = 'x' + faction + 'omegalab.odf'
        matches = re.findall(r'(?mi)^' + re.escape(pod) + r'[ \t]+[^\r\n]*', text)
        if not matches:
            continue
        assert len(matches) == 1, (file, pod, matches)
        replacement = pod + (' 0' if file.stem.lower() == 'fulltech' else ' 1 ' + lab)
        text = re.sub(r'(?mi)^' + re.escape(pod) + r'[ \t]+[^\r\n]*', replacement, text)
    after = text.encode('latin1')
    if before != after:
        changes[file.relative_to(root).as_posix()] = (before, after)
assert len(changes) == 5, len(changes)
for rel, (before, after) in changes.items():
    destination = root / rel
    assert destination.read_bytes() == before
    saved = backup / rel
    saved.parent.mkdir(parents=True, exist_ok=True)
    saved.write_bytes(before)
for rel, (before, after) in changes.items():
    destination = root / rel
    destination.chmod(0o666)
    destination.write_bytes(after)
    assert destination.read_bytes() == after
    mirror = repo / 'bajor/overlay' / rel
    mirror.parent.mkdir(parents=True, exist_ok=True)
    mirror.write_bytes(after)
    # Only the two research prerequisite lines may change.
    a = before.decode('latin1').splitlines()
    b = after.decode('latin1').splitlines()
    assert len(a) == len(b)
    delta = [(x, y) for x, y in zip(a, b) if x != y]
    assert len(delta) == 2
    assert all(y in ('xfomegapod.odf 1 xfomegalab.odf', 'xbomegapod.odf 1 xbomegalab.odf') for x, y in delta)
report = {'status': 'applied', 'backup': str(backup), 'runtimeVerified': False, 'files': list(changes), 'scope': 'Both existing Omega laboratories: laboratory-only research prerequisite. Laboratory construction and ship research gates unchanged.', 'nativeMinerResearch': 'Not applied: existing Ferengi pods unlock variants; stock global research has no cargo/mining-rate subsystem. Existing-unit automatic upgrades need a supported implementation before merging variants.'}
(repo / 'reports/omega-laboratory-research-applied.json').write_text(json.dumps(report, indent=2))
status = json.loads((repo / 'status.json').read_text(encoding='utf-8-sig'))
status['current'] = 'Omega research now requires only its own laboratory for Federation and Borg. Applied and file-checked; gameplay test pending. Automatic native/Ferengi miner and orbital research is under investigation; existing tiers preserved.'
(repo / 'status.json').write_text(json.dumps(status, indent=2), encoding='utf-8')
with (repo / 'build.log').open('a', encoding='utf-8') as log:
    log.write('\n[Omega laboratory research] Applied five technology trees; only Federation/Borg Omega pod prerequisites changed. Backup ' + str(backup) + '. No gameplay verification. Miner/orbital automatic research not implemented; tiered equipment retained.\n')
print(json.dumps(report, indent=2))
