$ErrorActionPreference='Stop'
if(Get-Process Armada2 -ErrorAction SilentlyContinue | Where-Object {$_.Path -eq 'D:\armadaIII\Armada2.exe'}){throw 'Armada III is running; no changes made.'}
$reportPath='D:\aramada\reports\bajoran-ai-diagnostic.json'
$r=Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
foreach($f in $r.files){
 if((Get-FileHash -LiteralPath (Join-Path $r.target $f.path) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $f.sourceSha256){throw "Active file changed: $($f.path). Refresh patch."}
 if((Get-FileHash -LiteralPath (Join-Path $r.stage $f.path) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $f.stagedSha256){throw "Staged validation failed: $($f.path)"}
}
$backup='D:\Xaramada-Modwork\backups\bajor-ai-diagnostic-'+(Get-Date -Format 'yyyyMMdd-HHmmss')
foreach($f in $r.files){$dest=Join-Path $r.target $f.path;$saved=Join-Path $backup $f.path;New-Item -ItemType Directory -Path (Split-Path $saved) -Force | Out-Null;Copy-Item -LiteralPath $dest -Destination $saved}
foreach($f in $r.files){$dest=Join-Path $r.target $f.path;Copy-Item -LiteralPath (Join-Path $r.stage $f.path) -Destination $dest -Force;if((Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant() -ne $f.stagedSha256){throw "Installed verification failed: $($f.path)"};Copy-Item -LiteralPath $dest -Destination (Join-Path 'D:\aramada\bajor\overlay' $f.path) -Force}
$r.applied=$true;$r | Add-Member -Force -NotePropertyName backup -NotePropertyValue $backup;$r | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $reportPath -Encoding utf8
$statusPath='D:\aramada\status.json';$s=Get-Content -LiteralPath $statusPath -Raw | ConvertFrom-Json;$s.current='Installed six-file Bajoran AI diagnostic: five basic economy/research/defense profiles and corrected Bajoran mining freighter link. Advanced, Universal Assembler and hero production temporarily excluded from AI only; player options, visuals and audio patch preserved. Backup and hashes verified. Test against Bajoran AI; runtime result pending.';$s.lastCompleted=[pscustomobject]@{task='Apply Bajoran AI diagnostic';time=[DateTime]::UtcNow.ToString('o');applied=$true;runtimeVerified=$false};$s | ConvertTo-Json -Depth 60 | Set-Content -LiteralPath $statusPath -Encoding utf8;Add-Content -LiteralPath D:\aramada\build.log -Value ("`n["+[DateTime]::UtcNow.ToString('o')+'] '+$s.current)
Write-Output "Applied six files. Backup: $backup"
