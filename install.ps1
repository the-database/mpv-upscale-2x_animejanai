# Download doeverything.ps1
Import-Module BitsTransfer
$download = "https://raw.githubusercontent.com/the-database/mpv-upscale/main/doeverything.ps1"
$script = "doeverything.ps1"
Start-BitsTransfer -Source $download -Destination $script

# Run doeverything.ps1
& "$PSScriptRoot\$script"

# Cleanup
Remove-Item $script
