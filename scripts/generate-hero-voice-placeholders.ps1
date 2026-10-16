$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Speech
$voiceStage='D:\Xaramada-Modwork\bajor-rebuild\sounds\voiceover\ingame'
New-Item -ItemType Directory -Path $voiceStage -Force | Out-Null
$heroes=@{
 Kira=@{
  Select=@('Kira here.','Ready for orders.')
  Acknowledge=@('Understood.','We will take care of it.')
  Move=@('Set course.','Take us in.')
  Attack=@('Engage the enemy.','Target their weapons.')
  Stop=@('Hold position.','All stop.')
  Repair=@('Get engineering on it.','Begin repairs.')
  RedAlert=@('All hands, battle stations.')
  YellowAlert=@('Stay alert. Maintain readiness.')
  GreenAlert=@('Stand down. Resume normal operations.')
  Transport=@('Prepare the transporters.','Energize.')
  SelfDestruct=@('Evacuate the ship. Begin the self destruct sequence.')
  Decommission=@('Bring us in. This ship has served Bajor well.')
  CloakEngage=@('Activate the cloak.')
  CloakDisengage=@('Decloak. Be ready.')
 }
 Sela=@{
  Select=@('Your orders?','I am listening.')
  Acknowledge=@('As planned.','It will be done.')
  Move=@('Proceed to the coordinates.','Execute the maneuver.')
  Attack=@('Make the first strike count.','Destroy the target.')
  Stop=@('Hold our position.','Discontinue the maneuver.')
  Repair=@('Restore our systems.','Commence repairs.')
  RedAlert=@('Battle readiness. No mistakes.')
  YellowAlert=@('Remain vigilant.')
  GreenAlert=@('Return to standard readiness.')
  Transport=@('Prepare the transporters.','Transport the personnel.')
  SelfDestruct=@('There will be nothing left for the enemy. Begin self destruction.')
  Decommission=@('Return this vessel to the fleet yards.')
  CloakEngage=@('Engage the cloaking device.')
  CloakDisengage=@('Disengage the cloak. Strike swiftly.')
 }
}
$synth=New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoice('Microsoft Zira Desktop')
$format=New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(22050,[System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen,[System.Speech.AudioFormat.AudioChannel]::Mono)
$report=@()
try {
 foreach($hero in $heroes.Keys){
  $synth.Rate=$(if($hero -eq 'Sela'){-1}else{0})
  foreach($action in $heroes[$hero].Keys){
   $i=0
   foreach($line in $heroes[$hero][$action]){
    $name=('xvoice_'+$hero+'_'+$action+'_'+$i+'.wav').ToLowerInvariant()
    $dest=Join-Path $voiceStage $name
    $synth.SetOutputToWaveFile($dest,$format)
    $synth.Speak($line)
    $synth.SetOutputToNull()
    $report += [pscustomobject]@{hero=$hero;action=$action;file=$name;text=$line;voice='Microsoft Zira Desktop';synthetic=$true;actorImitation=$false}
    $i++
   }
  }
 }
} finally {$synth.Dispose()}
$report | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath 'D:\aramada\reports\synthetic-hero-voices.json' -Encoding UTF8
Write-Output "$($report.Count) original synthetic hero command clips staged. Existing game recordings retained."
