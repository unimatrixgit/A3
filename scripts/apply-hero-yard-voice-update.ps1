$ErrorActionPreference='Stop'
$repo='D:\aramada';$target='D:\armadaIII';$stages=@('D:\Xaramada-Modwork\hero-yard-release','D:\Xaramada-Modwork\locutus-voices')
if(Get-CimInstance Win32_Process -Filter "Name='Armada2.exe'" | Where-Object {$_.ExecutablePath -eq "$target\Armada2.exe"}){throw 'Close Armada III before applying the prepared hero-yard and voice update'}
$checks=Get-Content -LiteralPath "$repo\reports\hero-yard-validation.json" -Raw | ConvertFrom-Json
$audio=Get-Content -LiteralPath "$repo\reports\locutus-voice-format-validation.json" -Raw | ConvertFrom-Json
if($checks.errors.Count -gt 0 -or $audio.errors.Count -gt 0){throw 'Prepared package validation has errors'}
$backup=Join-Path 'D:\Xaramada-Modwork\backups' ('hero-yard-voice-update-'+(Get-Date -Format 'yyyyMMdd-HHmmss'));$files=@();$seen=@{}
foreach($stage in $stages){foreach($file in Get-ChildItem -LiteralPath $stage -Recurse -File){
 if($file.Extension -notmatch '^\.(odf|tt|spr|aip|sod|tga|wav)$' -and $file.Name -ne 'events.dat'){continue}
 $rel=$file.FullName.Substring($stage.Length+1);$dest=Join-Path $target $rel
 if(-not ([IO.Path]::GetFullPath($dest)).StartsWith('D:\armadaIII\',[StringComparison]::OrdinalIgnoreCase)){throw 'Unexpected game path'}
 if($seen.ContainsKey($rel)){throw "Overlapping staged file $rel"};$seen[$rel]=$true
 $existed=Test-Path -LiteralPath $dest
 if($existed){$old=Join-Path $backup $rel;New-Item -ItemType Directory -Path (Split-Path $old) -Force | Out-Null;Copy-Item -LiteralPath $dest -Destination $old;(Get-Item -LiteralPath $dest).IsReadOnly=$false}
 New-Item -ItemType Directory -Path (Split-Path $dest) -Force | Out-Null;Copy-Item -LiteralPath $file.FullName -Destination $dest -Force
 $hash=(Get-FileHash -LiteralPath $dest).Hash;if($hash -ne (Get-FileHash -LiteralPath $file.FullName).Hash){throw "Hash mismatch $rel"}
 if($file.Extension -match '^\.(odf|tt|spr|aip)$' -or $file.Name -eq 'events.dat'){$overlay=Join-Path "$repo\bajor\overlay" $rel;New-Item -ItemType Directory -Path (Split-Path $overlay) -Force | Out-Null;Copy-Item -LiteralPath $dest -Destination $overlay -Force}
 $files += [pscustomobject]@{path=$rel;previouslyExisted=$existed;sha256=$hash}
}}
[pscustomobject]@{target=$target;backup=$backup;files=$files;hashesVerified=$true;runtimeVerified=$false} | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath "$repo\reports\hero-yard-voice-apply.json" -Encoding UTF8
$status=Get-Content -LiteralPath "$repo\status.json" -Raw | ConvertFrom-Json
foreach($feature in $status.features){
 switch($feature.id){
 'yard_names' {foreach($step in $feature.steps){$step.done=$true}}
 'yard_order' {foreach($step in $feature.steps){$step.done=$true}}
 '8472' {for($i=0;$i -lt ($feature.steps.Count-1);$i++){$feature.steps[$i].done=$true}}
 'locutus_original_voice' {for($i=0;$i -lt 4;$i++){$feature.steps[$i].done=$true}}
 'cooper_bioship' {$feature.steps[3].label='Applied; gameplay and fallback voice test pending';$feature.steps[3].done=$false}
 }
}
$status.current="Installed in D:/armadaIII: faction hero-yard names/order and matched tech requirements, three 8472 hero variants including Cooper's Command Bioship, native-style model buttons and five 8472 AI updates. Starting/Omega Locutus now use 21 downloaded original-game recordings through private command events. Cooper uses the native 8472 voice fallback; original STO Cooper audio was not obtained. Hero calling remains removed; the Cardassian science ship stays restored. $($files.Count) files copied and verified. Fresh-match gameplay and audio playback tests remain pending."
$status.steps=@(foreach($feature in $status.features){foreach($step in $feature.steps){[pscustomobject]@{label="$($feature.title): $($step.label)";done=$step.done}}})
$status | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath "$repo\status.json" -Encoding UTF8
Add-Content -LiteralPath "$repo\build.log" -Value "[$(Get-Date -Format o)] $($status.current)"
Write-Output "$($files.Count) files applied and verified. Backup: $backup"
