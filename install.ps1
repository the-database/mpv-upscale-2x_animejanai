# Test for ONNX model
if (Test-Path *.onnx -PathType Leaf) {
    $onnx = @(gci *.onnx)[0]
    Write-Host "Using ONNX model $onnx"
} else {
    Write-Error "ONNX model not found. Download ONNX model and place in the same directory as this installer and try again."
    Exit 1
}

Import-Module BitsTransfer

#   Install 7zip module
if (Get-Module -ListAvailable -Name 7Zip4PowerShell) {
    Write-Host "7Zip4PowerShell Module exists"
} 
else {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force
    Set-PSRepository -Name 'PSGallery' -SourceLocation "https://www.powershellgallery.com/api/v2" -InstallationPolicy Trusted
    Write-Host "Installing 7Zip4PowerShell Module"
    Install-Module -Name 7Zip4PowerShell -Force
}

# Install chocolatey
if (Get-Command -Name choco.exe -ErrorAction SilentlyContinue) {
    Write-Host "Chocolatey is installed"
} else {
    Write-Host "Installing Chocolatey"
    Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

# download Vapoursynth
$repo = "vapoursynth/vapoursynth"
$releases = "https://api.github.com/repos/$repo/releases"
$tag = (Invoke-WebRequest $releases | ConvertFrom-Json)[0].tag_name
$tag = "R60" # TODO REMOVE
$fileVapoursynth = "VapourSynth64-$tag.exe"
$download = "https://github.com/$repo/releases/download/$tag/$fileVapoursynth"
Write-Host "Downloading Vapoursynth $download"
Start-BitsTransfer -Source $download -Destination $fileVapoursynth

# download vs-mlrt
$repo = "AmusementClub/vs-mlrt"
$releases = "https://api.github.com/repos/$repo/releases"
$tag = (Invoke-WebRequest $releases | ConvertFrom-Json)[0].tag_name
$fileVsMlrt = "vsmlrt-windows-x64-cuda.$tag.7z"
$download = "https://github.com/$repo/releases/download/$tag/$fileVsMlrt"
Write-Host "Downloading vs-mlrt $download"
Start-BitsTransfer -Source $download -Destination $fileVsMlrt

# download mpv.net
$repo = "mpvnet-player/mpv.net"
$releases = "https://api.github.com/repos/$repo/releases"
$tag = (Invoke-WebRequest $releases | ConvertFrom-Json)[0].tag_name
$version = $tag.Replace("v", "")
$fileMpvNet = "mpv.net-$version.zip"
$download = "https://github.com/$repo/releases/download/$tag/$fileMpvNet"
Write-Host "Downloading mpv.net $download"
Start-BitsTransfer -Source $download -Destination $fileMpvNet

# download mpv-upscale
$fileMpvUpscale = "mpv-upscale.zip"
$download = "https://github.com/the-database/mpv-upscale/archive/refs/heads/main.zip"
Write-Host "Downloading mpv.net custom configurations $download"
Start-BitsTransfer -Source https://github.com/the-database/mpv-upscale/archive/refs/heads/main.zip -Destination $fileMpvUpscale

# Extract mpv.net 
Write-Host "Installing mpv.net"
Expand-Archive -Force -Path $fileMpvNet -DestinationPath C:\mpv.net

# Install Python 3.10
$version = (&{python -V}).Exception.Message
if ($version -like "*3.10*" -or $version -like "*3.8*") {
    Write-Host "$version is installed"
}
else {
    Write-Host "Installing Python 3.10.8"
    choco install -y python3 --version=3.10.8
}

# Install VapourSynth 
Write-Host "Installing VapourSynth - choose Install for all users"
Start-Process -FilePath $fileVapoursynth -Wait -PassThru -Verb runAs -ArgumentList '/s','/v"/qn"'

# Extract vs-mlrt
Write-Host "Installing vs-mlrt"
Expand-7Zip -ArchiveFileName $fileVsMlrt -TargetPath "$env:APPDATA/VapourSynth/plugins64"

# Copy ONNX
Write-Host "Creating TensorRT engine from ONNX model"
$env:CUDA_MODULE_LOADING="LAZY"
$engineName = (Get-Item -Path $onnx).BaseName
$pluginPath = "$env:APPDATA/VapourSynth/plugins64/vsmlrt-cuda"
$enginePath = "$pluginPath/$engineName.engine"
Copy-Item -Force -Path $onnx -Destination $enginePath
& "$pluginPath\trtexec" --fp16 --onnx=$onnx --minShapes=input:1x3x8x8 --optShapes=input:1x3x1080x1920 --maxShapes=input:1x3x1080x1920 --saveEngine="$enginePath" --tacticSources=+CUDNN,-CUBLAS,-CUBLAS_LT

# Extract mpv-upscale
Write-Host "Installing mpv.net custom configurations"
Expand-Archive -Path $fileMpvUpscale -DestinationPath "."
$sourceFolder = ".\mpv-upscale-main"
$editFile = "$sourceFolder\shaders\2x_SharpLines.vpy"
(Get-Content $editFile) -replace 'ENGINE_NAME = .+', "ENGINE_NAME = ""$engineName""" | Set-Content $editFile
$editFile = "$sourceFolder\shaders\2x_SharpLinesLite.vpy"
(Get-Content $editFile) -replace 'ENGINE_NAME = .+', "ENGINE_NAME = ""$engineName""" | Set-Content $editFile
Copy-Item -Force -Path $sourceFolder\* -Destination "$env:APPDATA/mpv.net" -Recurse
if (!(Test-Path "$env:APPDATA/mpv.net/custom.conf"))
{
   New-Item -path $env:APPDATA/mpv.net -name custom.conf -type "file" 
}

# Cleanup
Remove-Item -LiteralPath $sourceFolder -Force -Recurse
Remove-Item -Path $fileMpvNet -Force
Remove-Item -Path $fileVsMlrt -Force
Remove-Item -Path $fileVapourSynth -Force 
Remove-Item -Path $fileMpvUpscale -Force
