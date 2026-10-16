$ErrorActionPreference='Stop'
$target='D:\armadaIII';$stage='D:\Xaramada-Modwork\hero-reinforcements';$repo='D:\aramada'
if(Test-Path -LiteralPath (Join-Path $stage 'QUARANTINED.json')){throw 'Experimental reinforcement producer is quarantined after match-load crashes.'}
$report=Get-Content -LiteralPath "$repo\reports\hero-reinforcement-validation.json" -Raw | ConvertFrom-Json
if($report.errors.Count -gt 0){throw 'Reference validation has errors'}
if(Get-CimInstance Win32_Process -Filter "Name='Armada2.exe'" | Where-Object {$_.ExecutablePath -eq "$target\Armada2.exe"}){throw 'Close Armada III before applying the test patch'}
$backup=Join-Path 'D:\Xaramada-Modwork\backups' ('hero-reinforcements-'+(Get-Date -Format 'yyyyMMdd-HHmmss'));$files=@()
foreach($file in Get-ChildItem -LiteralPath $stage -Recurse -File){
 if($file.Extension -notmatch '^\.(odf|tt|spr)$' -and $file.Name -ne 'events.dat'){continue}
 $relative=$file.FullName.Substring($stage.Length+1);$dest=Join-Path $target $relative
 if(-not ([IO.Path]::GetFullPath($dest)).StartsWith('D:\armadaIII\',[StringComparison]::OrdinalIgnoreCase)){throw 'Unexpected target'}
 $existed=Test-Path -LiteralPath $dest
 if($existed){$old=Join-Path $backup $relative;New-Item -ItemType Directory -Path (Split-Path $old) -Force | Out-Null;Copy-Item -LiteralPath $dest -Destination $old;(Get-Item -LiteralPath $dest).IsReadOnly=$false}
 New-Item -ItemType Directory -Path (Split-Path $dest) -Force | Out-Null;Copy-Item -LiteralPath $file.FullName -Destination $dest -Force
 $hash=(Get-FileHash -LiteralPath $dest).Hash
 if($hash -ne (Get-FileHash -LiteralPath $file.FullName).Hash){throw "Hash mismatch $relative"}
 $overlay=Join-Path "$repo\bajor\overlay" $relative;New-Item -ItemType Directory -Path (Split-Path $overlay) -Force | Out-Null;Copy-Item -LiteralPath $dest -Destination $overlay -Force
 $files+=[pscustomobject]@{path=$relative;previouslyExisted=$existed;sha256=$hash}
}
[pscustomobject]@{target=$target;backup=$backup;files=$files;hashesVerified=$true;runtimeVerified=$false;testBuild=$true} | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath "$repo\reports\hero-reinforcement-apply.json" -Encoding UTF8
$status=Get-Content -LiteralPath "$repo\status.json" -Raw | ConvertFrom-Json
$feature=$status.features | Where-Object id -eq 'hero_reinforcements';for($i=0;$i -lt 5;$i++){$feature.steps[$i].done=$true}
$status.current="Ready for your test in D:/armadaIII: nine faction heroes have a controllable reinforcement build popup with wormhole arrival. Weyoun calls a Jem'Hadar battlecruiser; Kira calls Enterprise-E with original Picard voices. Uses normal resource costs and a 15-second build. Bajoran base is Deep Space 9 with DS9 model/icon; Cardassian base is Terok Nor; station name pools updated. $($files.Count) files copied and verified. Fresh-match movement, popup and arrival tests pending."
$status.steps=@(foreach($feature in $status.features){foreach($step in $feature.steps){[pscustomobject]@{label="$($feature.title): $($step.label)";done=$step.done}}})
$status | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath "$repo\status.json" -Encoding UTF8
Add-Content -LiteralPath "$repo\build.log" -Value "[$(Get-Date -Format o)] $($status.current)"
Write-Output "$($files.Count) files applied and hash-verified. Backup: $backup"
