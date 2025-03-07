# Note, all code to be executed on the remote server needs to belong
# in the ServerStats code block
$ServerStats = {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory)]
        [string]
        $ComputerName,

        [Parameter()]
        [pscredential]
        $Credential,

        [Parameter()]
        [bool]
        $ProcessStats=$false,

        [Parameter()]
        [double]
        $CpuUtilizationTimeout,

        [Parameter()]
        [bool]
        $CpuUtilizationOnlyValue=$false,

        [Parameter()]
        [bool]
        $NoWinRM=$false,

        [Parameter()]
        [bool]
        $Measurements=$false
    )

    $getWmiObjectParams = @{
        ComputerName  = $ComputerName
        Namespace     = "ROOT\cimv2"
        Impersonation = 3 # Impersonate. Allows objects to use the credentials of the caller.
    }

    if ($NoWinRM) {
        $getWmiObjectParams | Add-Member -NotePropertyName Credential -NotePropertyValue $Credential
    }

    # Helper Functions for aggregating process information
    $memory_used_mb = { [math]::Round(($_.WorkingSet64 / 1MB), 2) }
    $max_memory_used_mb = { [math]::Round(($_.PeakWorkingSet64 / 1MB), 2) }
    $process_alive_time = { [int] (New-TimeSpan -Start $_.StartTime -End (Get-Date)).TotalSeconds }
    $is_admin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

    $CPUInfo = Get-WmiObject Win32_Processor @getWmiObjectParams
    $OSInfo = Get-WmiObject Win32_OperatingSystem @getWmiObjectParams 

    if ($CPUInfo.count -gt 1) {
        $cpu = $CPUInfo[0]
    } else {
        $cpu = $CPUInfo
    }

    # Get Memory Information. 
    # The data will be shown in a table as MB, rounded to the nearest second decimal. 
    $OSTotalVirtualMemory = [math]::round($OSInfo.TotalVirtualMemorySize / 1MB, 2) 
    $OSTotalVisibleMemory = [math]::round(($OSInfo.TotalVisibleMemorySize / 1MB), 2) 
    $OSFreeVisibleMemory = [math]::round(($OSInfo.FreePhysicalMemory / 1MB), 2) 
    $OSUsedMemory = "{0:N2}" -f $OSTotalVisibleMemory - $OSFreeVisibleMemory
    $PhysicalMemory = Get-WmiObject CIM_PhysicalMemory @getWmiObjectParams |
    Measure-Object -Property capacity -Sum |
    ForEach-Object { [math]::round(($_.sum / 1GB), 2) } 
    $Disk = Get-WMIObject Win32_LogicalDisk @getWmiObjectParams
    $Total_FreeSpaceGB = 0
    $Total_DriveSpaceGB = 0
    ForEach ($drive in $Disk) {
        $FreeSpace = [System.Math]::Round((($drive.FreeSpace) / 1GB))
        $TotalSize = [System.Math]::Round((($drive.size) / 1GB))
        $Total_FreeSpaceGB += $FreeSpace
        $Total_DriveSpaceGB += $TotalSize
    }
    $Total_UsedDriveSpaceGB = $Total_DriveSpaceGB - $Total_FreeSpaceGB

    if ($CpuUtilizationOnlyValue) { # Get only value for CPU utilization
        function getPerf() {
            Get-WmiObject -Class Win32_PerfRawData_PerfOS_Processor @getWmiObjectParams |
            Where-Object -Property Name -eq "_Total" |
            Select-Object -Property PercentProcessorTime, TimeStamp_Sys100NS
        }
        $perf = @(getPerf)
        Start-Sleep -Seconds $CpuUtilizationTimeout
        $perf += getPerf

        $TimestampRaw = $perf[0].TimeStamp_Sys100NS
        $CPUUtilizationTimestamp = [DateTime]::FromFileTimeUtc($TimestampRaw).ToString("yyyy-MM-dd HH:mm:ss")

        $pptDiff = $perf[1].PercentProcessorTime - $perf[0].PercentProcessorTime
        $tsDiff = $perf[1].TimeStamp_Sys100NS - $perf[0].TimeStamp_Sys100NS
        $CPUUtilization = (1 - $pptDiff / $tsDiff) * 100
    } else { # Get peak and average
        if (!$NoWinRM) { # CPU utilization requires WinRM
            $counter_params = @{
                Counter        = "\Processor(_Total)\% Processor Time"
                SampleInterval = 1
                MaxSamples     = $CpuUtilizationTimeout
            }
            $CPUUtilization = (Get-Counter @counter_params |
                Select-Object -ExpandProperty countersamples |
                Select-Object -ExpandProperty CookedValue |
                Measure-Object -Average -Maximum)
        }
    }

    $process_stats = $null
    if ($ProcessStats -and !$NoWinRM) {
        # WinRM is required for process stats
        if ($is_admin) {
            # Get Information on current running processes
            # IncludeUserName means we need admin priveleges
            $process_stats = Get-Process -IncludeUserName |
            Select-Object -Property @{Name = 'user'; Expression = { $_.UserName } },
            @{Name = 'name'; Expression = { $_.ProcessName } },
            @{Name = 'path'; Expression = { $_.Path } },
            @{Name = 'pid'; Expression = { $_.Id } },
            @{Name = 'memory_used_mb'; Expression = $memory_used_mb },
            @{Name = 'max_memory_used_mb'; Expression = $max_memory_used_mb },
            @{Name = 'total_alive_time'; Expression = $process_alive_time }
        } else {
            $process_stats = Get-Process |
            Select-Object -Property @{Name = 'name'; Expression = { $_.ProcessName } },
            @{Name = 'path'; Expression = { $_.Path } },
            @{Name = 'pid'; Expression = { $_.Id } },
            @{Name = 'memory_used_mb'; Expression = $memory_used_mb },
            @{Name = 'max_memory_used_mb'; Expression = $max_memory_used_mb },
            @{Name = 'total_alive_time'; Expression = $process_alive_time }
        }
    }

    # Create an object to return, convert this to JSON or CSV as you need:

    # When running with the -Measurements flag, the output will match TMP API /measurements expected data structure
    if ($Measurements) {
        $server_info = New-Object -TypeName psobject -Property @{
            field_name         = "cpu_utilization_timeseries"
            measurable_type    = "server"
            value              = $CPUUtilization
            external_timestamp = $CPUUtilizationTimestamp
            measurable       = New-Object -TypeName psobject -Property @{
                host_name = $cpu.SystemName
            }
        }
    # When running without the -Measurements flag, the output will match 'tidal sync servers' expected data structure
    } else {
        $server_info = New-Object -TypeName psobject -Property @{
            host_name                = $cpu.SystemName
            ram_allocated_gb         = $PhysicalMemory 
            ram_used_gb              = $OSUsedMemory 
            storage_allocated_gb     = $Total_DriveSpaceGB 
            storage_used_gb          = $Total_UsedDriveSpaceGB 
            cpu_count                = $cpu.NumberOfLogicalProcessors
            operating_system         = $OSInfo.Caption 
            operating_system_version = $OSInfo.Version 
            cpu_name                 = $cpu.Name 
        }

        $custom_fields = New-Object -TypeName psobject -Property @{
            CPU_Description        = $cpu.Description 
            CPU_Manufacturer       = $cpu.Manufacturer 
            CPU_L2CacheSize        = $cpu.L2CacheSize 
            CPU_L3CacheSize        = $cpu.L3CacheSize
            CPU_SocketDesignation  = $cpu.SocketDesignation 
            TotalVisible_Memory_GB = $OSTotalVisibleMemory
            TotalVirtual_Memory_GB = $OSTotalVirtualMemory 
        }

        if ($CpuUtilizationOnlyValue) {
            $custom_fields | Add-Member -NotePropertyName cpu_utilization -NotePropertyValue $CPUUtilization
            $custom_fields | Add-Member -NotePropertyName cpu_utilization_timestamp -NotePropertyValue $CPUUtilizationTimestamp
        } else {
            if (!$NoWinRM) {
                $custom_fields | Add-Member -NotePropertyName cpu_average -NotePropertyValue $CPUUtilization.Average
                $custom_fields | Add-Member -NotePropertyName cpu_peak -NotePropertyValue $CPUUtilization.Maximum
                $custom_fields | Add-Member -NotePropertyName cpu_sampling_timeout -NotePropertyValue $CPUUtilization.Count
            }
        }

        Add-Member -InputObject $server_info -MemberType NoteProperty -Name "custom_fields" -Value $custom_fields

        if ($process_stats) {
            Add-Member -InputObject $server_info -MemberType NoteProperty -Name "process_stats" -Value $process_stats
        }
    }

    # Return the object
    $server_info
}
