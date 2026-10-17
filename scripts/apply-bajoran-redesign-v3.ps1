$ErrorActionPreference='Stop'
$repo='D:\aramada'
$releasePath=Join-Path $repo 'reports\bajoran-redesign-v3-release.json'
$r=Get-Content -LiteralPath $releasePath -Raw | ConvertFrom-Json
$v=Get-Content -LiteralPath (Join-Path $repo 'reports\bajoran-redesign-v3-validation.json') -Raw | ConvertFrom-Json
$target=[IO.Path]::GetFullPath($r.target).TrimEnd('\')
if($target -ne 'D:\armadaIII'){throw 'Unexpected target'}
if(@($v.errors).Count){throw 'Validation failed'}
if(Get-Process Armada2 -ErrorAction SilentlyContinue | Where-Object {$_.Path -eq (Join-Path $target 'Armada2.exe')}){throw 'Game is running'}
foreach($f in $r.files){
 $dest=[IO.Path]::GetFullPath((Join-Path $target $f.path))
 if(-not $dest.StartsWith($target+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Invalid destination'}
 $src=Join-Path $r.stage $f.path
 if((Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash -ne $f.sha256){throw "Stage mismatch: $($f.path)"}
 if($f.sourceSha256){if((Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash -ne $f.sourceSha256){throw "Live mismatch: $($f.path)"}}
 elseif(Test-Path -LiteralPath $dest){throw "New file already exists: $($f.path)"}
}
$backup='D:\Xaramada-Modwork\backups\bajor-redesign-v3-'+(Get-Date -Format yyyyMMdd-HHmmss)
New-Item -ItemType Directory -Path $backup | Out-Null
$newFiles=@()
foreach($f in $r.files){
 $dest=Join-Path $target $f.path
 if(Test-Path -LiteralPath $dest){$save=Join-Path $backup $f.path;New-Item -ItemType Directory -Path (Split-Path $save) -Force | Out-Null;Copy-Item -LiteralPath $dest -Destination $save}
 else{$newFiles+=$f.path}
}
$newFiles | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $backup 'new-files.json') -Encoding UTF8
foreach($f in $r.files){
 $dest=Join-Path $target $f.path
 New-Item -ItemType Directory -Path (Split-Path $dest) -Force | Out-Null
 Copy-Item -LiteralPath (Join-Path $r.stage $f.path) -Destination $dest -Force
 if((Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash -ne $f.sha256){throw "Installed mismatch: $($f.path)"}
 if([IO.Path]::GetExtension($dest) -in @('.odf','.tt','.spr','.cmd')){
 $mirror=Join-Path $repo ('bajor\overlay\'+$f.path)
 New-Item -ItemType Directory -Path (Split-Path $mirror) -Force | Out-Null
 Copy-Item -LiteralPath $dest -Destination $mirror -Force
 }
}
$r.applied=$true
$r | Add-Member -NotePropertyName backup -NotePropertyValue $backup -Force
$r | Add-Member -NotePropertyName hashesVerified -NotePropertyValue $true -Force
$r | Add-Member -NotePropertyName appliedAt -NotePropertyValue ([DateTime]::UtcNow.ToString('o')) -Force
$r | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath $releasePath -Encoding UTF8
@{target=$target;backup=$backup;files=@($r.files).Count;hashesVerified=$true;runtimeVerified=$false;appliedAt=$r.appliedAt} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $repo 'reports\bajoran-redesign-v3-apply.json') -Encoding UTF8
$ledgerPath=Join-Path $repo 'reports\bajoran-test-overrides.json'
$l=Get-Content -LiteralPath $ledgerPath -Raw | ConvertFrom-Json
$l | Add-Member -NotePropertyName restorationPending -NotePropertyValue $false -Force
$l | Add-Member -NotePropertyName restoredAt -NotePropertyValue $r.appliedAt -Force
$l | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $ledgerPath -Encoding UTF8
Write-Output "Installed and hash-verified $(@($r.files).Count) files. Backup: $backup"
