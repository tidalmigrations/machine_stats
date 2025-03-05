C:\machine_stats\windows\runner.ps1 `
-UserName Administrator `
-ServersPath "C:\machine_stats\windows\servers.txt" `
-ServerStatsPath "C:\machine_stats\windows\server_stats.ps1" `
-SecurePwdFilePath "C:\machine_stats\windows\SecuredText.txt" `
-CpuUtilizationTimeout 1 `
-CpuUtilizationOnlyValue `
-Measurements `
| tidal request -X POST /api/v1/measurements/import
