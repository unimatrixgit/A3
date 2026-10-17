from pathlib import Path
import re,json,wave,collections
r=json.loads(Path('D:/aramada/reports/non-bajor-hero-yard-voice-audit.json').read_text());root=Path('D:/armadaIII');audio={p.name.lower():p for p in(root/'sounds').rglob('*')if p.is_file()};names=sorted({x for h in r['heroes']for cmd in h['commands']for x in cmd['clips']});rows=[];errors=[]
for n in names:
 p=audio.get(n.lower())
 try:
  with wave.open(str(p),'rb')as w:d={'file':n,'channels':w.getnchannels(),'sampleWidth':w.getsampwidth(),'sampleRate':w.getframerate(),'frames':w.getnframes(),'compression':w.getcomptype()}
  if d['frames']==0 or d['compression']!='NONE':errors.append(d)
  rows.append(d)
 except Exception as e:errors.append({'file':n,'error':str(e)})
out={'uniqueHeroClips':len(names),'waveFiles':rows,'errors':errors,'runtimePlaybackVerified':False};Path('D:/aramada/reports/hero-audio-format-audit.json').write_text(json.dumps(out,indent=2));print(json.dumps({'uniqueClips':len(names),'errors':errors[:10],'errorCount':len(errors),'formats':dict(collections.Counter(str((x['channels'],x['sampleWidth'],x['sampleRate']))for x in rows))}))
