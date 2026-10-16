$ErrorActionPreference='Stop'
$target='D:\armadaIII'
$stage='D:\Xaramada-Modwork\bajor-rebuild'
if(Test-Path -LiteralPath (Join-Path $stage 'QUARANTINED.json')){throw 'Custom Bajoran assets are quarantined after a runtime regression. Keep the native recovery active.'}
$report=Get-Content -LiteralPath 'D:\aramada\reports\bajoran-release-validation.json' -Raw | ConvertFrom-Json
if($report.errors.Count -gt 0){throw 'Bajoran release validation has unresolved errors'}
$assets=Get-Content -LiteralPath 'D:\aramada\reports\bajoran-actual-assets.json' -Raw | ConvertFrom-Json
if($assets.errors.Count -gt 0){throw 'Actual model/texture validation has unresolved errors'}
$running=Get-CimInstance Win32_Process -Filter "Name='Armada2.exe'" | Where-Object {$_.ExecutablePath -eq 'D:\armadaIII\Armada2.exe'}
if($running){throw 'Close armadaIII before applying the regenerated faction.'}
$backup=Join-Path 'D:\Xaramada-Modwork\backups' ('bajor-full-rebuild-'+(Get-Date -Format 'yyyyMMdd-HHmmss'))
$applied=@()
foreach($file in Get-ChildItem -LiteralPath $stage -Recurse -File){
 if($file.Extension -notmatch '^\.(odf|tt|spr|aip|wav|tga|sod)$' -and $file.Name -ne 'events.dat'){continue}
 $relative=$file.FullName.Substring($stage.Length+1)
 $dest=Join-Path $target $relative
 if(-not ([IO.Path]::GetFullPath($dest)).StartsWith('D:\armadaIII\',[StringComparison]::OrdinalIgnoreCase)){throw 'Unexpected target path'}
 if(Test-Path -LiteralPath $dest){$old=Join-Path $backup $relative; New-Item -ItemType Directory -Path (Split-Path $old) -Force | Out-Null; Copy-Item -LiteralPath $dest -Destination $old; (Get-Item -LiteralPath $dest).IsReadOnly=$false}
 New-Item -ItemType Directory -Path (Split-Path $dest) -Force | Out-Null
 Copy-Item -LiteralPath $file.FullName -Destination $dest -Force
 if((Get-FileHash -LiteralPath $file.FullName).Hash -ne (Get-FileHash -LiteralPath $dest).Hash){throw "Copy verification failed: $relative"}
 if($file.Extension -match '^\.(odf|tt|spr|aip)$' -or $file.Name -eq 'events.dat'){
  $overlay=Join-Path 'D:\aramada\bajor\overlay' $relative
  New-Item -ItemType Directory -Path (Split-Path $overlay) -Force | Out-Null
  Copy-Item -LiteralPath $dest -Destination $overlay -Force
 }
 $applied += $relative
}
$manifest=Get-Content -LiteralPath 'D:\aramada\bajor\rebuild-manifest.json' -Raw | ConvertFrom-Json
$manifest.applied=$true
$manifest | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath 'D:\aramada\bajor\rebuild-manifest.json' -Encoding UTF8
$manifest | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath 'D:\aramada\bajor\manifest.json' -Encoding UTF8
[pscustomobject]@{target=$target;backup=$backup;files=$applied;copiedFilesVerified=$true;runtimeVerified=$false} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath 'D:\aramada\reports\bajoran-rebuild-apply.json' -Encoding UTF8
$status=Get-Content -LiteralPath 'D:\aramada\status.json' -Raw | ConvertFrom-Json
$status.current="Bajoran rebuild applied to armadaIII only: 19 ship roles, 14 buildings, 20 research pods, Universal Assembler, matching model-rendered icons, five AI profiles, all tech trees and 42 Kira/Sela synthetic command clips. $($applied.Count) files copied and verified. Correct Geometry hierarchy and Borg textures mapped. New-match visibility, assimilation and gameplay test still required. Backup: $backup"
foreach($feature in $status.features){
 if($feature.id -in @('bajor_roster','bajor_models','icons','bajor_ai','takeover','voices')){
  foreach($step in $feature.steps){if($step.label -notmatch 'Gameplay|in.game|observe|playback|visual confirmation|visual test'){$step.done=$true}}
 }
}
$status.steps=@(foreach($feature in $status.features){foreach($step in $feature.steps){[pscustomobject]@{label="$($feature.title): $($step.label)";done=$step.done}}})
$status | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath 'D:\aramada\status.json' -Encoding UTF8
Add-Content -LiteralPath 'D:\aramada\build.log' -Value "[$(Get-Date -Format o)] $($status.current)"
Write-Output "$($applied.Count) files applied and verified. armadaIII only; backup: $backup"

