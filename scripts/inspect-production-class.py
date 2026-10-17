exec(open('D:/aramada/scripts/analyze-bajoran-crash-production.py').read().split("print('\\n'.join")[0])
cls=struct.unpack('<I',read(c.Esi+0x40,4))[0];print('class',hex(cls))
for off in range(0,0x500,4):
 b=read(cls+off,4)
 if len(b)<4:continue
 ptr=struct.unpack('<I',b)[0];v=read(ptr,90);s=v.split(b'\0')[0]
 if 3<len(s)<85 and all(32<=x<127 for x in s):print(hex(off),hex(ptr),s)
a=struct.unpack('<I',read(cls+0x144,4))[0];end=struct.unpack('<I',read(cls+0x148,4))[0];print('weapon vector',hex(a),hex(end),read(a,end-a).hex())
print('instance str',re.findall(rb'[ -~]{5,}',read(cls,4096)))
