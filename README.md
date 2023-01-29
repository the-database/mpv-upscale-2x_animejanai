# mpv-upscale

## Overview
This project provides a PowerShell script (Windows only) to set up mpv to run ONNX upscaling models in realtime with TensorRT. Originally intented to use the 2x_AnimeJaNai models but any provided ONNX model can be selected during setup. 

## 2x_AnimeJaNai Model
2x_AnimeJaNai is a set of realtime 2x Real-ESRGAN Compact, UltraCompact, and SuperUltraCompact models intended for high or medium quality 1080p anime with an emphasis on correcting the inherit blurriness of anime while preserving details and colors. These models are not suitable for artifact-heavy or highly compressed content as they will just sharpen artifacts. The models also work with SD anime by running the models twice. The installer in this repository can set these models up to run with mpv on Windows.

Minimum of RTX 3080 is recommended for running UltraCompact model on 1080p in realtime; RTX 4090 is required to run Compact on 1080p in realtime. SuperUltraCompact should run in realtime on 1080p on some lower cards. The compact model is recommended on SD content. 

![Sample - Original Image](s1-original.png)
![Sample - Original Image](s1-2x_AnimeJaNai_Strong_V1_UltraCompact_net_g_100000.png)

Samples: https://imgsli.com/MTUxMDYx

Comparisons to Anime4K + other upscalers and compact models: https://imgsli.com/MTUxMjMx 

## Installer Instructions
1. Download and extract the [latest release](https://github.com/the-database/mpv-upscale-2x_animejanai/releases/download/1.0.0/mpv-upscale-2x_animejanai_v1.zip). 
2. Optionally add any custom ONNX models to the extracted directory, which should contain `install.ps1`.
3. Run Powershell with Admin rights, navigate to the extracted directory containing `install.ps1`, execute installer with commands: 
   ```
   Set-ExecutionPolicy unrestricted
   .\install.ps1
   ```

## Manual Setup Instructions
If the installer cannot be used, setup can be done manually as follows. 
1. Install latest Python 3.10.x from https://www.python.org/downloads/windows/
1. Install latest Vapoursynth64 from https://github.com/vapoursynth/vapoursynth/releases
2. Install latest pre-release vs-mlrt from https://github.com/AmusementClub/vs-mlrt/releases
   1. Download vsmlrt-windows-x64-cuda.v12.7z and extract contents to `%APPDATA%\VapourSynth\plugins64`
3. Download ONNX model and move to `%APPDATA%\VapourSynth\plugins64\vsmlrt-cuda`
4. Run command, replacing {MODEL_NAME} with the name of the ONNX model: ```.\trtexec --fp16 --onnx={MODEL_NAME}.onnx --minShapes=input:1x3x8x8 --optShapes=input:1x3x1080x1920 --maxShapes=input:1x3x1080x1920 --saveEngine={MODEL_NAME}.engine --tacticSources=+CUDNN,-CUBLAS,-CUBLAS_LT```
5. Download latest beta mpv.net from https://github.com/mpvnet-player/mpv.net/releases
   1. Extract to a permanent location such as `C:\`
   2. Run `mpvnet.exe` once and then close it
7. Download contents of this repository and extract to `%APPDATA%\mpv.net`
