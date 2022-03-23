# MS4W CPU Limitation Testing

$start = (Get-Date -format "hh-mm-ss").ToString()
$response = C:\machine_stats\windows\runner.ps1 -UserName Administrator -CpuUtilizationTimeout 1 -CpuUtilizationOnlyValue
$end = (Get-Date -format "hh-mm-ss").ToString()

$response | Out-File ("C:\Machine_stats\windows\result" + $start + "--" + $end + ".json")
