# Machine Stats for Windows

Machine Stats for Windows uses WinRM to `Invoke-Command` across your servers, creating a JSON file which you can securely send to your [Tidal Migrations](https://tidalmigrations.com/) instance using the [tidal command](https://tidalmigrations.com/tidal-tools/).

If WinRM is not the best solution for you, you can use an alternative approach backed by WMI by running the `-NoWinRM` flag. For more information check out the [guide](https://guides.tidalmg.com/machine_stats.html#gather-machine-stats-without-winrm).

## Usage

For detailed information on the different ways to run Machine Stats for Windows, check out the [guide](https://guides.tidalmg.com/machine_stats.html#windows). This README will explain one common use case - where you want to take a single reading of your inventory and then pipe the result straight to the Tidal Migrations platform using Tidal Tools.

1) Download and install [Tidal Tools](https://get.tidal.sh/).

2) Make sure you are logged in to your Tidal Migration workspace with 👇 . Check out the [guides](https://guides.tidalmg.com/tidal-tools.html#using-tidal-tools) for more information.
```
tidal login
```

3) Prepare the username and a password to access your servers:
    - Specify `-UserName` parameter value
    - Store the password securely by running `.\save_password.ps1` script

4) Ensure you have a text file (unicode/ascii) that has a list of hosts to be scanned. Hosts can be specified either as IP addresses or as hostnames that resolve via DNS. In either case, the hostnames and IP addresses must be resolvable (private or global DNS) and routable (either locally or over the internet) from the machine that machine-stats is running on. By default, Machine Stats looks for `servers.txt`, but you can also specify any custom location with `-ServersPath` parameter.

   You can easily export these with the 'Export' button from your Tidal Migrations account, https://your_domain.tidalmg.com/#/servers

5) Invoke the runner and sync with Tidal Migrations:
```
.\windows\runner.ps1 | tidal sync servers
```

You should be able to check your account and see the VMs and their corresponding attributes and metrics. You'll find that at a URL that is something like:

`https://your_domain.tidalmg.com/#/servers`

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
CPU Name
CPU Description
CPU Manufacturer
CPU L2 Cache Size
CPU L3 Cache Size
CPU Socket Designation
Total Visible Memory (GB)
Total Virtual Memory (GB)
```

You can also capture information about processes running on the host machine. This feature is disabled by default, to enable it use the flag `-ProcessStats`. Note that this will only work when using WinRM, and so can't be used alongside the `-NoWinRM` flag. Running this flag will gather the following information about a process:
```
User
Process Name
Process Path
Memory Used (MB)
Max Memory Used (MB)
Total Alive Time in Seconds
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

### Server name cannot be resolved error

Run ping \<subject-host\>, where `subject-host` is the subject hostname or IP address. If there's no response, you need to take steps to ensure these servers can communicate with each other.

Add the subject machines to the TrustedHosts file of the controller - see [Authentication error](#authentication-error).

Ensure the firewall of the subject machines allows connections from the controller device.

After attempted these solutions you should be able to ping \<subject-hosts\> and see responses from your subject computer.
