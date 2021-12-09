# Contributing to Machine Stats for Windows

Welcome! Happy to see you willing to make the project better.

## Testing Environments

Here's the short description on how to create a testing environment on [Google Cloud Platform](https://cloud.google.com/).

You need to create two VMs — one as _operator_ machine, i.e the machine where you'll be running the script, and another one the machine you'll be gathering stats from.

e2-micro machine type are good for both VMs. For operator machine you need to specify Windows Server version with Desktop Experience (e.g Windows Server 2012 R2 Datacenter). For another VM it's OK to choose the version without Desktop Experience, for example, Windows Server version 2004 Datacenter Core, because you're not going to connect to that instance directly (using RDP), but only using the Machine Stats PowerShell script from the operator VM.

### Getting the code

#### From Git repository

1. Open Internet Explorer and allow downloads:
   1. Click the gear-shaped Tools button and select Internet Options.
   2. Select the Security tab and click Custom Level.
   3. Scroll through the Security Settings list to the Downloads heading and select the Enable radio button to permit downloads. Click OK. Click Yes when prompted.
   4. Close and restart Internet Explorer to apply the changes.
2. Browse to the official Git website: https://git-scm.com/downloads
3. Click the download link for Windows and allow the download to complete.
4. Browse to the download location (or use the download shortcut in your browser). Double-click the file to extract and launch the installer.
5. Open PowerShell or Git Bash and run `git clone https://github.com/tidalmigrations/machine_stats.git`
6. The code for Machine Stats for Windows is in the `C:\Users\<YourUserName>\machine_stats\windows` where `<YourUserName>` is the name of your Windows user.

#### From Google Cloud Storage bucket

If you would like to test some changes which are not in Git repository do the following:

1. Create a new Google Cloud Storage bucket using [Google Cloud Console](https://console.cloud.google.com/storage/create-bucket) or [Google Cloud SDK](https://cloud.google.com/storage/docs/gsutil/commands/mb).
2. Upload scripts to that bucket, e.g `gsutil cp windows/*.ps1 gs://my-bucket`
3. Connect to the _operator_ VM via RDP and run the following command from PowerShell or command prompt:
   ```
   gsutil cp gs://my-bucker/*.ps1 .
   ```
   Replace `my-bucket` with the actual name of your Google Cloud Storage bucket.
   
### Configure WinRM

To make it possible to connect from one Windows VM to another we need to do the following:

1. Open Windows Start menu
2. Search for Windows PowerShell
3. Right-click on Windows PowerShell icon and select Run as administrator from the contect menu
4. In the opened PowerShell prompt run the following command:
   ```
   Set-Item WSMan:localhost\client\trustedhosts -value *
   ```
5. Close the administrator PowerShell window. You're ready to connect to other Windows machines with WinRM.
