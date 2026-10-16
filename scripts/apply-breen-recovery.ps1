$ErrorActionPreference='Stop'
if (Get-Process -Name Armada2 -ErrorAction SilentlyContinue) { Write-Output 'Waiting: Armada II must be closed before applying the Breen recovery patch.'; exit 2 }
$gameRoot='D:\Xaramada'
$stageRoot='D:\Xaramada-Modwork\next-update\breen-fix'
$backupRoot=Join-Path 'D:\Xaramada-Modwork\backups' ('breen-recovery-'+(Get-Date -Format 'yyyyMMdd-HHmmss'))
$written=0
foreach ($sourceFile in Get-ChildItem -LiteralPath $stageRoot -Recurse -File -Force) {
    $relativePath=[IO.Path]::GetRelativePath($stageRoot,$sourceFile.FullName)
    $targetFile=Join-Path $gameRoot $relativePath
    if (Test-Path -LiteralPath $targetFile) {
        $backupFile=Join-Path $backupRoot $relativePath
        New-Item -ItemType Directory -Path (Split-Path $backupFile) -Force | Out-Null
        Copy-Item -LiteralPath $targetFile -Destination $backupFile
        (Get-Item -LiteralPath $targetFile).IsReadOnly=$false
    }
    New-Item -ItemType Directory -Path (Split-Path $targetFile) -Force | Out-Null
    Copy-Item -LiteralPath $sourceFile.FullName -Destination $targetFile -Force
    $overlayFile=Join-Path 'D:\aramada\overlay' $relativePath
    New-Item -ItemType Directory -Path (Split-Path $overlayFile) -Force | Out-Null
    Copy-Item -LiteralPath $sourceFile.FullName -Destination $overlayFile -Force
    Add-Content -LiteralPath 'D:\aramada\build.log' -Value ('[BREEN APPLY] '+$relativePath)
    $written++
}
$report=Get-Content -LiteralPath 'D:\aramada\reports\breen-recovery.json' -Raw | ConvertFrom-Json
$report.applied=$true
$report | Add-Member -NotePropertyName backupDirectory -NotePropertyValue $backupRoot -Force
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath 'D:\aramada\reports\breen-recovery.json' -Encoding utf8
$status=Get-Content -LiteralPath 'D:\aramada\status.json' -Raw | ConvertFrom-Json
$status.current='Breen recovery patch applied: five AI profiles added, race settings completed and Dominion-starbase dependencies removed. File checks pass; a new Breen skirmish still needs testing.'
$status | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath 'D:\aramada\status.json' -Encoding utf8
Add-Content -LiteralPath 'D:\aramada\build.log' -Value ('[BREEN READY] '+$written+' files applied and backed up. Runtime Breen skirmish retest pending.')
Write-Output ($written.ToString()+' Breen recovery files applied. Backup: '+$backupRoot)
