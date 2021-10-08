# Machine Stats for Windows

Machine Stats for Windows gathers different parameters (RAM, Storage, CPU, etc) across your servers, creating a JSON file to securely send to your [Tidal Migrations](https://tidalmigrations.com/) instance using the [tidal command](https://tidalmigrations.com/tidal-tools/).

## Features

It is capable of connecting and gathering information from Windows machines via two different approaches. By default, it connects to machines via WinRM or if remote hosts are on the same domain it is able to connect directly via WMI.
- Works with computers within an AD domain or workgroups
- Customizable CPU utilization measurement timeouts
- Ready to be run in a scheduled task

## Usage

1. Download and install [Tidal Tools](https://get.tidal.sh/).
2. Ensure you are logged in to your Tidal Migrations account with
    ```
    tidal login
    ```
3. Prepare the username and a password to access your servers:
    - Specify `-UserName` parameter value
    - Store the password securely by running `.\save_password.ps1` script
4. Ensure you have a file that has a list of all the hostnames you want to scan. By default, Machine Stats looks for `servers.txt`, but you can also specify any custom location with `-ServersPath` parameter. The hosts will need to be accessible via your network connection from the machine that you run this from.

   You can easily export these with the 'Export' button from your Tidal Migrations account, https://your_domain.tidalmg.com/#/servers
5. Invoke the runner and sync with Tidal Migrations:
    ```
    .\runner.ps1 | tidal sync servers
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

It is also configured to capture the following values:

```
CPU_Description
CPU_Manufacturer
CPU_L2CacheSize
CPU_L3CacheSize
CPU_SocketDesignation
TotalVisible_Memory_GB
TotalVirtual_Memory_GB
CPU Utilization
```

## Parameters

### `-UserName <String>`

Specifies the user name used for connection to the remote machine.
To securely provide a password, please run the `save_password.ps1` 
script.
        
### `-ServersPath <String>`

Specifies the path to file with the list of servers (one server per 
line).
By default it looks for `servers.txt` in the current directory.
        
### `-CpuUtilizationTimeout <Double>`

Specifies the number of seconds to measure CPU utilization.
The default value is `30`.
        
### `-NoWinRM [<SwitchParameter>]`

Specifies if WinRM should not be used.

## Getting more help

To get more help, run the following:

```
Get-Help .\runner.ps1 -Full
```

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
