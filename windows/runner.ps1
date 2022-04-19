<#
.SYNOPSIS

Gathers machine statistics (RAM, storage, CPU, etc) from a server environment.

.DESCRIPTION

The runner.ps1 script gathers machine statistics from a server environment.

.PARAMETER UserName

Specifies the user name used for connection to the remote machine.
To securely provide a password, please run the save_password.ps1 script.

.PARAMETER ServersPath

Specifies the path to file with the list of servers (one server per line).
By default it looks for servers.txt in the current directory.

.PARAMETER NoWinRM

Specifies if WinRM should not be used.

.PARAMETER ProcessStats

Specifies if capturing process metrics should be enabled (WinRM only).

.PARAMETER CpuUtilizationTimeout

Specifies the number of seconds to measure CPU utilization.
The default value is 30.

.PARAMETER CpuUtilizationOnlyValue

Capture point-in-time CPU utilization value rather than a peak and average over a given time.

.INPUTS

None. You cannot pipe objects to runner.ps1

.OUTPUTS

runner.ps1 generates a JSON output with all the gathered data suitable to be
used with Tidal Tools or Tidal Migrations API.

.EXAMPLE

.\runner.ps1

.EXAMPLE

.\runner.ps1 -UserName myuser

#>
[CmdletBinding()]
param (
    [Parameter(Mandatory)]
    [string]
    $UserName,

    [Parameter()]
    [string]
    $ServersPath = (Join-Path -Path $PWD -ChildPath "servers.txt"),

    [Parameter()]
    [string]
    $SecurePwdFilePath = (Join-Path -Path $PWD -ChildPath "SecuredText.txt"),

    [Parameter()]
    [string]
    $ServerStatsPath = (Join-Path -Path $PWD -ChildPath "server_stats.ps1"),

    [Parameter()]
    [switch]
    $NoWinRM,

    [Parameter()]
    [switch]
    $ProcessStats,

    [Parameter()]
    [double]
    $CpuUtilizationTimeout = 30,

    [Parameter()]
    [switch]
    $CpuUtilizationOnlyValue
)

if (![System.IO.File]::Exists($SecurePwdFilePath)) {
    Write-Error "$SecurePwdFilePath does not exist. Be sure to run save_password.ps1 before trying again."
    exit 1
} else {
    Write-Host "Reading credential from $SecurePwdFilePath"
}

$secPwd = Get-Content $SecurePwdFilePath | ConvertTo-SecureString
$cred = New-Object System.Management.Automation.PSCredential -ArgumentList $UserName, $secPwd

$env_user = Invoke-Command -ComputerName ([Environment]::MachineName) -Credential $cred -ScriptBlock { $env:USERNAME }
Write-Host "About to execute inventory gathering as user: $env_user"

# Load the ScriptBlock $ServerStats:
. $ServerStatsPath

# Get server inventory:
$server_list = Get-Content $ServersPath

$num_servers = $server_list.Count
$ServersBaseName = Get-ChildItem -Path $ServersPath | Select-Object -ExpandProperty BaseName
Write-Host "$num_servers Servers read from $ServersBaseName"

# Collected server statistics go here:
$server_stats = @()
$jobs = @()

$server_list | ForEach-Object {
    if ($NoWinRM) {
        $startJobParams = @{
            ScriptBlock  = $ServerStats
            ArgumentList = $_, $cred, $ProcessStats, $CpuUtilizationTimeout, $CpuUtilizationOnlyValue, $NoWinRM
        }
        $jobs += Start-Job @startJobParams
    } else {
        $invokeCommandParams = @{
            ComputerName = $_
            Credential   = $cred
            ScriptBlock  = $ServerStats
            ArgumentList = "localhost", $null, $ProcessStats, $CpuUtilizationTimeout, $CpuUtilizationOnlyValue, $NoWinRM
        }
        $jobs += Invoke-Command @invokeCommandParams -AsJob
    }
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
        } Catch {
            Start-Sleep -Milliseconds 500
            Break
        }
    }
    Write-Progress -Id 1 -Activity "Watching Background Jobs" -Status "Waiting for background jobs to complete: $TotProgress of $num_servers" -PercentComplete (($TotProgress / $num_servers) * 100)
    Start-Sleep -Seconds 3
} Until (($jobs | Get-Job | Where-Object { (($_.State -eq "Running") -or ($_.state -eq "NotStarted")) }).count -eq 0)

$jobs | Receive-Job | ForEach-Object {
    $server_stats += $_
}

$num_results = $server_stats.Count
Write-Host "$num_results results received out of $num_servers servers."

# Output results
$results = @{ servers = $server_stats }
$json = $results | ConvertTo-Json -Depth 99
Write-Output $json

# Cleanup:
$jobs | Remove-Job
