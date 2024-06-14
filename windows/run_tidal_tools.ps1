# Sample wrapper for gathering machine statistics (RAM, storage, CPU, etc)
# and sending them to the Tidal Accelerator Platform
c:\machine_stats\windows\runner.ps1 `
-UserName Administrator `
-ServersPath "c:\machine_stats\windows\servers.txt" `
-ServerStatsPath "c:\machine_stats\windows\server_stats.ps1" `
-SecurePwdFilePath "c:\machine_stats\windows\SecuredText.txt" `
| tidal sync servers
