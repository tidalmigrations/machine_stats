$cred = Get-Credential -UserName "INSERT_USERNAME" -Message "Password:"

. "./server_stats.ps1"

#####
# It's better to read in your servers from a list:
# $server_list = Get-Content "./servers.txt"

# But for initial testing, just haardcode a few:
$server_list = @("server_1", "server_2")
$server_stats = @()

$server_list | ForEach-Object {
  $server_stats += Invoke-Command -ComputerName $_ -Credential $cred -ScriptBlock $ServerStats
}

$results = @{ "servers": $server_list; }
$results | ConvertTo-Json -depth 99 | Out-File "./$date-server_stats.json" -Encoding utf8 -Force

