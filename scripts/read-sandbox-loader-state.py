"""Read diagnostic flags from the isolated game; never write process memory."""
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import struct
import subprocess

command = "Get-Process Armada2 | Select-Object Id,Path,@{n='loader';e={@($_.Modules | Where-Object ModuleName -eq 'mmm_loader.dll' | ForEach-Object {$_.BaseAddress.ToInt64()})}} | ConvertTo-Json -Compress"
shell = 'C:/Users/thoma/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
process = json.loads(subprocess.check_output([shell, '-NoProfile', '-Command', command], text=True))
assert isinstance(process, dict), 'Expected exactly one game process'
assert process['Path'].lower() == 'd:\\armadalab\\armada2.exe', 'Read only the separate test game'
loaders = process['loader'] if isinstance(process['loader'], list) else [process['loader']]
assert len(loaders) == 1 and isinstance(loaders[0], int), 'Loader is not present yet'
k = ctypes.WinDLL('kernel32', use_last_error=True)
k.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
k.OpenProcess.restype = wintypes.HANDLE
k.ReadProcessMemory.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
k.CloseHandle.argtypes = [wintypes.HANDLE]
handle = k.OpenProcess(0x410, False, process['Id'])
if not handle:
    raise ctypes.WinError(ctypes.get_last_error())
def read(address, size):
    buffer = ctypes.create_string_buffer(size)
    count = ctypes.c_size_t()
    if not k.ReadProcessMemory(handle, address, buffer, size, ctypes.byref(count)):
        raise ctypes.WinError(ctypes.get_last_error())
    assert count.value == size
    return buffer.raw
try:
    profile = struct.unpack('<I', read(0x76b5ac, 4))[0]
    base = loaders[0]
    result = {'target': process['Path'], 'readOnly': True,
              'profileGuard84': read(profile+0x84, 1)[0],
              'scriptInitFlag': read(base+0x19ed74, 1)[0],
              'inputCallback': hex(struct.unpack('<I', read(0x735c6c, 4))[0]),
              'interfacePointer': hex(struct.unpack('<I', read(base+0x19ed50, 4))[0]),
              'fleetOpsFlag': read(base+0x1ae978, 1)[0]}
finally:
    k.CloseHandle(handle)
Path('D:/aramada/reports/sandbox-loader-state.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result))
