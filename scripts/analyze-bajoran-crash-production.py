import sys,struct,json,pathlib,re
sys.path.insert(0,'D:/Xaramada-Modwork/tools/crash-analysis')
from minidump.minidumpfile import MinidumpFile
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
p=pathlib.Path('D:/Xaramada-Modwork/diagnostics/session-20261017-022014-19964/Armada2.exe_261017_022925.dmp');m=MinidumpFile.parse(str(p));r=m.get_reader();e=m.exception.exception_records[0];c=next(t.ContextObject for t in m.threads.threads if t.ThreadId==e.ThreadId);cs=Cs(CS_ARCH_X86,CS_MODE_32)
def read(a,n):
 try:return r.read(a,n)
 except:return b''
def asm(a,n):return [hex(i.address)+' '+i.mnemonic+' '+i.op_str for i in cs.disasm(read(a,n),a)]
print('\n'.join(asm(c.Eip-28,96)))
stack=read(c.Esp,384);calls=[]
for off in range(0,len(stack),4):
 v=struct.unpack_from('<I',stack,off)[0]
 if 0x400000<=v<0x7fa000:calls.append({'stackOffset':off,'address':hex(v),'nearby':asm(v-12,24)})
print(json.dumps(calls,indent=2))
for reg in ['Esi','Ebx','Eax','Edx']:
 a=getattr(c,reg);b=read(a,1024);print(reg,hex(a),'strings',re.findall(rb'[ -~]{5,}',b)[:20]);print('head',b[:96].hex())
out={'exception':'access violation reading null pointer','address':hex(c.Eip),'registers':{k:hex(getattr(c,k))for k in ['Eax','Ebx','Ecx','Edx','Esi','Edi','Esp','Ebp','Eip']},'instructions':asm(c.Eip-28,96),'stackCandidates':calls,'causeConfirmed':False}
pathlib.Path('D:/aramada/reports/bajoran-crash-dump-production.json').write_text(json.dumps(out,indent=2))

