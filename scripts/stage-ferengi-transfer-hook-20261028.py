"""Stage a name-scoped Ferengi cargo handling hook; do not install the executable."""
from pathlib import Path
import sys,struct,hashlib,json,math
sys.path[:0]=['D:/Xaramada-Modwork/tools/crash-analysis','D:/Xaramada-Modwork/tools/native-patch-tests'];import pefile,capstone
from keystone import Ks,KS_ARCH_X86,KS_MODE_32
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
repo=Path('D:/aramada');stage=repo/'patches/drozana-commerce-20261028';source=Path('D:/armadaIII/Armada2.exe');raw=bytearray(source.read_bytes());pe=pefile.PE(data=raw);base=pe.OPTIONAL_HEADER.ImageBase;assert base==0x400000
assert pe.get_data(0x4ce370-base,11).hex()=='8b89cc010000e925b01800','GetOdfName implementation differs'
assert not(pe.OPTIONAL_HEADER.DllCharacteristics&0x40),'ASLR needs relocated hook calls'
ks=Ks(KS_ARCH_X86,KS_MODE_32);align=lambda n,a:(n+a-1)//a*a;last=pe.sections[-1];rva=align(last.VirtualAddress+max(last.Misc_VirtualSize,last.SizeOfRawData),pe.OPTIONAL_HEADER.SectionAlignment);offset=align(len(raw),pe.OPTIONAL_HEADER.FileAlignment);va=base+rva
header=pe.sections[0].get_file_offset()+40*len(pe.sections);assert header+40<=pe.sections[0].PointerToRawData,'No room for another section header'
hooks=[];payload=bytearray()
for entry,expected in [(0x4ae1c0,bytes.fromhex('558bec6aff')),(0x4ae440,bytes.fromhex('558bec5356'))]:
 original=pe.get_data(entry-base,5);assert original==expected,(hex(entry),original.hex())
 start=va+len(payload);asm='pushfd; pushad; mov ecx, dword ptr [ecx+0x40]; test ecx,ecx; jz done; call 0x4ce370; test eax,eax; jz done; mov edx,eax; mov ebx,512; scan: mov cl,byte ptr [eax]; test cl,cl; jz compare; cmp cl,92; je separator; cmp cl,47; jne next; separator: lea edx,[eax+1]; next: inc eax; dec ebx; jnz scan; jmp done; compare: '
 for i,char in enumerate('xfgtrade'):asm+=f'mov al,byte ptr [edx+{i}]; or al,32; cmp al,{ord(char)}; jne done; '
 asm+='mov al,byte ptr [edx+8]; test al,al; jz boost; cmp al,46; jne done; '
 for i,char in enumerate('odf',9):asm+=f'mov al,byte ptr [edx+{i}]; or al,32; cmp al,{ord(char)}; jne done; '
 asm+='cmp byte ptr [edx+12],0; jne done; boost: fld dword ptr [esp+44]; fadd st(0),st(0); fstp dword ptr [esp+44]; done: popad; popfd'
 encoded=bytes(ks.asm(asm,addr=start)[0]);resume=start+len(encoded);jump=bytes(ks.asm(f'jmp {entry+5}',addr=resume+5)[0]);assert len(jump)==5;code=encoded+original+jump;payload.extend(code);payload.extend(b'\x90'*((-len(payload))%16))
 loc=pe.get_offset_from_rva(entry-base);raw[loc:loc+5]=bytes(ks.asm(f'jmp {start}',addr=entry)[0]);hooks.append({'entry':entry,'cave':start,'restorePoint':resume,'original':original.hex(),'codeSize':len(code)})
raw.extend(b'\0'*(offset-len(raw)));size=align(len(payload),pe.OPTIONAL_HEADER.FileAlignment);raw.extend(payload+b'\0'*(size-len(payload)))
struct.pack_into('<8sIIIIIIHHI',raw,header,b'.fgdock\0',len(payload),rva,size,offset,0,0,0,0,0x60000020);struct.pack_into('<H',raw,pe.FILE_HEADER.get_field_absolute_offset('NumberOfSections'),len(pe.sections)+1);struct.pack_into('<I',raw,pe.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),align(rva+len(payload),pe.OPTIONAL_HEADER.SectionAlignment));struct.pack_into('<I',raw,pe.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfCode'),pe.OPTIONAL_HEADER.SizeOfCode+size)
patched=pefile.PE(data=raw);struct.pack_into('<I',raw,patched.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),patched.generate_checksum());patched=pefile.PE(data=raw)
# Emulate both full entry detours for exact names, paths, unrelated ships and amounts.
tests=[];registers=[UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_ECX,UC_X86_REG_EDX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]
for hook in hooks:
 for name,boost in [('xfgtrade',True),('XFGTRADE.ODF',True),('odf/ships/xfgtrade.odf',True),('odf\\ships\\xfgtrade.odf',True),('fcargo.odf',False),('xfgtrade2.odf',False),('xfgtrade.bad',False),('xsrepair',False)]:
  for amount in [0.,.25,50.,-5.]:
   uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(base,align(patched.OPTIONAL_HEADER.SizeOfImage,4096));uc.mem_write(base,bytes(patched.get_memory_mapped_image()));uc.mem_map(0x2000000,0x10000);uc.mem_map(0x3000000,0x4000);uc.mem_write(0x3000040,struct.pack('<I',0x3001000));uc.mem_write(0x3002000,name.encode()+b'\0');sp=0x2008000;uc.mem_write(sp,struct.pack('<IIf',0x400100,0x3003000,amount))
   initial={reg:0x123400+i*0x100 for i,reg in enumerate(registers)};initial[UC_X86_REG_ECX]=0x3000000
   for reg,value in initial.items():uc.reg_write(reg,value)
   uc.reg_write(UC_X86_REG_ESP,sp);uc.reg_write(UC_X86_REG_EFLAGS,0x246)
   def intercept(u,address,size,data):
    if address==0x4ce370:
     rsp=u.reg_read(UC_X86_REG_ESP);ret=struct.unpack('<I',u.mem_read(rsp,4))[0];u.reg_write(UC_X86_REG_EAX,0x3002000);u.reg_write(UC_X86_REG_ESP,rsp+4);u.reg_write(UC_X86_REG_EIP,ret)
    if address==hook['restorePoint']:u.emu_stop()
   uc.hook_add(UC_HOOK_CODE,intercept);uc.emu_start(hook['entry'],hook['restorePoint']+5,count=10000)
   result=struct.unpack('<f',uc.mem_read(sp+8,4))[0];assert result==amount*(2 if boost else 1),(name,result)
   assert uc.reg_read(UC_X86_REG_ESP)==sp and uc.reg_read(UC_X86_REG_EFLAGS)==0x246
   assert all(uc.reg_read(reg)==value for reg,value in initial.items());tests.append({'entry':hex(hook['entry']),'name':name,'amount':amount,'result':result})
p=stage/'engine-candidate/Armada2.exe';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
report={'status':'STAGED_NOT_INSTALLED','sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidateSha256':hashlib.sha256(raw).hexdigest(),'hooks':hooks,'emulatedTests':len(tests),'tests':tests,'scope':'Only CargoShipClass ODF name xfgtrade (case-insensitive, optional directory/.odf extension). Transfer amount doubled at LoadCargo and UnloadCargo entry. Other ships and station handling rates unchanged.','registersFlagsStackPreserved':True,'nativeFunctionCalled':'GameObjectClass::GetOdfName 0x4ce370','runtimeVerified':False};(stage/'ferengi-handling-native-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({'emulatedTests':len(tests),'shipsAffected':['xfgtrade'],'engineCandidateOnly':True,'runtimeVerified':False}))
