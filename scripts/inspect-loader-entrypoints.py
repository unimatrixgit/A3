from pathlib import Path
import struct,sys,json
sys.path.insert(0,'D:/Xaramada-Modwork/tools/crash-analysis');from capstone import Cs,CS_ARCH_X86,CS_MODE_32
results=[]
for p in [Path('D:/armadaIII/missions/a2_fed01S.dsl'),Path('D:/Xaramada-Modwork/last-man-standing/research/mmm-extracted/mmm/missions/mmm_loader.dll')]:
 b=p.read_bytes();u16=lambda o:struct.unpack_from('<H',b,o)[0];u32=lambda o:struct.unpack_from('<I',b,o)[0];nt=u32(60);opt=nt+24;base=u32(opt+28);sec=opt+u16(nt+20);ss=[]
 for i in range(u16(nt+6)):
  o=sec+40*i;ss.append((u32(o+12),max(u32(o+8),u32(o+16)),u32(o+20)))
 def off(r):
  for va,size,raw in ss:
   if va<=r<va+size:return raw+r-va
  return r
 e=off(u32(opt+96));names=off(u32(e+32));ordinals=off(u32(e+36));functions=off(u32(e+28));rows=[]
 for i in range(u32(e+24)):
  a=off(u32(names+4*i));name=b[a:b.find(b'\0',a)].decode(errors='replace')
  if name not in ['ScriptInit','ScriptExtendInterface']:continue
  address=u32(functions+4*u16(ordinals+2*i));cs=Cs(CS_ARCH_X86,CS_MODE_32)
  entry=address
  jumps=[]
  for _ in range(4):
   first=next(cs.disasm(b[off(address):off(address)+16],base+address),None)
   if first is None or first.mnemonic!='jmp' or not first.op_str.startswith('0x'):break
   jumps.append(hex(base+address));address=int(first.op_str,16)-base
  instructions=[]
  for x in cs.disasm(b[off(address):off(address)+200],base+address):
   instructions.append(hex(x.address)+' '+x.mnemonic+' '+x.op_str)
   if x.mnemonic.startswith('ret'):break
  rows.append(dict(name=name,address=hex(base+entry),resolvedAddress=hex(base+address),jumpThunks=jumps,instructions=instructions))
 results.append(dict(file=p.name,entries=rows))
Path('D:/aramada/reports/mission-loader-entrypoints.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
