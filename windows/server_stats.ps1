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
    ForEach ($drive in $disk) {
      $FreeSpace = [System.Math]::Round((($drive.FreeSpace) / 1GB))
      $TotalSize = [System.Math]::Round((($drive.size) / 1GB))
      $Total_FreeSpaceGB += $FreeSpace
      $Total_DriveSpaceGB += $TotalSize
    }

    # Create an object to return, convert this to JSON or CSV as you need:
    $infoObject = New-Object PSObject 

    Add-Member -inputObject $infoObject -memberType NoteProperty -name "ServerName" -value $CPUInfo.SystemName 
    Add-Member -inputObject $infoObject -memberType NoteProperty -name "CPU_Name" -value $CPUInfo.Name 
    Add-Member -inputObject $infoObject -memberType NoteProperty -name "CPU_Description" -value $CPUInfo.Description 
    Add-Member -inputObject $infoObject -memberType NoteProperty -name "CPU_Manufacturer" -value $CPUInfo.Manufacturer 
    Add-Member -inputObject $infoObject -memberType NoteProperty -name "CPU_NumberOfCores" -value $CPUInfo.NumberOfCores 
    Add-Member -inputObject $infoObject -memberType NoteProperty -name "CPU_L2CacheSize" -value $CPUInfo.L2CacheSize 
    Add-Member -inputObject $infoObject -memberType NoteProperty -name "CPU_L3CacheSize" -value $CPUInfo.L3CacheSize 
    Add-Member -inputObject $infoObject -memberType NoteProperty -name "CPU_SocketDesignation" -value $CPUInfo.SocketDesignation 
    Add-Member -inputObject $infoObject -memberType NoteProperty -name "OS_Name" -value $OSInfo.Caption 
    Add-Member -inputObject $infoObject -memberType NoteProperty -name "OS_Version" -value $OSInfo.Version 
    Add-Member -inputObject $infoObject -memberType NoteProperty -name "TotalPhysical_Memory_GB" -value $PhysicalMemory 
    Add-Member -inputObject $infoObject -memberType NoteProperty -name "TotalVirtual_Memory_GB" -value $OSTotalVirtualMemory 
    Add-Member -inputObject $infoObject -memberType NoteProperty -name "TotalVisable_Memory_GB" -value $OSTotalVisibleMemory
    Add-Member -inputObject $infoObject -memberType NoteProperty -name "TotalDiskSpace_Free_GB" -value $Total_FreeSpaceGB 
    Add-Member -inputObject $infoObject -memberType NoteProperty -name "TotalDiskSpace_Allocated_GB" -value $Total_DriveSpaceGB 
    $infoObject
}

