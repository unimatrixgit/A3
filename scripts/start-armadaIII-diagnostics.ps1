$ErrorActionPreference='Stop'
# Main installation: intentionally no crash monitor or debugger.
if(!(Get-Process Armada2 -ErrorAction SilentlyContinue | Where-Object {$_.Path -eq 'D:\armadaIII\Armada2.exe'})){Start-Process -FilePath 'D:\armadaIII\Armada2.exe' -WorkingDirectory 'D:\armadaIII'}
