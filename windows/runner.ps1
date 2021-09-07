[CmdletBinding()]
param (
    [Parameter(Mandatory)]
    [string]
    $UserName,

    [Parameter()]
    [double]
    $CpuUtilizationTimeout = 30
)
###
# runner.ps1
#
# To use, simply:
#  1. Set your username below (line 19), use a username that has login access to the hosts you are scanning.
#
#  2. Run the save_password.ps1 script to securely store your credential in
#     SecuredText.txt
#
#  3. Save a list of server hostnames in servers.txt
#
#  4. Run this script in a Scheduled Task (or invoke directly from the command line)
#
#
#  For questions or support, send mail to:
#
#    support@tidalmigrations.com
#

################################################################
# Do not modify below this line:
$securePwdFile = Join-Path -Path $PWD -ChildPath "SecuredText.txt"

if(![System.IO.File]::Exists($securePwdFile)){
  Write-Error "$securePwdFile does not exist. Be sure to run save_password.ps1 before trying again."
  exit 1
} else {
  Write-Host "Reading credential from $securePwdFile"
}


$secPwd = Get-Content "SecuredText.txt" | ConvertTo-SecureString
$cred = New-Object System.Management.Automation.PSCredential -ArgumentList $UserName, $secPwd

$env_user = Invoke-Command -ComputerName ([Environment]::MachineName) -Credential $cred -ScriptBlock { $env:USERNAME }
Write-Host "About to execute inventory gathering as user: $env_user"

$ServerStats = {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory)]
        [string]
        $ComputerName,

        [Parameter(Mandatory)]
        [pscredential]
        $Credential,

        [Parameter(Mandatory)]
        [double]
        $CpuUtilizationTimeout
    )
    $getWmiObjectParams = @{
        ComputerName = $ComputerName
        Credential = $Credential
        Namespace = "ROOT\cimv2"
        Impersonation = 3 # Impersonate. Allows objects to use the credentials of the caller.
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
    $cpu_count = (Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors

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
        cpu_utilization = @{
            value = $cpu_utilization
            timeout = $CpuUtilizationTimeout
        }
    }

    Add-Member -InputObject $server_info -MemberType NoteProperty -name "custom_fields" -value $custom_fields 
    $server_info
}

# Get server inventory:
$server_list = Get-Content ".\servers.txt"

$num_servers = $server_list.Count
Write-Host "$num_servers Servers read from servers.txt"

# Collected server statistics go here:
$server_stats = @()
$jobs = @()

$server_list | ForEach-Object {
  $jobs += Start-Job -ScriptBlock $ServerStats -ArgumentList $_, $cred, $CpuUtilizationTimeout
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
} Until (($jobs | Get-Job | Where-Object {(($_.State -eq "Running") -or ($_.state -eq "NotStarted"))}).count -eq 0)

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
