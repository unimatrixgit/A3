param([string]$Source='D:\armadaIII',[string]$Output='D:\A3-Releases\2026-10-19')
$ErrorActionPreference='Stop'
$payload=Join-Path $Output 'payload'
New-Item -ItemType Directory -Path $payload -Force | Out-Null
$files=@();$required=@()
$folders=@('AI','odf','misc','Sprites','techtree','missions','objectives','SOD','Textures','sounds','bzn','bitmaps','animations','cursors')
$configExtensions=@('.odf','.aip','.h','.cfg','.spr','.tt','.dat','.set','.lua','.txt')
foreach($folder in $folders){$dir=Join-Path $Source $folder;if(-not(Test-Path -LiteralPath $dir)){continue};foreach($file in Get-ChildItem -LiteralPath $dir -File -Recurse){$relative=$file.FullName.Substring($Source.Length+1);if($file.Extension.ToLowerInvariant() -in $configExtensions){$dest=Join-Path $payload $relative;New-Item -ItemType Directory -Path (Split-Path $dest) -Force | Out-Null;Copy-Item -LiteralPath $file.FullName -Destination $dest;$files += [pscustomobject]@{path=$relative;size=$file.Length;sha256=(Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash}}elseif($file.Extension -match '^\.(sod|tga|wav|mp3|bmp|bzn|png|jpg|dds|ani|cur)$'){$required += $relative}}}
foreach($name in @('ART_CFG.h','RTS_CFG.h','game_cfg.h','events.dat','Dynamic_Localized_Strings.h','label.map','mshell.set','Input.map')){$f=Join-Path $Source $name;if(Test-Path -LiteralPath $f){Copy-Item -LiteralPath $f -Destination (Join-Path $payload $name);$files += [pscustomobject]@{path=$name;size=(Get-Item -LiteralPath $f).Length;sha256=(Get-FileHash -LiteralPath $f -Algorithm SHA256).Hash}}}
[pscustomobject]@{name='Armada III configuration update';version='0.1.0-beta.20261019';files=$files;requiredBase=$required;runtimeVerified=$false} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $Output 'manifest.json') -Encoding UTF8
foreach($name in @('Install-ArmadaIII.ps1','Rollback-ArmadaIII.ps1','Setup.cmd')){Copy-Item -LiteralPath (Join-Path $PSScriptRoot $name) -Destination (Join-Path $Output $name)}
@'
ARMADA III CONFIGURATION UPDATE 0.1.0-beta.20261019

Requires an existing compatible Armada III asset installation and a licensed Armada II executable. This update is not a standalone game or a stock-only Armada II conversion. Retail executables and third-party binary models, textures, maps and recordings are not included.

Extract the installer ZIP into its own folder and run Setup.cmd. Select the existing game folder. Close the game first. The installer checks payload hashes and required asset presence, backs up overwritten files, and creates a desktop shortcut. Asset presence checks do not establish compatible asset versions.

Rollback: run Rollback-ArmadaIII.ps1 from the timestamped A3-Backups folder inside the selected game folder. Existing saves may retain old definitions; start a new match.

BETA: current installed Armada III configuration snapshot, not the quarantined ArmadaLab experiments. Recent crash-recovery and new-content gameplay checks remain pending. No claim of full gameplay verification or complete TV/movie ship coverage is made.

Source, asset dependencies and credits: https://www.dunerealms.com/git/unimatrix/A3
'@ | Set-Content -LiteralPath (Join-Path $Output 'RELEASE-NOTES.txt') -Encoding UTF8
& 'C:\Program Files\7-Zip\7z.exe' a -tzip -mx=5 (Join-Path $Output 'payload.zip') (Join-Path $payload '*') -bso0 -bsp0
if($LASTEXITCODE -ne 0){throw 'Payload compression failed'}
$package=Join-Path $Output 'ArmadaIII-Update-0.1.0-beta.20261019.zip'
$items=@('payload.zip','manifest.json','Install-ArmadaIII.ps1','Rollback-ArmadaIII.ps1','Setup.cmd','RELEASE-NOTES.txt') | ForEach-Object {Join-Path $Output $_}
& 'C:\Program Files\7-Zip\7z.exe' a -tzip -mx=5 $package @items -bso0 -bsp0
if($LASTEXITCODE -ne 0){throw 'Installer compression failed'}
$hash=(Get-FileHash -LiteralPath $package -Algorithm SHA256).Hash
"$hash  $(Split-Path $package -Leaf)" | Set-Content -LiteralPath (Join-Path $Output 'SHA256SUMS.txt') -Encoding ASCII
Write-Output "Built $package; $($files.Count) configuration files; $($required.Count) required asset paths. SHA256: $hash"
