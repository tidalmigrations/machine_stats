# Machine Stats for Windows

Machine Stats for Windows uses WinRM to `Invoke-Command` across your servers, creating a JSON file to securely send to your [Tidal Migrations](https://tidalmigrations.com/) instance using the [tidal command](https://tidalmigrations.com/tidal-tools/).

The script `runner.ps1` should be customized for each network that you will be scanning.

1) Specify your username (step 1) and a list of hostnames (step 3).

2) If you plan on running this in a scheduled task, you may want to store your credential with the `PsCredential` method. See [this blog post](https://www.interworks.com/blog/trhymer/2013/07/08/powershell-how-encrypt-and-store-credentials-securely-use-automation-scripts) for an example.

> _NB: You do need WinRM enabled across your environment for this._
> _For a simple guide to do this via GPO, see [here](https://support.auvik.com/hc/en-us/articles/204424994-How-to-enable-WinRM-with-domain-controller-Group-Policy-for-WMI-monitoring)._

As of Windows 2008 Server onward [WinRM service starts automatically](https://docs.microsoft.com/en-us/windows/win32/winrm/installation-and-configuration-for-windows-remote-management#configuration-of-winrm-and-ipmi).

## Usage

1) Edit line 19 in the [windows/runner.ps1.](runner.ps1) file, to provide the needed Windows username to access to VMs.

2) Ensure you are logged in to Tidal Migrations, via:
```
tidal login
```

3) Ensure you have a file `windows\servers.txt` that has a list of all the hostnames you want to scan. The hosts will need to be accessible via your network connection from the machine that you run this from.

You can easily export these with the 'Export' button from your Tidal Migrations account, https://your_domain.tidalmg.com/#/servers

4) Securely provide the password for the user account:
```
.\windows\save_password.ps1
```

5) Invoke the runner and sync with Tidal Migrations:
```
.\windows\runner.ps1 | tidal sync servers
```

You should be able to check your account and see the VMs and their corresponding attributes and metrics. You'll find that at a URL that is something like:

https://your_domain.tidalmg.com/#/servers

## Data captured

For Windows, by default, the following metrics are captured from the resources and sent and stored in Tidal Migrations:

```
Host Name
RAM Allocated (GB)
RAM Used (GB)
Storage Allocated (GB)
Storage Used (GB)
CPU Count
Operating System
Operating System Version
CPU name
```

You can also capture information about processes running on the host machine. This feature is disabled by default, to enable it uncomment lines 50 to 67 and line 96 in [windows/server_stats.ps1.](server_stats.ps1). If you do that, it will gather the following information about a process:
```
User
Process Name
Process Path
Memory Used (MB)
Max Memory Used (MB)
Total Alive Time in Seconds
```

It is also configured to capture the following values, however in order to see them in Tidal Migrations you must add the following as custom fields for servers. You can do that at a URL that looks like, https://your_domain.tidalmg.com/#/admin/servers

```
CPU_Description
CPU_Manufacturer
CPU_L2CacheSize
CPU_L3CacheSize
CPU_SocketDesignation
TotalVisible_Memory_GB
TotalVirtual_Memory_GB
```

*NB: The names must match the names above exactly. If you wish to change these or add other values you can do so at the end of the file in [windows/server_stats.ps1](windows/server_stats.ps1)*


## Troubleshooting

### Scripts disabled error

If you see an error that says:

>[file] cannot be loaded because running scripts is disabled on this system.

You can allow the script to be run by executing the following:

```
Set-ExecutionPolicy -ExecutionPolicy ByPass -Scope CurrentUser
```

See the [PowerShell documentation for more information](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy).

### Authentication error

If an error is returned describing that

>The WinRM client cannot process the request. If the authentication scheme is different from Kerberos, or if the client computer is not joined to a domain, then HTTPS transport must be used or the destination machine must be added to the TrustedHosts configuration setting. Use winrm.cmd to configure TrustedHosts

You can resolve this by running this command:

```
Set-Item WSMan:localhost\client\trustedhosts -value *
```

You can confirm this ran successfully with, `get-item WSMan:\localhost\Client\TrustedHosts`, which should list an output with a `*` under the Value column.

After running this command you should be able to try again and successfully connect to the remote hosts to gather data.
