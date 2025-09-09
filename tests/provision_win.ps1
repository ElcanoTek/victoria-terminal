# PowerShell script to run the Victoria installer in the Windows VM

$installer_name = "VictoriaSetup.exe"
$installer_path = "C:\vagrant\installers\$installer_name"

Write-Host "Looking for installer at: $installer_path"

if (Test-Path $installer_path) {
    Write-Host "Installer found. Running it silently..."
    # Use /VERYSILENT and /SP- for a non-interactive Inno Setup installation.
    # Start-Process waits for the installer to finish.
    Start-Process -FilePath $installer_path -ArgumentList "/VERYSILENT /SP-" -Wait
    Write-Host "Installer finished. Victoria should now be installed."
    Write-Host "You can find it in the Start Menu."
} else {
    Write-Host "------------------------------------------------------------------"
    Write-Host "Installer not found at $installer_path."
    Write-Host "Please download the '$installer_name' from the GitHub Releases"
    Write-Host "and place it in the 'installers/' directory of this project on your host machine."
    Write-Host "Then, run 'vagrant provision' or 'vagrant reload --provision'."
    Write-Host "------------------------------------------------------------------"
}
