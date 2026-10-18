$ErrorActionPreference = 'Stop'
$testRoot = 'D:\ArmadaLab'
if (!(Test-Path -LiteralPath "$testRoot\Armada2.exe")) { throw 'Separate game copy is missing' }
if (Get-Process Armada2 -ErrorAction SilentlyContinue) { throw 'An Armada game is already open' }
$previousPath = $env:PATH
$previousCompat = $env:__COMPAT_LAYER
try {
    # The old engine formats its inherited PATH into a limited startup buffer.
    # Keep this process environment small; do not change Windows/user settings.
    $env:PATH = 'C:\Windows\System32;C:\Windows;C:\Windows\System32\Wbem'
    $env:__COMPAT_LAYER = 'DWM8And16BitMitigation HIGHDPIAWARE'
    Start-Process -FilePath "$testRoot\Armada2.exe" -WorkingDirectory $testRoot
} finally {
    $env:PATH = $previousPath
    $env:__COMPAT_LAYER = $previousCompat
}
