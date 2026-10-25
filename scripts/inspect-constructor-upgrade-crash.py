import sys,io,pathlib,struct
sys.path.insert(0,'D:/Xaramada-Modwork/tools/crash-analysis')
from minidump.minidumpfile import MinidumpFile
from minidump.streams.ContextStream import WOW64_CONTEXT
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
p=pathlib.Path('C:/Users/thoma/AppData/Local/CrashDumps/Armada2.exe.8420.dmp');m=MinidumpFile.parse(str(p));e=m.exception.exception_records[0];c=WOW64_CONTEXT.parse(io.BytesIO(p.read_bytes()[e.ThreadContext.Rva:e.ThreadContext.Rva+e.ThreadContext.DataSize]));r=m.get_reader();print(m.exception);print({k:hex(getattr(c,k)) for k in ['Eip','Esp','Ebp','Eax','Ebx','Ecx','Edx','Esi','Edi']})
cs=Cs(CS_ARCH_X86,CS_MODE_32)
for x in cs.disasm(r.read(c.Eip-32,100),c.Eip-32):print(hex(x.address),x.mnemonic,x.op_str)
print('STACK', [hex(x) for x in struct.unpack('<80I',r.read(c.Esp,320))])
