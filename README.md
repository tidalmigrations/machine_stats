# AD Windows Machine Stats
A simple and effective way to gather machine statistics (RAM, Storage, CPU) 
from a Windows Server environment.  Uses WinRM to Invoke-Command across 
your servers, creating a JSON file to securely send to your [Tidal Migrations](https://tidalmigrations.com/) 
instance using the [tidal command](https://tidalmigrations.com/tidal-tools/).

## Windows

The script `runner.ps1` should be customized for each environment.

1) Specifiy your username and a list of hostnames (either from reading a
file, hard coded, or querying a directory).

2) If you plan on running this in a scheduled task, you may want to
store your credential with the PsCredential method. See [this blog post](https://www.interworks.com/blog/trhymer/2013/07/08/powershell-how-encrypt-and-store-credentials-securely-use-automation-scripts) for an example.


_NB:_ You do need WinRM enabled across your environment for this.  
For a simple guide to do this via GPO, see [here](https://support.auvik.com/hc/en-us/articles/204424994-How-to-enable-WinRM-with-domain-controller-Group-Policy-for-WMI-monitoring).

