$ErrorActionPreference='Stop'
Start-Process powershell.exe -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File','D:\aramada\scripts\crash-capture.ps1') -WindowStyle Hidden
if(!(Get-Process Armada2 -ErrorAction SilentlyContinue|Where-Object {$_.Path -eq 'D:\armadaIII\Armada2.exe'})){Start-Process -FilePath 'D:\armadaIII\Armada2.exe' -WorkingDirectory 'D:\armadaIII'}
