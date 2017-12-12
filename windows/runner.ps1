$cred = Get-Credential -UserName "INSERT_USERNAME" -Message "Password:"

. "$PSScriptRoot\server_stats.ps1"

$server_list = @("server_1", "server_2")
$results = @()

$server_list | ForEach-Object {
  $results += ServerStats($_, $cred) 
}

$results | ConvertTo-Json -depth 99 | Out-File "$PSScriptRoot\$date-server_stats.json" -Encoding utf8 -Force

