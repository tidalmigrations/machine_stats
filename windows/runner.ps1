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

# NB: For initial testing, you may want to haardcode a few:
# $server_list = @($env:COMPUTERNAME, $env:COMPUTERNAME, $env:COMPUTERNAME )

$num_servers = $server_list.Count
Write-Output "$num_servers Servers read from servers.txt"

# Collected server statistics go here:
$server_stats = @()
$jobs = @()

$server_list | ForEach-Object {
  $jobs += Invoke-Command -ComputerName $_ -Credential $cred -ScriptBlock $ServerStats -AsJob
}

Do {
  $TotProgress = 0
  ForEach ($job in $jobs) {
    Try {
      $Prog = ($job | Get-Job).ChildJobs[0].Progress.StatusDescription[-1]
      If ($Prog -is [char]) {
        $Prog = 0
      }
      $TotProgress += $Prog
    }
    Catch {
      Start-Sleep -Milliseconds 500
      Break
    }
  }
  Write-Progress -Id 1 -Activity "Watching Background Jobs" -Status "Waiting for background jobs to complete: $TotProgress of $num_servers" -PercentComplete (($TotProgress / $num_servers) * 100)
  Start-Sleep -Seconds 3
} Until (($jobs | Get-Job | Where-Object {(($_.State -eq “Running”) -or ($_.state -eq “NotStarted”))}).count -eq 0)

$jobs | Receive-Job | ForEach-Object {
  $server_stats += $_
}

$num_results = $server_stats.Count
Write-Output "$num_results results received out of $num_servers servers."


# Write results to file:
$results = @{ "servers" = $server_stats; }
$date = Get-Date -format yyyy_MM_dd
$outfile = "./$date-server_stats.json"
$results | ConvertTo-Json -depth 99 | Out-File $outfile -Encoding utf8 -Force

Write-Output "Wrote to $outfile"

# Cleanup:
$jobs | Remove-Job

# Sync with Tidal:
tidal sync servers $outfile 2>&1
