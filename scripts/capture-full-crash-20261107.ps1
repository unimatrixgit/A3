$ErrorActionPreference='Stop'
$target='D:\ArmadaLab\Armada2.exe'
$folder='D:\Xaramada-Modwork\diagnostics\lab-crash-20261107-full'
New-Item -ItemType Directory -Path $folder -Force | Out-Null
$deadline=(Get-Date).AddHours(8)
do {
 $game=Get-Process Armada2 -ErrorAction SilentlyContinue | Where-Object {$_.Path -eq $target} | Select-Object -First 1
 if($game){break}
 Start-Sleep -Seconds 1
} while((Get-Date) -lt $deadline)
if(!$game){'No game launched before timeout.' | Set-Content "$folder\capture.log";exit}
& 'D:\Xaramada-Modwork\tools\procdump\procdump.exe' -accepteula -ma -e -n 1 $game.Id $folder *> "$folder\capture.log"
