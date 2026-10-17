exec(open('D:/aramada/scripts/analyze-bajoran-crash.py').read().split("print('\\n'.join")[0])
print('\n'.join(asm(0x4d1590,180)))
for off in [0x40,0xf4,0x128,0x154]:
 a=struct.unpack('<I',read(c.Esi+off,4))[0];print('OBJECT',hex(off),hex(a),read(a,100))
print('RTTI',read(0x6eee08,150),read(0x6eee98,150))
