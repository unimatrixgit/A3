$ErrorActionPreference='Stop'
if(Get-Process Armada2 -ErrorAction SilentlyContinue){throw 'Close the game before rollback.'}
$root=Split-Path (Split-Path $PSScriptRoot)
foreach($file in (Get-Content (Join-Path $PSScriptRoot 'rollback.json') -Raw | ConvertFrom-Json)){$target=[IO.Path]::GetFullPath((Join-Path $root $file.path));if(-not $target.StartsWith($root.TrimEnd('\')+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Unsafe rollback path'};if($file.existed){Copy-Item -LiteralPath (Join-Path $PSScriptRoot $file.path) -Destination $target -Force}else{if(Test-Path -LiteralPath $target){Remove-Item -LiteralPath $target}}}
Write-Output 'Backed-up files restored. Restart the game.'
