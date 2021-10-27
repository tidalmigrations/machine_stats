# Note, all code to be executed on the remote server needs to belong
# in the ServerStats code block
$ServerStats = {
    # Helper Functions for aggregating process information
    $memory_used_mb = {[math]::Round(($_.WorkingSet64 / 1MB), 2)};
    $max_memory_used_mb = {[math]::Round(($_.PeakWorkingSet64 / 1MB), 2)};
    $process_alive_time = {[math]::Round((New-TimeSpan -Start $_.StartTime -End (Get-Date)).TotalSeconds)}
    $is_admin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

    $CPUInfo = Get-WmiObject Win32_Processor 
    $OSInfo = Get-WmiObject Win32_OperatingSystem  

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
    $PhysicalMemory = Get-WmiObject CIM_PhysicalMemory |
        Measure-Object -Property capacity -Sum |
            ForEach-Object { [math]::round(($_.sum / 1GB), 2) } 
    $Disk = Get-WMIObject Win32_LogicalDisk
    $Total_FreeSpaceGB = 0
    $Total_DriveSpaceGB = 0
    ForEach ($drive in $Disk) {
        $FreeSpace = [System.Math]::Round((($drive.FreeSpace) / 1GB))
        $TotalSize = [System.Math]::Round((($drive.size) / 1GB))
        $Total_FreeSpaceGB += $FreeSpace
        $Total_DriveSpaceGB += $TotalSize
    }
    $Total_UsedDriveSpaceGB = $Total_DriveSpaceGB - $Total_FreeSpaceGB

    $counter_params = @{
        Counter = "\Processor(_Total)\% Processor Time"
        SampleInterval = 1
        MaxSamples = 30
    }
    $CPUUtilization = (Get-Counter @counter_params |
        Select-Object -ExpandProperty countersamples |
            Select-Object -ExpandProperty CookedValue |
                Measure-Object -Average -Maximum)

    # if ($is_admin){
    # # Get Information on current running processes
    # # IncludeUserName means we need admin priveleges
    #   $process_stats = Get-Process -IncludeUserName |
    #     Select-Object -Property @{Name=’user’; Expression={$_.UserName}},
    #                             @{Name=’name’; Expression={$_.ProcessName}},
    #                             @{Name=’path’; Expression={$_.Path}},
    #                             @{Name=’pid’; Expression={$_.Id}},
    #                             @{Name=’memory_used_mb’; Expression=$memory_used_mb},
    #                             @{Name=’max_memory_used_mb’; Expression=$max_memory_used_mb},
    #                             @{Name=’total_alive_time’; Expression=$process_alive_time}
    # } else {
    #     $process_stats = Get-Process |
    #       Select-Object -Property @{Name=’name’; Expression={$_.ProcessName}},
    #                               @{Name=’path’; Expression={$_.Path}},
    #                               @{Name=’pid’; Expression={$_.Id}},
    #                               @{Name=’memory_used_mb’; Expression=$memory_used_mb},
    #                               @{Name=’max_memory_used_mb’; Expression=$max_memory_used_mb},
    #                               @{Name=’total_alive_time’; Expression=$process_alive_time}
    # }

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
        cpu_average = $CPUUtilization.Average
        cpu_peak = $CPUUtilization.Maximum
        cpu_sampling_timeout = $CPUUtilization.Count
    }

    Add-Member -InputObject $server_info -MemberType NoteProperty -name "custom_fields" -value $custom_fields
    # Add-Member -InputObject $server_info -MemberType NoteProperty -name "process_stats" -value $process_stats
    $server_info
}
