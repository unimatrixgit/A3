$ErrorActionPreference='Stop'
if(Get-Process Armada2 -ErrorAction SilentlyContinue | Where-Object {$_.Path -eq 'D:\armadaIII\Armada2.exe'}){throw 'Game is running; no changes made.'}
$reportPath='D:\aramada\reports\bajoran-ds9-animation-recovery.json';$r=Get-Content -LiteralPath $reportPath -Raw|ConvertFrom-Json
foreach($f in $r.files){if((Get-FileHash -LiteralPath (Join-Path $r.target $f.path) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $f.sourceSha256){throw "Active file changed: $($f.path)"};if((Get-FileHash -LiteralPath (Join-Path $r.stage $f.path) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $f.sha256){throw "Staged file changed: $($f.path)"}}
$backup='D:\Xaramada-Modwork\backups\bajoran-ds9-animation-recovery-'+(Get-Date -Format 'yyyyMMdd-HHmmss')
foreach($f in $r.files){$saved=Join-Path $backup $f.path;New-Item -ItemType Directory -Path (Split-Path $saved) -Force|Out-Null;Copy-Item -LiteralPath (Join-Path $r.target $f.path) -Destination $saved}
foreach($f in $r.files){$dest=Join-Path $r.target $f.path;Copy-Item -LiteralPath (Join-Path $r.stage $f.path) -Destination $dest -Force;if((Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant() -ne $f.sha256){throw "Installed verification failed: $($f.path)"}}
foreach($f in $r.files){$dest=Join-Path 'D:\aramada\bajor\overlay' $f.path;New-Item -ItemType Directory -Path (Split-Path $dest) -Force|Out-Null;Copy-Item -LiteralPath (Join-Path $r.target $f.path) -Destination $dest -Force}
$r.applied=$true;$r|Add-Member -Force -NotePropertyName backup -NotePropertyValue $backup;$r|ConvertTo-Json -Depth 35|Set-Content -LiteralPath $reportPath -Encoding utf8
$statusPath='D:\aramada\status.json';$s=Get-Content -LiteralPath $statusPath -Raw|ConvertFrom-Json;$s.current='Installed one-file DS9 construction diagnostic: removed animation/buildAnimation requests absent from supplied DS9 definition; its model has zero animation channels. DS9 appearance/scale/weapons/production/stats unchanged. AI, audio, harvester fix and temporary test overrides retained. Backup/hash verified. Fresh DS9 construction test required; recovery unconfirmed.';$s.lastCompleted=[pscustomobject]@{task='Remove unsupported DS9 animation requests';time=[DateTime]::UtcNow.ToString('o');applied=$true;runtimeVerified=$false};$s|ConvertTo-Json -Depth 60|Set-Content -LiteralPath $statusPath -Encoding utf8;Add-Content -LiteralPath D:\aramada\build.log -Value ("`n["+[DateTime]::UtcNow.ToString('o')+'] '+$s.current);Write-Output "DS9 animation diagnostic installed. Backup: $backup"



