"""Private stock-load experiment: retain ONLY the active MMM input callback.

Adds a private code section; never redistributes the executable. All other
callbacks retain stock clearing behavior. Pair with interface-binding experiment.
"""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import struct
import subprocess
import sys

target=Path('D:/ArmadaLab/Armada2.exe')
report_path=Path('D:/aramada/reports/scoped-mmm-callback-experiment.json')
shell='C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe'
running=subprocess.check_output([shell,'-NoProfile','-Command','@(Get-Process Armada2 -ErrorAction SilentlyContinue).Count'],text=True)
assert int(running.strip())==0,'Close the test game first'
expected='f9e283deb68506a779feceecac144d1c035f6e4fe79c636e5207437780fecb28'
if '--undo' in sys.argv:
    report=json.loads(report_path.read_text());backup=Path(report['backup'])
    assert hashlib.sha256(backup.read_bytes()).hexdigest()==expected
    assert hashlib.sha256(target.read_bytes()).hexdigest()==report['afterSha256']
    shutil.copy2(backup,target);report['reverted']=True
else:
    b=bytearray(target.read_bytes());assert hashlib.sha256(b).hexdigest()==expected
    u16=lambda o:struct.unpack_from('<H',b,o)[0]
    u32=lambda o:struct.unpack_from('<I',b,o)[0]
    nt=u32(60);opt=nt+24;base=u32(opt+28);table=opt+u16(nt+20);count=u16(nt+6)
    assert base==0x400000 and not u16(opt+70)&0x40
    sections=[(u32(table+i*40+12),max(u32(table+i*40+8),u32(table+i*40+16)),u32(table+i*40+20))for i in range(count)]
    def offset(address):
        for va,size,raw in sections:
            if va<=address-base<va+size:return raw+address-base-va
        raise ValueError(hex(address))
    def align(n,a):return (n+a-1)//a*a
    header=table+count*40
    assert header+40<=u32(opt+60) and b[header:header+40]==bytes(40)
    hook=0x45844e;at=offset(hook)
    assert b[at:at+10]==bytes.fromhex('6a 00 8b 01 ff 90 28 04 00 00')
    rva=align(max(v+s for v,s,_ in sections),u32(opt+32))
    raw=align(len(b),u32(opt+36));address=base+rva
    # Verify GetModuleHandleA's import, rather than trusting an arbitrary call.
    imports=offset(base+u32(opt+104));module_iat=None
    while u32(imports) or u32(imports+12):
        thunk=offset(base+(u32(imports)or u32(imports+16)));iat=u32(imports+16);i=0
        while u32(thunk+4*i):
            value=u32(thunk+4*i)
            if not value&0x80000000:
                name_at=offset(base+value)+2
                if b[name_at:b.index(0,name_at)]==b'GetModuleHandleA':module_iat=base+iat+4*i
            i+=1
        imports+=20
    assert module_iat==0x7b7b58
    code=bytearray()
    code+=b'\x51'  # preserve interface ECX across Win32 call
    code+=b'\x68'+struct.pack('<I',address+64)
    code+=b'\xff\x15'+struct.pack('<I',module_iat)
    code+=b'\x85\xc0\x74\x0d'  # absent module -> original reset
    code+=b'\x05'+struct.pack('<I',0x20a0)
    code+=b'\x3b\x05'+struct.pack('<I',0x735c6c)
    code+=b'\x74\x0d'  # exact current MMM callback -> keep it
    code+=b'\x59\x6a\x00\x8b\x01\xff\x90\x28\x04\x00\x00\xc3'
    # The reset path above is 12 bytes, so skip displacement is corrected here.
    code[28]=0x0c
    code+=b'\x59\xc3'
    code.extend(b'\xcc'*(64-len(code)));code+=b'mmm_loader.dll\0'
    size=align(len(code),u32(opt+36))
    b[at:at+10]=b'\xe8'+struct.pack('<i',address-(hook+5))+b'\x90'*5
    b[header:header+40]=struct.pack('<8sIIIIIIHHI',b'.lms\0\0\0\0',len(code),rva,size,raw,0,0,0,0,0x60000020)
    struct.pack_into('<H',b,nt+6,count+1)
    struct.pack_into('<I',b,opt+56,align(rva+len(code),u32(opt+32)))
    struct.pack_into('<I',b,opt+64,0)
    b.extend(bytes(raw-len(b)));b.extend(code);b.extend(bytes(size-len(code)))
    backup_dir=target.parent/'Development/backups'/('scoped-callback-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
    backup_dir.mkdir(parents=True);backup=backup_dir/target.name;shutil.copy2(target,backup)
    target.write_bytes(b)
    report={'target':str(target),'backup':str(backup),'beforeSha256':expected,'afterSha256':hashlib.sha256(b).hexdigest(),'stubAddress':hex(address),'experimental':True,'runtimeVerified':False,'reverted':False}
report_path.write_text(json.dumps(report,indent=2));print(json.dumps(report))
