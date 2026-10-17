$ErrorActionPreference='Stop'
if(Get-Process Armada2 -ErrorAction SilentlyContinue | Where-Object {$_.Path -eq 'D:\armadaIII\Armada2.exe'}){throw 'Game is running; no changes made.'}
$reportPath='D:\aramada\reports\bajoran-completion-audio-diagnostic.json';$r=Get-Content -LiteralPath $reportPath -Raw|ConvertFrom-Json
foreach($f in $r.files){if((Get-FileHash -LiteralPath (Join-Path $r.target $f.path) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $f.sourceSha256){throw "Active file changed: $($f.path)"};if((Get-FileHash -LiteralPath (Join-Path $r.stage $f.path) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $f.sha256){throw "Staged file changed: $($f.path)"}}
$backup='D:\Xaramada-Modwork\backups\bajoran-completion-audio-diagnostic-'+(Get-Date -Format 'yyyyMMdd-HHmmss')
foreach($f in $r.files){$saved=Join-Path $backup $f.path;New-Item -ItemType Directory -Path (Split-Path $saved) -Force|Out-Null;Copy-Item -LiteralPath (Join-Path $r.target $f.path) -Destination $saved}
foreach($f in $r.files){$dest=Join-Path $r.target $f.path;Copy-Item -LiteralPath (Join-Path $r.stage $f.path) -Destination $dest -Force;if((Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant() -ne $f.sha256){throw "Installed verification failed: $($f.path)"}}
foreach($f in $r.files){$dest=Join-Path 'D:\aramada\bajor\overlay' $f.path;New-Item -ItemType Directory -Path (Split-Path $dest) -Force|Out-Null;Copy-Item -LiteralPath (Join-Path $r.target $f.path) -Destination $dest -Force}
$r.applied=$true;$r|Add-Member -Force -NotePropertyName backup -NotePropertyValue $backup;$r|ConvertTo-Json -Depth 35|Set-Content -LiteralPath $reportPath -Encoding utf8
$statusPath='D:\aramada\status.json';$s=Get-Content -LiteralPath $statusPath -Raw|ConvertFrom-Json;$s.current='Installed one-file Bajoran construction announcement diagnostic: six missing WAV references replaced with installed recordings used by shared construction events. Models, menus, stats, AI, hero fleets and events.dat unchanged. Backup and hash verified. Test individual structure completion; crash cause remains unconfirmed.';$s.lastCompleted=[pscustomobject]@{task='Correct Bajoran construction sound references';time=[DateTime]::UtcNow.ToString('o');applied=$true;runtimeVerified=$false};$s|ConvertTo-Json -Depth 60|Set-Content -LiteralPath $statusPath -Encoding utf8;Add-Content -LiteralPath D:\aramada\build.log -Value ("`n["+[DateTime]::UtcNow.ToString('o')+'] '+$s.current);Write-Output "Construction audio diagnostic installed. Backup: $backup"



