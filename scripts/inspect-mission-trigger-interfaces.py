from pathlib import Path
import struct,json,re

def pe(p):
 b=p.read_bytes();u16=lambda o:struct.unpack_from('<H',b,o)[0];u32=lambda o:struct.unpack_from('<I',b,o)[0];nt=u32(60);assert b[nt:nt+4]==b'PE\0\0';opt=nt+24;dirs=opt+(96 if u16(opt)==267 else 112);sec=opt+u16(nt+20);sections=[]
 for i in range(u16(nt+6)):
  o=sec+i*40;sections.append((u32(o+12),max(u32(o+8),u32(o+16)),u32(o+20)))
 def off(r):
  for va,size,raw in sections:
   if va<=r<va+size:return raw+r-va
  return r
 def string(r):
  o=off(r);return b[o:b.find(b'\0',o)].decode('ascii',errors='replace')
 exports=[];imports=[];erv=u32(dirs)
 if erv:
  e=off(erv);names=off(u32(e+32))
  for i in range(u32(e+24)):exports.append(string(u32(names+i*4)))
 irv=u32(dirs+8)
 if irv:
  o=off(irv)
  while any(b[o:o+20]):
   lookup,_,_,name,iat=struct.unpack_from('<IIIII',b,o);symbols=[];t=off(lookup or iat)
   while u32(t):
    v=u32(t);symbols.append('#'+str(v&65535)if v&0x80000000 else string(v+2));t+=4
   imports.append(dict(library=string(name),symbols=symbols));o+=20
 return dict(file=p.name,exports=exports,imports=imports)
r=Path('D:/armadaIII/missions');out=[pe(r/n)for n in ['a2_fed01R.drl','a2_fed01S.dsl','a2_kling02R.drl','a2_kling02S.dsl']];Path('D:/aramada/reports/mission-trigger-module-interfaces.json').write_text(json.dumps(out,indent=2));print(json.dumps([dict(file=x['file'],exports=[s for s in x['exports']if not s.startswith('?')][:80],libraries=[i['library']for i in x['imports']],engineImports=[i for i in x['imports']if i['library'].lower()not in ['kernel32.dll','msvcrt.dll','user32.dll']])for x in out],indent=2))

