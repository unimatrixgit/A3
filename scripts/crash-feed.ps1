$ErrorActionPreference='Continue'
while ($true) {
  try {
    $events=@(Get-WinEvent -FilterHashtable @{LogName='Application';Id=1000,1001;StartTime=(Get-Date).AddDays(-7)} -ErrorAction SilentlyContinue | Where-Object {$_.Message -match '(?i)armada2?\.exe|D:\\Xaramada|D:\\armadaIII'} | Select-Object -First 25 | ForEach-Object {[pscustomobject]@{time=$_.TimeCreated.ToString('o');source='Windows Application';id=$_.Id;message=$_.Message}})
    $logs=@(foreach($root in @('D:\Xaramada','D:\armadaIII')) {Get-ChildItem -LiteralPath $root -File -ErrorAction SilentlyContinue | Where-Object {$_.Name -match '(?i)\.(log|dmp|mdmp)$|error.*\.txt$|crash.*\.txt$'} | ForEach-Object { [pscustomobject]@{path=$_.FullName;modified=$_.LastWriteTime.ToString('o');text=$(if($_.Extension -match '(?i)dmp'){'Binary crash dump available'}else{(Get-Content -LiteralPath $_.FullName -Tail 60 -ErrorAction SilentlyContinue) -join "`n"})}}})
    $data=[pscustomobject]@{updated=(Get-Date).ToString('o');events=$events;files=$logs;note='Windows crash reports refresh every 10 seconds. No new report does not prove the game loaded successfully.'}
    $json=$data | ConvertTo-Json -Depth 8
    [IO.File]::WriteAllText('D:\aramada\crash-logs\latest.json',$json,[Text.UTF8Encoding]::new($false))
    [IO.File]::WriteAllText('D:\aramada\crashes.json',$json,[Text.UTF8Encoding]::new($false))
  } catch { Add-Content -LiteralPath 'D:\aramada\build.log' -Value "Crash feed read error: $_" }
  Start-Sleep -Seconds 10
}
