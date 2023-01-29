# https://github.com/the-database/mpv-upscale

# Download doeverything.ps1
Import-Module BitsTransfer
$script = "doeverything.ps1"
$download = "https://raw.githubusercontent.com/the-database/mpv-upscale/main/$script"
Start-BitsTransfer -Source $download -Destination $script

# Run doeverything.ps1
& "$PSScriptRoot\$script"

# Cleanup
Remove-Item $script
