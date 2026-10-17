function Get-DiagnosticHash($path){$stream=[IO.File]::OpenRead($path);$sha=[Security.Cryptography.SHA256]::Create();try{[BitConverter]::ToString($sha.ComputeHash($stream)).Replace("-","")}finally{$stream.Dispose();$sha.Dispose()}}
$ErrorActionPreference='Continue'
$diagnosticRoot='D:\Xaramada-Modwork\diagnostics'
$repo='D:\aramada'
$tool='D:\Xaramada-Modwork\tools\procdump\procdump.exe'
New-Item -ItemType Directory -Path $diagnosticRoot -Force|Out-Null
$mutex=New-Object Threading.Mutex($false,'Local\ArmadaIIICrashDiagnostics')
if(!$mutex.WaitOne(0)){exit}
function Write-Diagnostic($message){$line='['+[DateTime]::UtcNow.ToString('o')+'] '+$message;Add-Content -LiteralPath (Join-Path $diagnosticRoot 'monitor.log') -Value $line;Add-Content -LiteralPath "$repo\build.log" -Value $line}
Write-Diagnostic 'Crash capture armed for D:\armadaIII\Armada2.exe only. Session logs and full crash dumps are local; no game launched.'
$lastKey=''
while($true){
 try{
  $game=Get-Process Armada2 -ErrorAction SilentlyContinue|Where-Object {$_.Path -eq 'D:\armadaIII\Armada2.exe'}|Select-Object -First 1
  if(!$game){Start-Sleep -Milliseconds 500;continue}
  $key=[string]$game.Id+'-'+$game.StartTime.ToUniversalTime().Ticks
  if($key -eq $lastKey){Start-Sleep -Seconds 1;continue}
  $lastKey=$key;$stamp=Get-Date -Format 'yyyyMMdd-HHmmss';$session=Join-Path $diagnosticRoot ('session-'+$stamp+'-'+$game.Id);New-Item -ItemType Directory -Path $session -Force|Out-Null
  $started=Get-Date;$capture=$null
  $record=[ordered]@{started=$started.ToString('o');pid=$game.Id;image=$game.Path;session=$session;captureArmed=$false;memoryDumpCreated=$false;scope='Process/session/exception capture; does not record individual in-game build commands.'}
  $protectedFiles=@(Get-ChildItem D:\armadaIII\odf -Recurse -File|Where-Object {$_.BaseName -match '^(bj|xbjuconst)'})+@(Get-Item D:\armadaIII\events.dat,D:\armadaIII\techtree\tech1.tt)
  $hashes=@($protectedFiles|ForEach-Object{[pscustomobject]@{path=$_.FullName;sha256=(Get-DiagnosticHash $_.FullName)}})
  $hashes|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $session 'active-files.json') -Encoding utf8
  Copy-Item -LiteralPath "$repo\status.json" -Destination (Join-Path $session 'patch-status.json') -ErrorAction SilentlyContinue
  $dumpCount=@(Get-ChildItem -LiteralPath $diagnosticRoot -Filter '*.dmp' -Recurse -File -ErrorAction SilentlyContinue).Count
  $drive=Get-PSDrive -Name D
  if($dumpCount -lt 6 -and $drive.Free -gt 4GB){
   $arguments=@('-accepteula','-ma','-e','-n','1',[string]$game.Id,$session)
   $capture=Start-Process -FilePath $tool -ArgumentList $arguments -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $session 'procdump.log') -RedirectStandardError (Join-Path $session 'procdump-error.log')
   $record.captureArmed=$true;$record.capturePid=$capture.Id
   Write-Diagnostic "Crash capture attached to Armada III PID $($game.Id). Session: $session"
  }else{Write-Diagnostic "Session logging only: dump limit reached or less than 4 GB free. Session: $session"}
  $record|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $session 'session.json') -Encoding utf8
  while($true){$current=Get-Process -Id $game.Id -ErrorAction SilentlyContinue;if(!$current -or $current.Path -ne 'D:\armadaIII\Armada2.exe'){break};$sample=[pscustomobject]@{time=[DateTime]::UtcNow.ToString('o');pid=$current.Id;workingSet=$current.WorkingSet64;privateMemory=$current.PrivateMemorySize64;virtualMemory=$current.VirtualMemorySize64;threads=$current.Threads.Count;handles=$current.HandleCount;cpuSeconds=$current.CPU};Add-Content -LiteralPath (Join-Path $session 'process.jsonl') -Value ($sample|ConvertTo-Json -Compress);Start-Sleep -Seconds 2}
  Start-Sleep -Seconds 2
  $record.ended=[DateTime]::UtcNow.ToString('o');$record.memoryDumpCreated=@(Get-ChildItem -LiteralPath $session -Filter '*.dmp' -File).Count -gt 0
  $record.dumpFiles=@(Get-ChildItem -LiteralPath $session -Filter '*.dmp' -File|ForEach-Object{[pscustomobject]@{path=$_.FullName;bytes=$_.Length}})
  $events=@(Get-WinEvent -FilterHashtable @{LogName='Application';Id=1000,1001;StartTime=$started} -ErrorAction SilentlyContinue|Where-Object {$_.Message -match 'Armada2.exe'}|ForEach-Object{[pscustomobject]@{time=$_.TimeCreated.ToString('o');id=$_.Id;message=$_.Message}})
  $events|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $session 'windows-events.json') -Encoding utf8
  $record|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $session 'session.json') -Encoding utf8
  $record|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $diagnosticRoot 'latest-session.json') -Encoding utf8
  Write-Diagnostic "Armada III session ended. Dump created: $($record.memoryDumpCreated). Windows crash events: $($events.Count). Details: $session"
 }catch{Write-Diagnostic ('Capture error: '+$_)}
 Start-Sleep -Seconds 1
}


