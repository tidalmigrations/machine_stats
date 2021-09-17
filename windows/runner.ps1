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

.PARAMETER CpuUtilizationTimeout
Specifies the number of seconds to measure CPU utilization.
The default value is 30.

.PARAMETER WinRM
Specifies if WinRM should be used.

.INPUTS

None. You cannot pipe objects to runner.ps1

.OUTPUTS

runner.ps1 generates a JSON output with all the gathered data suitable to be
used with Tidal Tools or Tidal Migrations API.

.EXAMPLE

.\runner.ps1

.EXAMPLE

.\runner.ps1 -UserName myuser

.EXAMPLE

.\runner.ps1 -CpuUtilizationTimeout 20
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
    [double]
    $CpuUtilizationTimeout = 30,

    [Parameter()]
    [switch]
    $WinRM
)

$securePwdFile = Join-Path -Path $PWD -ChildPath "SecuredText.txt"

if(![System.IO.File]::Exists($securePwdFile)){
    Write-Error "$securePwdFile does not exist. Be sure to run save_password.ps1 before trying again."
    exit 1
}
Write-Host "Reading credential from $securePwdFile"

$secPwd = Get-Content $securePwdFile | ConvertTo-SecureString
$cred = New-Object System.Management.Automation.PSCredential ($UserName, $secPwd)

$ServerStats = {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory)]
        [string]
        $ComputerName,

        [Parameter()]
        [pscredential]
        $Credential,

        [Parameter(Mandatory)]
        [double]
        $CpuUtilizationTimeout
    )
    $getWmiObjectParams = @{
        ComputerName = $ComputerName
        Namespace = "ROOT\cimv2"
        Impersonation = 3 # Impersonate. Allows objects to use the credentials of the caller.
    }
    $remote = $ComputerName -notin ".", "localhost", ([Environment]::MachineName)
    if ($remote) {
        $getWmiObjectParams | Add-Member -NotePropertyName Credential -NotePropertyValue $Credential
    }
    $CPUInfo = Get-WmiObject Win32_Processor @getWmiObjectParams
    $OSInfo = Get-WmiObject Win32_OperatingSystem @getWmiObjectParams 

    $PhysicalMemory = Get-WmiObject CIM_PhysicalMemory @getWmiObjectParams |
        Measure-Object -Property capacity -Sum |
            ForEach-Object { [math]::round(($_.sum / 1GB), 2) } 
    $Disk = Get-WmiObject Win32_LogicalDisk @getWmiObjectParams

    if ($CPUInfo.count -gt 1) {
        $cpu = $CPUInfo[0]
    } else {
        $cpu = $CPUInfo
    }
    $cpu_count = Get-WmiObject Win32_Processor @getWmiObjectParams |
        Measure-Object -Property NumberOfCores -Sum |
            Select-Object -ExpandProperty Sum
    # Get Memory Information. 
    # The data will be shown in a table as MB, rounded to the nearest second decimal. 
    $OSTotalVirtualMemory = [math]::round($OSInfo.TotalVirtualMemorySize / 1MB, 2) 
    $OSTotalVisibleMemory = [math]::round(($OSInfo.TotalVisibleMemorySize  / 1MB), 2) 
    $OSFreeVisibleMemory = [math]::round(($OSInfo.FreePhysicalMemory  / 1MB), 2) 
    $OSUsedMemory = "{0:N2}" -f $OSTotalVisibleMemory - $OSFreeVisibleMemory
    $Total_FreeSpaceGB = 0
    $Total_DriveSpaceGB = 0
    ForEach ($drive in $Disk) {
        $FreeSpace = [System.Math]::Round((($drive.FreeSpace) / 1GB))
        $TotalSize = [System.Math]::Round((($drive.size) / 1GB))
        $Total_FreeSpaceGB += $FreeSpace
        $Total_DriveSpaceGB += $TotalSize
    }
    $Total_UsedDriveSpaceGB = $Total_DriveSpaceGB - $Total_FreeSpaceGB

    # CPU utilization
    function getPerf() {
        Get-WmiObject -Class Win32_PerfRawData_PerfOS_Processor @getWmiObjectParams |
            Where-Object -Property Name -eq "_Total" |
                Select-Object -Property PercentProcessorTime, TimeStamp_Sys100NS
    }
    $perf = @(getPerf)
    Start-Sleep -Seconds $CpuUtilizationTimeout
    $perf += getPerf

    $pptDiff = $perf[1].PercentProcessorTime - $perf[0].PercentProcessorTime
    $tsDiff = $perf[1].TimeStamp_Sys100NS - $perf[0].TimeStamp_Sys100NS
    $cpu_utilization = (1 - $pptDiff / $tsDiff) * 100

    # Create an object to return, convert this to JSON or CSV as you need:
    $server_info = New-Object -TypeName psobject -Property @{
        host_name = $cpu.SystemName
        ram_allocated_gb = $PhysicalMemory 
        ram_used_gb = $OSUsedMemory 
        storage_allocated_gb = $Total_DriveSpaceGB 
        storage_used_gb = $Total_UsedDriveSpaceGB 
        cpu_count = $cpu_count
        operating_system = $OSInfo.Caption 
        operating_system_version = $OSInfo.Version 
        cpu_name = $cpu.Name 
    } 
    $custom_fields = New-Object -TypeName psobject -Property @{
        CPU_Description = $cpu.Description 
        CPU_Manufacturer = $cpu.Manufacturer 
        CPU_L2CacheSize = $cpu.L2CacheSize 
        CPU_L3CacheSize = $cpu.L3CacheSize 
        CPU_SocketDesignation = $cpu.SocketDesignation 
        TotalVisible_Memory_GB = $OSTotalVisibleMemory
        TotalVirtual_Memory_GB = $OSTotalVirtualMemory 
        cpu_utilization = $cpu_utilization
        cpu_utilization_timeout = $CpuUtilizationTimeout
    }

    Add-Member -InputObject $server_info -MemberType NoteProperty -name "custom_fields" -value $custom_fields 
    $server_info
}

# Get server inventory:
$server_list = Get-Content $ServersPath

$num_servers = $server_list.Count
Write-Host "$num_servers Servers read from servers.txt"

# Collected server statistics go here:
$server_stats = @()
$jobs = @()

$server_list | ForEach-Object {
    if ($WinRM -eq $false) {
        $startJobParams = @{
            ScriptBlock = $ServerStats
            ArgumentList = $_, $cred, $CpuUtilizationTimeout
        }
        $jobs += Start-Job @startJobParams
    } else {
        $invokeCommandParams = @{
            ComputerName = $_
            Credential = $cred
            ScriptBlock = $ServerStats
            ArgumentList = "localhost", $null, $CpuUtilizationTimeout
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
        }
        Catch {
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
$json = $results | ConvertTo-Json -depth 99
Write-Output $json

# Cleanup:
$jobs | Remove-Job
