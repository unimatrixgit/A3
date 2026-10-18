import sys,struct,pathlib,io,re,json
sys.path.insert(0,'D:/Xaramada-Modwork/tools/crash-analysis')
from minidump.minidumpfile import MinidumpFile
from minidump.streams.ContextStream import WOW64_CONTEXT
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
p=pathlib.Path('C:/Users/thoma/AppData/Local/CrashDumps/Armada2.exe.30252.dmp');m=MinidumpFile.parse(str(p));r=m.get_reader();e=m.exception.exception_records[0];c=WOW64_CONTEXT.parse(io.BytesIO(p.read_bytes()[e.ThreadContext.Rva:e.ThreadContext.Rva+e.ThreadContext.DataSize]));b=pathlib.Path('D:/armadaIII/Armada2.exe').read_bytes();nt=struct.unpack_from('<I',b,60)[0];sec=nt+24+struct.unpack_from('<H',b,nt+20)[0];sections=[]
for i in range(struct.unpack_from('<H',b,nt+6)[0]):
 o=sec+i*40;size,va,rawsize,raw=struct.unpack_from('<IIII',b,o+8);sections.append((0x400000+va,max(size,rawsize),raw))
def read(a,n):
 try:return r.read(a,n)
 except:
  for va,size,raw in sections:
   if va<=a<va+size:return b[raw+a-va:raw+a-va+n]
  return b''
cs=Cs(CS_ARCH_X86,CS_MODE_32)
for a in [0x4e7300,0x4e6a80,0x505ca0,0x50bec0,0x51a100]:
 print(hex(a),'\n'+'\n'.join(hex(x.address)+' '+x.mnemonic+' '+x.op_str for x in cs.disasm(read(a,100),a)))
stack=read(c.Esp,1400);found=[]
for i in range(0,len(stack)-3,4):
 a=struct.unpack_from('<I',stack,i)[0]
 if a<0x1000000:continue
 data=read(a,1024);strings=[s.decode(errors='replace')for s in re.findall(rb'[ -~]{5,}',data)if re.search(rb'odf|borg|bren|cube|xy_|xbtp|assim|regen|phot',s,re.I)]
 if strings:found.append(dict(offset=i,pointer=hex(a),strings=strings[:8]))
print(json.dumps(found,indent=2));print('Ebp',hex(c.Ebp),'frame',read(c.Ebp,60).hex())
