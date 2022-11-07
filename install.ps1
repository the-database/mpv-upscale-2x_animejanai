# Test for ONNX model
if (Test-Path *.onnx -PathType Leaf) {
    $hdOnnx = @(Get-ChildItem *UltraCompact*.onnx)[0]
    $sdOnnx = @(Get-ChildItem *Compact*.onnx -Exclude "UltraCompact")[0]
    if ($null -eq $sdOnnx) {
        $sdOnnx = $hdOnnx
    }
    Write-Host "For SD content, using ONNX model $sdOnnx"
    Write-Host "For HD content, using ONNX model $hdOnnx"
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


$pluginPath = "$env:APPDATA/VapourSynth/plugins64/vsmlrt-cuda"


# download Vapoursynth
$repo = "vapoursynth/vapoursynth"
$releases = "https://api.github.com/repos/$repo/releases"
$tagVapoursynth = (Invoke-WebRequest -UseBasicParsing $releases | ConvertFrom-Json)[0].tag_name
$fileVapoursynth = "VapourSynth64-$tagVapoursynth.exe"
$download = "https://github.com/$repo/releases/download/$tagVapoursynth/$fileVapoursynth"
Write-Host "Downloading Vapoursynth $download"
Start-BitsTransfer -Source $download -Destination $fileVapoursynth

# download vs-mlrt
$installVsMlrt = !(Test-Path $pluginPath)
if (-not $installVsMlrt) {
    # Create prompt body
    $title = "Confirm"
    $message = "vs-mlrt is already installed. Reinstall latest version?"
    
    # Create answers
    $yes = New-Object System.Management.Automation.Host.ChoiceDescription "&Yes", "Continue with the next step of the operation."
    $no = New-Object System.Management.Automation.Host.ChoiceDescription "&No", "Skip this operation and proceed with the next operation."
    
    # Create ChoiceDescription with answers
    $options = [System.Management.Automation.Host.ChoiceDescription[]]($yes, $no)

    # Show prompt and save user's answer to variable
    $response = $host.UI.PromptForChoice($title, $message, $options, 1)

    $installVsMlrt = $response -eq 0
}
if ($installVsMlrt) {
    $repo = "AmusementClub/vs-mlrt"
    $releases = "https://api.github.com/repos/$repo/releases"
    $tag = (Invoke-WebRequest -UseBasicParsing $releases | ConvertFrom-Json)[0].tag_name
    $fileVsMlrt = "vsmlrt-windows-x64-cuda.$tag.7z"
    $download = "https://github.com/$repo/releases/download/$tag/$fileVsMlrt"
    Write-Host "Downloading vs-mlrt $download"
    Start-BitsTransfer -Source $download -Destination $fileVsMlrt
}

# download mpv.net
$repo = "mpvnet-player/mpv.net"
$releases = "https://api.github.com/repos/$repo/releases"
$tag = (Invoke-WebRequest -UseBasicParsing $releases | ConvertFrom-Json)[0].tag_name
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
if ((&{vspipe -v} 2>&1) -like "*$tagVapoursynth*") {
    Write-Host "VapourSynth $tagVapoursynth is installed"
} else {
    Write-Host "Installing VapourSynth - choose Install for all users"
    Start-Process -FilePath $fileVapoursynth -Wait -PassThru -Verb runAs -ArgumentList '/s','/v"/qn"'
}

# Extract vs-mlrt
if ($installVsMlrt) { 
    Write-Host "Installing vs-mlrt"
    Expand-7Zip -ArchiveFileName $fileVsMlrt -TargetPath "$env:APPDATA/VapourSynth/plugins64"
}

# Copy HD ONNX and create engine
Write-Host "Creating TensorRT engine from ONNX model $hdOnnx"
$env:CUDA_MODULE_LOADING="LAZY"
$hdEngineName = "$((Get-Item -Path $hdOnnx).BaseName)-1080"
$enginePath = "$pluginPath/$hdEngineName.engine"
Copy-Item -Path $hdOnnx -Destination $enginePath
$createEngine = !(Test-Path $enginePath)
if (-not $createEngine) {
    # Create prompt body
    $title = "Confirm"
    $message = "$enginePath already exists. Re-generate engine and replace existing engine?"
    
    # Create answers
    $yes = New-Object System.Management.Automation.Host.ChoiceDescription "&Yes", "Continue with the next step of the operation."
    $no = New-Object System.Management.Automation.Host.ChoiceDescription "&No", "Skip this operation and proceed with the next operation."
    
    # Create ChoiceDescription with answers
    $options = [System.Management.Automation.Host.ChoiceDescription[]]($yes, $no)

    # Show prompt and save user's answer to variable
    $response = $host.UI.PromptForChoice($title, $message, $options, 1)

    $createEngine = $response -eq 0
}
if ($createEngine) {
    & "$pluginPath\trtexec" --fp16 --onnx=$hdOnnx --minShapes=input:1x3x8x8 --optShapes=input:1x3x1080x1920 --maxShapes=input:1x3x1080x1920 --saveEngine="$enginePath" --tacticSources=+CUDNN,-CUBLAS,-CUBLAS_LT
}

# Copy SD ONNX and create engine
Write-Host "Creating TensorRT engine from ONNX model $sdOnnx"
$env:CUDA_MODULE_LOADING="LAZY"
$sdEngineName = "$((Get-Item -Path $sdOnnx).BaseName)-720"
$enginePath = "$pluginPath/$sdEngineName.engine"
Copy-Item -Path $sdOnnx -Destination $enginePath
$createEngine = !(Test-Path $enginePath)
if (-not $createEngine) {
    # Create prompt body
    $title = "Confirm"
    $message = "$enginePath already exists. Re-generate engine and replace existing engine?"
    
    # Create answers
    $yes = New-Object System.Management.Automation.Host.ChoiceDescription "&Yes", "Continue with the next step of the operation."
    $no = New-Object System.Management.Automation.Host.ChoiceDescription "&No", "Skip this operation and proceed with the next operation."
    
    # Create ChoiceDescription with answers
    $options = [System.Management.Automation.Host.ChoiceDescription[]]($yes, $no)

    # Show prompt and save user's answer to variable
    $response = $host.UI.PromptForChoice($title, $message, $options, 1)

    $createEngine = $response -eq 0
}
if ($createEngine) {
    & "$pluginPath\trtexec" --fp16 --onnx=$sdOnnx --minShapes=input:1x3x8x8 --optShapes=input:1x3x720x1280 --maxShapes=input:1x3x720x1280 --saveEngine="$enginePath" --tacticSources=+CUDNN,-CUBLAS,-CUBLAS_LT
}

# Extract mpv-upscale
Write-Host "Installing mpv.net custom configurations"
Expand-Archive -Path $fileMpvUpscale -DestinationPath "."
$sourceFolder = ".\mpv-upscale-main"
$editFile = "$sourceFolder\shaders\2x_SharpLines.vpy"
(Get-Content $editFile) -replace 'SD_ENGINE_NAME = .+', "SD_ENGINE_NAME = ""$sdEngineName""" | Set-Content $editFile
(Get-Content $editFile) -replace 'HD_ENGINE_NAME = .+', "HD_ENGINE_NAME = ""$hdEngineName""" | Set-Content $editFile
$editFile = "$sourceFolder\shaders\2x_SharpLinesLite.vpy"
(Get-Content $editFile) -replace 'ENGINE_NAME = .+', "ENGINE_NAME = ""$sdEngineName""" | Set-Content $editFile
Copy-Item -Force -Path $sourceFolder\* -Destination "$env:APPDATA/mpv.net" -Recurse
if (!(Test-Path "$env:APPDATA/mpv.net/custom.conf"))
{
    New-Item -path $env:APPDATA/mpv.net -name custom.conf -type "file" 
}


# Cleanup
Write-Host "Cleaning up downloaded files"
Remove-Item -LiteralPath $sourceFolder -Force -Recurse
Remove-Item -Path $fileMpvNet -Force
Remove-Item -Path $fileVapourSynth -Force 
Remove-Item -Path $fileMpvUpscale -Force
if ($installVsMlrt) {
    Remove-Item -Path $fileVsMlrt -Force
}
Write-Host "Done"
