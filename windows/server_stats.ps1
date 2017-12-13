$ServerStats = {
    $CPUInfo = Get-WmiObject Win32_Processor 
    $OSInfo = Get-WmiObject Win32_OperatingSystem  

    # Get Memory Information. 
    # The data will be shown in a table as MB, rounded to the nearest second decimal. 
    $OSTotalVirtualMemory = [math]::round($OSInfo.TotalVirtualMemorySize / 1MB, 2) 
    $OSTotalVisibleMemory = [math]::round(($OSInfo.TotalVisibleMemorySize  / 1MB), 2) 
    $PhysicalMemory = Get-WmiObject CIM_PhysicalMemory | Measure-Object -Property capacity -Sum | % {[math]::round(($_.sum / 1GB),2)} 
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

    # Create an object to return, convert this to JSON or CSV as you need:
    $server_info = New-Object PSObject 
    $custom_fields = New-Object PSObject 

    Add-Member -inputObject $server_info -memberType NoteProperty -name "host_name" -value $CPUInfo.SystemName 
    Add-Member -inputObject $server_info -memberType NoteProperty -name "ram_allocated_gb" -value $OSTotalVisibleMemory
    Add-Member -inputObject $server_info -memberType NoteProperty -name "storage_allocated_gb" -value $Total_DriveSpaceGB 
    Add-Member -inputObject $server_info -memberType NoteProperty -name "storage_used_gb" -value $Total_UsedDriveSpaceGB 
    Add-Member -inputObject $server_info -memberType NoteProperty -name "cpu_count" -value $CPUInfo.NumberOfCores 
    Add-Member -inputObject $server_info -memberType NoteProperty -name "operating_system" -value $OSInfo.Caption 
    Add-Member -inputObject $server_info -memberType NoteProperty -name "operating_system_version" -value $OSInfo.Version 
    Add-Member -inputObject $server_info -memberType NoteProperty -name "cpu_name" -value $CPUInfo.Name 

    # Custom fields:
    Add-Member -inputObject $custom_fields -memberType NoteProperty -name "CPU_Description" -value $CPUInfo.Description 
    Add-Member -inputObject $custom_fields -memberType NoteProperty -name "CPU_Manufacturer" -value $CPUInfo.Manufacturer 
    Add-Member -inputObject $custom_fields -memberType NoteProperty -name "CPU_L2CacheSize" -value $CPUInfo.L2CacheSize 
    Add-Member -inputObject $custom_fields -memberType NoteProperty -name "CPU_L3CacheSize" -value $CPUInfo.L3CacheSize 
    Add-Member -inputObject $custom_fields -memberType NoteProperty -name "CPU_SocketDesignation" -value $CPUInfo.SocketDesignation 
    Add-Member -inputObject $custom_fields -memberType NoteProperty -name "TotalPhysical_Memory_GB" -value $PhysicalMemory 
    Add-Member -inputObject $custom_fields -memberType NoteProperty -name "TotalVirtual_Memory_GB" -value $OSTotalVirtualMemory 

    Add-Member -inputObject $server_info -memberType NoteProperty -name "custom_fields" -value $custom_fields 
    $server_info
}

