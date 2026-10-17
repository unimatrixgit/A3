import sys,struct,pathlib,json
sys.path.insert(0,'D:/Xaramada-Modwork/tools/crash-analysis')
from minidump.minidumpfile import MinidumpFile
out=[]
for p in pathlib.Path('D:/Xaramada-Modwork/diagnostics').rglob('*.dmp'):
 m=MinidumpFile.parse(str(p));r=m.get_reader();e=m.exception.exception_records[0];c=next(t.ContextObject for t in m.threads.threads if t.ThreadId==e.ThreadId)
 def read(a,n):
  try:return r.read(a,n)
  except:return b''
 cls=struct.unpack('<I',read(c.Esi+0x40,4))[0];labels={}
 for off in [0x74,0x7c,0x198,0x1b4]:
  ptr=struct.unpack('<I',read(cls+off,4))[0];labels[hex(off)]=read(ptr,140).split(b'\0')[0].decode('ascii',errors='replace')
 out.append({'dump':str(p),'labels':labels,'fault':hex(c.Eip)})
pathlib.Path('D:/aramada/reports/crash-object-identification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
