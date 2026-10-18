param([string]$GamePath,[switch]$VerifyOnly)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Windows.Forms
if(-not $GamePath){$dialog=New-Object System.Windows.Forms.FolderBrowserDialog;$dialog.Description='Select your existing Armada II installation. Use a separate copy for Armada III.';if($dialog.ShowDialog() -ne 'OK'){exit 1};$GamePath=$dialog.SelectedPath}
$GamePath=[IO.Path]::GetFullPath($GamePath)
if(-not (Test-Path -LiteralPath (Join-Path $GamePath 'Armada2.exe'))){throw 'Select an existing licensed Armada II installation containing Armada2.exe.'}
$work=Join-Path ([IO.Path]::GetTempPath()) ('A3-installer-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $work | Out-Null
Expand-Archive -LiteralPath (Join-Path $PSScriptRoot 'payload.zip') -DestinationPath $work
$manifest=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'manifest.json') -Raw | ConvertFrom-Json
foreach($file in $manifest.files){$source=Join-Path $work $file.path;if(-not (Test-Path -LiteralPath $source)){throw "Package file missing: $($file.path)"};if((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne $file.sha256){throw "Package checksum failed: $($file.path)"};$target=[IO.Path]::GetFullPath((Join-Path $GamePath $file.path));if(-not $target.StartsWith($GamePath.TrimEnd('\')+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Unsafe package path'}}
$missing=@($manifest.requiredBase | Where-Object {-not (Test-Path -LiteralPath (Join-Path $GamePath $_))})
if($missing.Count){throw "Required baseline files are absent ($($missing.Count)). This package requires the supplied Armada II baseline and its existing asset packs. First missing file: $($missing[0])"}
if($VerifyOnly){Write-Output "Verified $($manifest.files.Count) payload checksums and baseline file presence. No game files changed. Package extracted for inspection at $work";exit 0}
if(Get-Process Armada2 -ErrorAction SilentlyContinue){throw 'Close Armada II before installing.'}
if([System.Windows.Forms.MessageBox]::Show("Install Armada III beta into $GamePath ? Existing files will be backed up. This snapshot has unresolved gameplay testing; see RELEASE-NOTES.txt.",'Armada III installer','OKCancel','Information') -ne 'OK'){exit 1}
$backup=Join-Path $GamePath ('A3-Backups\'+(Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $backup -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'Rollback-ArmadaIII.ps1') -Destination $backup
$records=@()
foreach($file in $manifest.files){$target=Join-Path $GamePath $file.path;$exists=Test-Path -LiteralPath $target;if($exists){$saved=Join-Path $backup $file.path;New-Item -ItemType Directory -Path (Split-Path $saved) -Force | Out-Null;Copy-Item -LiteralPath $target -Destination $saved;$item=Get-Item -LiteralPath $target;if($item.IsReadOnly){$item.IsReadOnly=$false}};$records += [pscustomobject]@{path=$file.path;existed=$exists};$records | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $backup 'rollback.json') -Encoding UTF8;New-Item -ItemType Directory -Path (Split-Path $target) -Force | Out-Null;Copy-Item -LiteralPath (Join-Path $work $file.path) -Destination $target -Force;if((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $file.sha256){throw "Installed checksum failed: $($file.path). Backup: $backup"}}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'Rollback-ArmadaIII.ps1') -Destination $backup
$shell=New-Object -ComObject WScript.Shell;$link=$shell.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) 'Armada III.lnk'));$link.TargetPath=Join-Path $GamePath 'Armada2.exe';$link.WorkingDirectory=$GamePath;$link.Save()
[System.Windows.Forms.MessageBox]::Show("Armada III beta installed. Backup and rollback script: $backup. Start a fresh match for testing.",'Armada III') | Out-Null

