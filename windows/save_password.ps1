
# Do this once, to save your password to a secure string on disk:
$securePassword =  Read-host "What's your password?" -AsSecureString | ConvertFrom-SecureString
Set-Content "SecuredText.txt" $securePassword

Write-Output "Wrote securePassword to SecuredText.txt"

