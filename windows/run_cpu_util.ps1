# Sample wrapper for capturing time-series CPU utilization data
# and sending it to the Tidal Accelerator Platform
c:\machine_stats\windows\runner.ps1 `
-UserName Administrator `
-ServersPath "c:\machine_stats\windows\servers.txt" `
-ServerStatsPath "c:\machine_stats\windows\server_stats.ps1" `
-SecurePwdFilePath "c:\machine_stats\windows\SecuredText.txt" `
-CpuUtilizationTimeout 1 `
-CpuUtilizationOnlyValue `
-Measurements `
| tidal request -X POST /api/v1/measurements/import
