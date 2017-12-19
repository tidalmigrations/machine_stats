### 
# runner.ps1
#
# To use, simply:
#  1. set your USERNAME below 
#
#  2. run the save_password.ps1 script to securely store your credential in 
#     SecuredText.txt
#
#  3. Save a list of server hostnames in servers.txt
#
#  4. Run this script in a Scheduled Task
#
#
#  For questions or support, send mail to:
#
#    support@tidalmigrations.com
#
$username = "INSERT_USERNAME"

################################################################
# Do not modify below this line:
$securePwdFile = "$PWD\SecuredText.txt"

if(![System.IO.File]::Exists($securePwdFile)){
  Write-Error "$securePwdFile does not exist. Be sure to run save_password.ps1 before trying again."
  exit 1
} else {
  Write-Output "Reading credential from $securePwdFile"
} 


$secPwd = Get-Content "SecuredText.txt" | ConvertTo-SecureString
$cred = New-Object System.Management.Automation.PSCredential -ArgumentList $username, $secPwd

$env_user = Invoke-Command -ComputerName $env:COMPUTERNAME -Credential $cred -ScriptBlock { $env:USERNAME } 
Write-Output "About to execute inventory gathering as user: $env_user"


# Load the ScriptBlock $ServerStats:
. ".\server_stats.ps1"

# Get server inventory:
$server_list = Get-Content ".\servers.txt"
$num_servers = $server_list.Count
Write-Output "$num_servers Servers read from servers.txt" 


# NB: For initial testing, you may want to haardcode a few:
# $server_list = @("server_1", "server_2")

# Collected server statistics go here:
$server_stats = @()

$server_list | ForEach-Object {
  $server_stats += Invoke-Command -ComputerName $_ -Credential $cred -ScriptBlock $ServerStats
}

# Write results to file:
$results = @{ "servers" = $server_stats; }
$date = Get-Date -format yyyy_MM_dd
$results | ConvertTo-Json -depth 99 | Out-File "./$date-server_stats.json" -Encoding utf8 -Force


