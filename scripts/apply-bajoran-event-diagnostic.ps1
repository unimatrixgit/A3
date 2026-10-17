$ErrorActionPreference = 'Stop'
if (Get-Process Armada2 -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq 'D:\armadaIII\Armada2.exe' }) { throw 'Armada III is running; no changes made.' }
$reportPath = 'D:\aramada\reports\bajoran-event-diagnostic.json'
$report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
$destination = 'D:\armadaIII\events.dat'
$staged = 'D:\Xaramada-Modwork\bajor-event-diagnostic\events.dat'
if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant() -ne $report.sourceSha256) { throw 'Active events file changed. Refresh diagnostic before applying.' }
if ((Get-FileHash -LiteralPath $staged -Algorithm SHA256).Hash.ToLowerInvariant() -ne $report.stagedSha256) { throw 'Staged file does not match validation.' }
$backup = 'D:\Xaramada-Modwork\backups\bajor-event-diagnostic-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
New-Item -ItemType Directory -Path $backup | Out-Null
Copy-Item -LiteralPath $destination -Destination (Join-Path $backup 'events.dat')
Copy-Item -LiteralPath $staged -Destination $destination -Force
if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant() -ne $report.stagedSha256) { throw 'Installed file failed verification.' }
Copy-Item -LiteralPath $destination -Destination 'D:\aramada\bajor\overlay\events.dat' -Force
$report.applied = $true
$report | Add-Member -Force -NotePropertyName backup -NotePropertyValue $backup
$report | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $reportPath -Encoding utf8
$statusPath = 'D:\aramada\status.json'
$status = Get-Content -LiteralPath $statusPath -Raw | ConvertFrom-Json
$status.current = 'Installed one-file Bajoran shared-event audio fallback diagnostic. Existing Federation recordings now provide Bajoran selections; seven duplicate sound removals and single starting heroes preserved. Backup and installed hash verified. Test a fresh Bajoran match; crash cause and stability remain unconfirmed.'
$feature = $status.features | Where-Object id -eq 'bajor_crash_diagnostic'
$feature.steps[3].done = $true
$status.steps = @($status.features | ForEach-Object { $featureTitle = $_.title; $_.steps | ForEach-Object { [pscustomobject]@{label=$featureTitle + ': ' + $_.label; done=$_.done} } })
$status | ConvertTo-Json -Depth 60 | Set-Content -LiteralPath $statusPath -Encoding utf8
Add-Content -LiteralPath 'D:\aramada\build.log' -Value ("`n[" + [DateTime]::UtcNow.ToString('o') + '] ' + $status.current)
Write-Output "One-file diagnostic installed. Backup: $backup"
