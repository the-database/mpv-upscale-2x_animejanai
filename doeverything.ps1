# Test for ONNX model
if (Test-Path *.onnx -PathType Leaf) {
    $allOnnx = Get-ChildItem *.onnx
    $onnxPrompt = ""
    for ($counter=0; $counter -lt ($allOnnx | Measure-Object).Count; $counter++){
        $onnxPrompt += "$($counter+1). $($allOnnx[$counter].Name)`n"
    }

    $prompt = "Select ONNX model for upscaling SD content (Recommended: Compact): `n$onnxPrompt"
    do {
        $sdChoice = Read-Host $prompt
        $prompt = "Invalid selection. Number must be between 1 and $($allOnnx.Length). $prompt"

    } while ($sdChoice -lt 1 -or $sdChoice -gt $allOnnx.Length)

    $sdOnnx = @(Get-ChildItem *.onnx)[$sdChoice-1]

    $prompt = "Select ONNX model for upscaling HD content (Recommended: UltraCompact (Quality) or SubCompact (Performance)): `n$onnxPrompt"
    do {
        $hdChoice = Read-Host $prompt
        $prompt = "Invalid selection. Number must be between 1 and $($allOnnx.Length). $prompt"

    } while ($hdChoice -lt 1 -or $hdChoice -gt $allOnnx.Length)

    $hdOnnx = @(Get-ChildItem *.onnx)[$hdChoice-1]
    
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

$mpvnetPath = "C:\mpv.net"
$pluginPath = "$mpvnetPath/vapoursynth64/plugins/vsmlrt-cuda"


# download mpv.net
$repo = "mpvnet-player/mpv.net"
$releases = "https://api.github.com/repos/$repo/releases"
$tag = (Invoke-WebRequest -UseBasicParsing $releases | ConvertFrom-Json)[0].tag_name
$version = $tag.Replace("v", "")
$fileMpvNet = "mpv.net-$version.zip"

# check if file exists before downloading
if(-not(Test-Path $fileMpvNet)){
    $download = "https://github.com/$repo/releases/download/$tag/$fileMpvNet"
    Write-Host "Downloading mpv.net $download"
    Start-BitsTransfer -Source $download -Destination $fileMpvNet
}

# download mpv_lazy
$repo = "hooke007/MPV_lazy"
$releases = "https://api.github.com/repos/$repo/releases"
$tag = (Invoke-WebRequest -UseBasicParsing $releases | ConvertFrom-Json)[0].tag_name
$fileMpvLazy = "mpv-lazy-$tag-vsMega.7z"
$fileMpvLazyExe = "mpv-lazy-$tag.exe"

# check if files exist before downloading
if((-not(Test-Path $fileMpvLazy)) -or (-not(Test-Path $fileMpvLazyExe))){
    $download = "https://github.com/$repo/releases/download/$tag/$fileMpvLazy"
    $downloadExe = "https://github.com/$repo/releases/download/$tag/$fileMpvLazyExe"
    Write-Host "Downloading mpv_lazy $download"
    Start-BitsTransfer -Source $downloadExe -Destination $fileMpvLazyExe
    Start-BitsTransfer -Source $download -Destination $fileMpvLazy
}

# download mpv-upscale-2x_animejanai
$fileMpvUpscale = "mpv-upscale-2x_animejanai.zip"

# check if file exists before downloading and use web request instead of bits transfer because dynamic zip
if(-not(Test-Path $fileMpvUpscale)){
    $url = "https://github.com/the-database/mpv-upscale-2x_animejanai/archive/refs/heads/main.zip"
    $output = $fileMpvUpscale
    Write-Host "Downloading mpv.net custom configurations $download"
    Invoke-WebRequest -Uri $url -OutFile $output
}

# Install mpv_lazy
Write-Host "Installing mpv_lazy"
Start-Process mpv-lazy-20230127.exe -ArgumentList "-y" -Wait
Remove-Item "./mpv-lazy/portable_config" -Force -Recurse
Expand-7Zip -ArchiveFileName $fileMpvLazy -TargetPath "." 
Rename-Item mpv-lazy mpv.net
Copy-Item -Path ".\mpv.net" -Destination "C:\" -Recurse -Force

# Extract mpv.net 
Write-Host "Installing mpv.net"
Expand-Archive -Force -Path $fileMpvNet -DestinationPath $mpvnetPath

# Copy HD ONNX and create engine
$env:CUDA_MODULE_LOADING="LAZY"
$hdEngineName = "$((Get-Item -Path $hdOnnx).BaseName)-1080"
$enginePath = "$pluginPath/$hdEngineName.engine"
Copy-Item -Path $hdOnnx -Destination $pluginPath
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
    Write-Host "Creating TensorRT engine from ONNX model $hdOnnx"
    & "$pluginPath\trtexec" --fp16 --onnx=$hdOnnx --minShapes=input:1x3x8x8 --optShapes=input:1x3x1080x1920 --maxShapes=input:1x3x1080x1920 --saveEngine="$enginePath" --tacticSources=+CUDNN,-CUBLAS,-CUBLAS_LT
}

# Copy SD ONNX and create engine
$env:CUDA_MODULE_LOADING="LAZY"
$sdEngineName = "$((Get-Item -Path $sdOnnx).BaseName)-720"
$enginePath = "$pluginPath/$sdEngineName.engine"
Copy-Item -Path $sdOnnx -Destination $pluginPath
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
    Write-Host "Creating TensorRT engine from ONNX model $sdOnnx"
    & "$pluginPath\trtexec" --fp16 --onnx=$sdOnnx --minShapes=input:1x3x8x8 --optShapes=input:1x3x720x1280 --maxShapes=input:1x3x1080x1920 --saveEngine="$enginePath" --tacticSources=+CUDNN,-CUBLAS,-CUBLAS_LT
}

# Extract mpv-upscale-2x_animejanai
Write-Host "Installing mpv.net custom configurations"
Expand-Archive -Path $fileMpvUpscale -DestinationPath "."
Write-Host "Finished expand-archive"
$sourceFolder = ".\mpv-upscale-2x_animejanai-main"
$editFile = "$sourceFolder\shaders\2x_SharpLines.vpy"
(Get-Content $editFile) -replace 'SD_ENGINE_NAME = .+', "SD_ENGINE_NAME = ""$sdEngineName""" | Set-Content $editFile
(Get-Content $editFile) -replace 'HD_ENGINE_NAME = .+', "HD_ENGINE_NAME = ""$hdEngineName""" | Set-Content $editFile
$editFile = "$sourceFolder\shaders\2x_SharpLinesLite.vpy"
(Get-Content $editFile) -replace 'ENGINE_NAME = .+', "ENGINE_NAME = ""$hdEngineName""" | Set-Content $editFile
#Copy-Item -Force -Path $sourceFolder\* -Destination "$env:APPDATA/mpv.net" -Recurse
Copy-Item -Force -Path $sourceFolder\* -Destination "C:\mpv.net\portable_config" -Recurse
if (!(Test-Path "C:\mpv.net\portable_config/custom.conf"))
{
    New-Item -path C:\mpv.net\portable_config -name custom.conf -type "file" 
}

# Cleanup
#Write-Host "Cleaning up downloaded files"
#Remove-Item -LiteralPath $sourceFolder -Force -Recurse
#Remove-Item -Path $fileMpvNet -Force
#Remove-Item -Path $fileMpvUpscale -Force
#Remove-Item -Path $fileMpvLazy -Force
#Remove-Item -Path $fileMpvLazyExe -Force
#Remove-Item -Path "mpv.net" -Force -Recurse
Write-Host "Done"
