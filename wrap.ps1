$machineStatsPath = ''
$measurementsPath  = ''
$userName = ''
$CpuUtilizationTimeout = 240

cd $machineStatsPath
& ("$machineStatsPath\runner.ps1") -UserName $userName -CpuUtilizationTimeout $CpuUtilizationTimeout > "$measurementsPath/stats.json"
cd $measurementsPath
& python "$measurementsPath\script.py"
