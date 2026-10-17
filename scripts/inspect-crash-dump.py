import sys,json,pathlib
sys.path.insert(0,'D:/Xaramada-Modwork/tools/crash-analysis')
from minidump.minidumpfile import MinidumpFile
p=pathlib.Path('D:/Xaramada-Modwork/diagnostics/session-20261017-020009-20500/Armada2.exe_261017_020536.dmp')
m=MinidumpFile.parse(str(p));print(m.exception);print('THREADS',len(m.threads.threads));e=m.exception.exception_records[0];print(vars(e));print('MODULES',[(x.name,hex(x.baseaddress),hex(x.size))for x in m.modules.modules if 'armada' in x.name.lower()]);t=next(t for t in m.threads.threads if t.ThreadId==e.ThreadId);print(vars(t));print(vars(t.ContextObject))
