"""Read-only disassembly of the isolated stock engine's mission load path."""
from pathlib import Path
import json
import re
import struct
import sys

sys.path.insert(0, 'D:/Xaramada-Modwork/tools/crash-analysis')
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

root = Path('D:/ArmadaLab')
data = (root / 'Armada2.exe').read_bytes()
u16 = lambda o: struct.unpack_from('<H', data, o)[0]
u32 = lambda o: struct.unpack_from('<I', data, o)[0]
nt = u32(60)
optional = nt + 24
base = u32(optional + 28)
table = optional + u16(nt + 20)
sections = [(u32(table + 40*i + 12), u32(table + 40*i + 16),
             u32(table + 40*i + 20)) for i in range(u16(nt + 6))]

def offset(address):
    rva = address - base
    for va, size, raw in sections:
        if va <= rva < va + size:
            return raw + rva - va
    raise ValueError(f'Address outside backed sections: {address:#x}')

symbols = {}
for line in (root / 'armada2.map').read_text(errors='replace').splitlines():
    match = re.match(r'\s+[0-9a-f]+:[0-9a-f]+\s+(\S+)\s+([0-9a-f]{8})\b', line, re.I)
    if match:
        symbols[int(match[2], 16)] = match[1]

cs = Cs(CS_ARCH_X86, CS_MODE_32)
regions = [(0x401a30, 0x290), (0x451c20, 0x1a0), (0x457d90, 0x30),
           (0x458440, 0x190), (0x47ce00, 0x150)]
result = {'target': str(root), 'readOnly': True, 'regions': []}
for start, size in regions:
    rows = []
    for instruction in cs.disasm(data[offset(start):offset(start)+size], start):
        row = {'address': hex(instruction.address), 'operation': instruction.mnemonic,
               'operands': instruction.op_str}
        if instruction.address in symbols:
            row['symbol'] = symbols[instruction.address]
        if instruction.mnemonic in ('call', 'jmp') and instruction.op_str.startswith('0x'):
            row['targetSymbol'] = symbols.get(int(instruction.op_str, 16), '')
        rows.append(row)
    result['regions'].append({'start': hex(start), 'instructions': rows})
callback = u32(offset(0x6af380 + 0x428))
result['callbackSetter'] = {'address': hex(callback), 'symbol': symbols.get(callback)}
destination = Path('D:/aramada/reports/native-save-lifecycle.json')
destination.write_text(json.dumps(result, indent=2))
print(json.dumps({'report': str(destination), 'callbackSetter': result['callbackSetter']}))
