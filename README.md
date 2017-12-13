# machine_stats
A collection of functions for capturing machine statistics

## Windows

The script `runner.ps1` should be customized for each environment.

1) Specifiy your username and a list of hostnames (either from reading a
file, or hard coded).

2) If you plan on running this in a scheduled task, you may want to
store your credential with the PsCredential method. See https://www.interworks.com/blog/trhymer/2013/07/08/powershell-how-encrypt-and-store-credentials-securely-use-automation-scripts for an example.


NB: You do need WinRM enabled across your environment for this.  One
simple guide to do this via GPO is:
https://support.auvik.com/hc/en-us/articles/204424994-How-to-enable-WinRM-with-domain-controller-Group-Policy-for-WMI-monitoring

