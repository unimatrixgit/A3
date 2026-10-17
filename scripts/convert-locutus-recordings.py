import sys,pathlib,subprocess,json,wave,hashlib,array,math
sys.path.insert(0,'D:/Xaramada-Modwork/tools/python-audio');import imageio_ffmpeg
exe=imageio_ffmpeg.get_ffmpeg_exe();src=pathlib.Path('D:/Xaramada-Modwork/downloads/locutus-audio');dest=pathlib.Path('D:/Xaramada-Modwork/locutus-voices/sounds/voiceover/ingame');dest.mkdir(parents=True,exist_ok=True);report=[]
for file in sorted(src.glob('gvoloc*.mp3')):
 out=dest/(file.stem+'.wav');subprocess.run([exe,'-nostdin','-v','error','-y','-i',str(file),'-ac','1','-ar','22050','-c:a','pcm_s16le',str(out)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 with wave.open(str(out),'rb')as w:
  assert w.getnchannels()==1 and w.getsampwidth()==2 and w.getframerate()==22050
  duration=w.getnframes()/w.getframerate();samples=array.array('h',w.readframes(w.getnframes()));rms=math.sqrt(sum(v*v for v in samples)/len(samples));assert duration>.2 and rms>20
 report.append({'file':out.name,'durationSeconds':round(duration,3),'sampleRate':22050,'channels':1,'bits':16,'rms':round(rms,2),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
pathlib.Path('D:/aramada/reports/locutus-voice-format-validation.json').write_text(json.dumps({'clips':report,'errors':[],'playbackVerified':False},indent=2));print(json.dumps({'converted':len(report),'format':'PCM16 mono 22050 Hz','errors':0}))
