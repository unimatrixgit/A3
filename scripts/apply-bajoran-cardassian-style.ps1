$ErrorActionPreference='Stop'
if(Test-Path -LiteralPath 'D:\Xaramada-Modwork\bajor-cardassian-style\QUARANTINED.json'){throw 'Style package quarantined after loading crash; prepare a separate isolated visual test.'}
if(Get-Process Armada2 -ErrorAction SilentlyContinue | Where-Object {$_.Path -eq 'D:\armadaIII\Armada2.exe'}){throw 'Game is running; no changes made.'}
$reportPath='D:\aramada\reports\bajoran-cardassian-style.json';$r=Get-Content -LiteralPath $reportPath -Raw|ConvertFrom-Json
if(@($r.errors).Count){throw 'Building style package validation failed.'}
foreach($f in $r.files){if((Get-FileHash -LiteralPath (Join-Path $r.target $f.path) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $f.sourceSha256){throw "Active file changed: $($f.path)"};if((Get-FileHash -LiteralPath (Join-Path $r.stage $f.path) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $f.sha256){throw "Staged file changed: $($f.path)"}}
$backup='D:\Xaramada-Modwork\backups\bajoran-cardassian-style-'+(Get-Date -Format 'yyyyMMdd-HHmmss')
foreach($f in $r.files){$saved=Join-Path $backup $f.path;New-Item -ItemType Directory -Path (Split-Path $saved) -Force|Out-Null;Copy-Item -LiteralPath (Join-Path $r.target $f.path) -Destination $saved}
foreach($f in $r.files){$dest=Join-Path $r.target $f.path;Copy-Item -LiteralPath (Join-Path $r.stage $f.path) -Destination $dest -Force;if((Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant() -ne $f.sha256){throw "Installed verification failed: $($f.path)"}}
foreach($f in $r.files){$dest=Join-Path 'D:\aramada\bajor\overlay' $f.path;New-Item -ItemType Directory -Path (Split-Path $dest) -Force|Out-Null;Copy-Item -LiteralPath (Join-Path $r.target $f.path) -Destination $dest -Force}
$r.applied=$true;$r|Add-Member -Force -NotePropertyName backup -NotePropertyValue $backup;$r|ConvertTo-Json -Depth 35|Set-Content -LiteralPath $reportPath -Encoding utf8
$statusPath='D:\aramada\status.json';$s=Get-Content -LiteralPath $statusPath -Raw|ConvertFrom-Json;$s.current='Installed Cardassian-style appearances for 13 Bajoran facilities using existing native models/textures and matching GUI icons. DS9 retained; regular constructor menu follows Cardassian core order with identical building access. Harvesting weapons, automatic freighter configuration, AI, audio, costs and tech unchanged. Backup/hashes verified. Fresh Bajoran construction test required; artwork runtime test pending.';$s.lastCompleted=[pscustomobject]@{task='Apply Cardassian-style Bajoran buildings and menu order';time=[DateTime]::UtcNow.ToString('o');applied=$true;runtimeVerified=$false};$s|ConvertTo-Json -Depth 60|Set-Content -LiteralPath $statusPath -Encoding utf8;Add-Content -LiteralPath D:\aramada\build.log -Value ("`n["+[DateTime]::UtcNow.ToString('o')+'] '+$s.current);Write-Output "15 Cardassian-style Bajoran files installed. Backup: $backup"



