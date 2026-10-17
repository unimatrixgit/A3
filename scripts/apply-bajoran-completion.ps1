param([ValidateSet('Visuals','AI')][string]$Part='Visuals')
$ErrorActionPreference='Stop'
if(Test-Path -LiteralPath 'D:\Xaramada-Modwork\bajor-completion-v2\QUARANTINED.json'){throw 'Custom Bajoran visual release is quarantined after repeated crashes. Prepare a separate validated diagnostic.'}
if(Get-Process Armada2 -ErrorAction SilentlyContinue | Where-Object {$_.Path -eq 'D:\armadaIII\Armada2.exe'}){throw 'Armada III is running; close it before installation.'}
$repo='D:\aramada'
$r=Get-Content -LiteralPath (Join-Path $repo 'reports\bajoran-completion-release.json') -Raw | ConvertFrom-Json
$v=Get-Content -LiteralPath (Join-Path $repo 'reports\bajoran-completion-validation.json') -Raw | ConvertFrom-Json
if(@($v.errors).Count){throw 'Completion package validation failed.'}
$files=@($r.files | Where-Object {if($Part -eq 'AI'){$_.path.EndsWith('.aip')}else{!$_.path.EndsWith('.aip')}})
foreach($f in $files){$dest=Join-Path $r.target $f.path;$src=Join-Path $r.stage $f.path
 if((Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash.ToLowerInvariant() -ne $f.sha256){throw "Staged file changed: $($f.path)"}
 if($f.sourceSha256){if(!(Test-Path -LiteralPath $dest) -or (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant() -ne $f.sourceSha256){throw "Active file changed: $($f.path). Refresh package before applying."}}elseif(Test-Path -LiteralPath $dest){throw "New target unexpectedly exists: $($f.path)"}
}
$backup='D:\Xaramada-Modwork\backups\bajor-completion-'+$Part.ToLowerInvariant()+'-'+(Get-Date -Format 'yyyyMMdd-HHmmss')
New-Item -ItemType Directory -Path $backup | Out-Null
foreach($f in $files){$dest=Join-Path $r.target $f.path;if(Test-Path -LiteralPath $dest){$saved=Join-Path $backup $f.path;New-Item -ItemType Directory -Path (Split-Path $saved) -Force | Out-Null;Copy-Item -LiteralPath $dest -Destination $saved}}
$eventHash=(Get-FileHash -LiteralPath D:\armadaIII\events.dat -Algorithm SHA256).Hash
foreach($f in $files){$dest=Join-Path $r.target $f.path;New-Item -ItemType Directory -Path (Split-Path $dest) -Force | Out-Null;Copy-Item -LiteralPath (Join-Path $r.stage $f.path) -Destination $dest -Force;if((Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant() -ne $f.sha256){throw "Copy verification failed: $($f.path)"};if($f.path -match '\.(odf|aip|spr)$'){$overlay=Join-Path "$repo\bajor\overlay" $f.path;New-Item -ItemType Directory -Path (Split-Path $overlay) -Force | Out-Null;Copy-Item -LiteralPath $dest -Destination $overlay -Force}}
if((Get-FileHash -LiteralPath D:\armadaIII\events.dat -Algorithm SHA256).Hash -ne $eventHash){throw 'Audio-event hash changed unexpectedly.'}
$result=[pscustomobject]@{part=$Part;target=$r.target;backup=$backup;files=$files;hashesVerified=$true;audioEventsPreserved=$true;runtimeVerified=$false}
$result | ConvertTo-Json -Depth 35 | Set-Content -LiteralPath "$repo\reports\bajoran-completion-$($Part.ToLowerInvariant())-apply.json" -Encoding utf8
$statusPath="$repo\status.json";$s=Get-Content -LiteralPath $statusPath -Raw | ConvertFrom-Json
if($Part -eq 'Visuals'){$s.current='Bajoran visual package installed: 53 custom faction models, normal/assimilated hull textures, matching build buttons and wireframes. DS9 and working audio patch preserved; tested simplified AI retained. File hashes verified; fresh-match visual/stability test required before full AI restoration.'}else{$s.current='Complete Bajoran AI profiles installed: all 54 roster definitions covered with economy-first opening, corrected mining freighter association and delayed Universal/advanced construction. Player options and audio patch preserved. File hashes verified; test against Bajoran AI through advanced production.'}
$s.lastCompleted=[pscustomobject]@{task='Apply Bajoran completion '+$Part;time=[DateTime]::UtcNow.ToString('o');applied=$true;runtimeVerified=$false};$s | ConvertTo-Json -Depth 60 | Set-Content -LiteralPath $statusPath -Encoding utf8;Add-Content -LiteralPath "$repo\build.log" -Value ("`n["+[DateTime]::UtcNow.ToString('o')+'] '+$s.current)
Write-Output "$Part package: $($files.Count) files installed and verified. Backup: $backup"

