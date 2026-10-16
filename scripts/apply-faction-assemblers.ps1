$ErrorActionPreference='Stop'
$target='D:\armadaIII'
$stage='D:\Xaramada-Modwork\faction-assemblers'
$repo='D:\aramada'
$validation=Get-Content -LiteralPath "$repo\reports\faction-assembler-validation.json" -Raw | ConvertFrom-Json
if($validation.errors.Count -gt 0){throw 'Builder validation failed'}
$running=Get-CimInstance Win32_Process -Filter "Name='Armada2.exe'" | Where-Object {$_.ExecutablePath -eq "$target\Armada2.exe"}
if($running){throw 'Armada III is running; close it before applying builder files.'}
$backup=Join-Path 'D:\Xaramada-Modwork\backups' ('faction-assemblers-'+(Get-Date -Format 'yyyyMMdd-HHmmss'))
$files=@()
foreach($file in Get-ChildItem -LiteralPath $stage -Recurse -File){
 if($file.Extension -notmatch '^\.(odf|tt|spr|aip|tga|sod)$'){continue}
 $relative=$file.FullName.Substring($stage.Length+1)
 $dest=Join-Path $target $relative
 if(-not ([IO.Path]::GetFullPath($dest)).StartsWith('D:\armadaIII\',[StringComparison]::OrdinalIgnoreCase)){throw 'Unexpected game path'}
 $existed=Test-Path -LiteralPath $dest
 if($existed){$old=Join-Path $backup $relative;New-Item -ItemType Directory -Path (Split-Path $old) -Force | Out-Null;Copy-Item -LiteralPath $dest -Destination $old;(Get-Item -LiteralPath $dest).IsReadOnly=$false}
 New-Item -ItemType Directory -Path (Split-Path $dest) -Force | Out-Null
 Copy-Item -LiteralPath $file.FullName -Destination $dest -Force
 $hash=(Get-FileHash -LiteralPath $dest).Hash
 if($hash -ne (Get-FileHash -LiteralPath $file.FullName).Hash){throw "Verification failed: $relative"}
 if($file.Extension -match '^\.(odf|tt|spr|aip)$'){$overlay=Join-Path "$repo\bajor\overlay" $relative;New-Item -ItemType Directory -Path (Split-Path $overlay) -Force | Out-Null;Copy-Item -LiteralPath $dest -Destination $overlay -Force}
 $files += [pscustomobject]@{path=$relative;previouslyExisted=$existed;sha256=$hash}
}
[pscustomobject]@{target=$target;backup=$backup;files=$files;hashesVerified=$true;runtimeVerified=$false} | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath "$repo\reports\faction-assembler-apply.json" -Encoding UTF8
$status=Get-Content -LiteralPath "$repo\status.json" -Raw | ConvertFrom-Json
foreach($feature in $status.features){if($feature.id -in @('faction_builders','assembler_art','assembler_tech','no_8472_assembler')){foreach($step in $feature.steps){$step.done=$true}}}
$status.current="Faction builder patch applied to D:/armadaIII only: eight faction-specific Universal constructors with custom fabrication-pod variants, matching buttons/portraits, technology entries and 40 AI profiles. Borg Assembler includes Recycler; Borg Universal carries overflow facilities. Species 8472 removed from every Universal build list and all Universal production excluded from 8472. $($files.Count) files copied and hash-verified. Start a fresh match to test; runtime verification pending. Other Bajoran rebuild features remain staged."
$status.steps=@(foreach($feature in $status.features){foreach($step in $feature.steps){[pscustomobject]@{label="$($feature.title): $($step.label)";done=$step.done}}})
$status | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath "$repo\status.json" -Encoding UTF8
Add-Content -LiteralPath "$repo\build.log" -Value "[$(Get-Date -Format o)] $($status.current)"
Write-Output "$($files.Count) builder patch files applied and hash-verified. Backup: $backup"
