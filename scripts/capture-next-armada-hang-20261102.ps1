$ErrorActionPreference='Continue'
$lock=New-Object Threading.Mutex($false,'Local\ArmadaIIIHangCapture20261102')
if(!$lock.WaitOne(0)){exit}
$diagnosticRoot='D:\Xaramada-Modwork\diagnostics'
$deadline=(Get-Date).AddHours(4)
try {
 while((Get-Date) -lt $deadline){
  $game=Get-Process Armada2 -ErrorAction SilentlyContinue | Where-Object Path -EQ 'D:\ArmadaLab\Armada2.exe' | Select-Object -First 1
  if($game){
   if((Get-PSDrive D).Free -lt 4GB){exit}
   $session=Join-Path $diagnosticRoot ('hang-'+(Get-Date -Format yyyyMMdd-HHmmss)+'-'+$game.Id)
   New-Item -ItemType Directory -Path $session -Force | Out-Null
   @{pid=$game.Id;image=$game.Path;trigger='Unresponsive window for at least5 seconds';terminatesGame=$false;started=(Get-Date).ToString('o')} | ConvertTo-Json | Set-Content (Join-Path $session 'capture.json')
   & 'D:\Xaramada-Modwork\tools\procdump\procdump.exe' -accepteula -ma -h -n 1 $game.Id $session 2>&1 | Out-File (Join-Path $session 'procdump.log')
   break
  }
  Start-Sleep -Seconds 2
 }
} finally {$lock.ReleaseMutex();$lock.Dispose()}
