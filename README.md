# Upscaling Anime in mpv with 2x_AnimeJaNai

## Overview
This project provides a PowerShell script (Windows only) to set up mpv to run ONNX upscaling models in realtime with TensorRT (NVIDIA only). Linux and Mac may work with manual setup described below. Originally intented to use the 2x_AnimeJaNai models but any provided ONNX model can be selected during setup. 

## 2x_AnimeJaNai Model

https://user-images.githubusercontent.com/25811902/215538361-c94d4666-668e-4709-9164-9fe605ee25f8.mp4

Additional Samples: https://imgsli.com/MTUxMDYx

Comparisons of all 2x_AnimeJaNai variants to Anime4K + other upscalers and compact models: https://imgsli.com/MTUxMjY4

2x_AnimeJaNai is a set of realtime 2x Real-ESRGAN Compact, UltraCompact, and SuperUltraCompact models intended for high or medium quality 1080p anime to 4k with an emphasis on correcting the inherit blurriness of anime while preserving details and colors. These models are not suitable for artifact-heavy or highly compressed content as they will just sharpen artifacts. The models can also work with SD anime by running the models twice, first from SD to HD, and then HD to UHD. The installer in this repository can set these models up to run with mpv on Windows.

| Model                                                  | Minimum GPU to Upscale 1080p Anime to 4K in Realtime | Usage |
| ------------------------------------------------------ | --------------------- | ----- |
| 2x_AnimeJaNai_Standard_V1_Compact_net_g_120000         | RTX 4090              | Most suitable for upscaling high quality SD anime to 1080p. The compact model is too slow to upscale 1080p on most cards besides the RTX 4090. Also can work well on some digital art and manga. |
| 2x_AnimeJaNai_Strong_V1_Compact_net_g_120000           | RTX 4090              | Sharper version of the standard compact model, but may oversharpen some images. |
| 2x_AnimeJaNai_Standard_V1_UltraCompact_net_g_100000    | RTX 3080              | Slightly lower quality than the compact models. Most suitable for model for upscaling 1080p anime, especially when viewing up close on a monitor. The ultracompact models achieve the best balance of quality and performance. |
| 2x_AnimeJaNai_Strong_V1_UltraCompact_net_g_100000      | RTX 3080              | Sharper version of the standard ultracompact model. May appear oversharpened when viewing up close but can work best when viewing from a distance. |
| 2x_AnimeJaNai_Strong_V1_SuperUltraCompact_net_g_100000 | TBD. RTX 3060 Ti?     | Fastest performance model which sacrifices a bit more quality, primarily in background detail. Use if running any card slower than the RTX 3080. Minimum card required has yet to be determined. |

## Installer Instructions
1. Download and extract the [latest release](https://github.com/the-database/mpv-upscale-2x_animejanai/releases/download/1.0.0/mpv-upscale-2x_animejanai_v1.zip). 
2. Optionally add any custom ONNX models to the extracted directory, which should contain `install.ps1`.
3. Run Powershell with Admin rights, navigate to the extracted directory containing `install.ps1`, execute installer with commands: 
   ```
   Set-ExecutionPolicy unrestricted
   .\install.ps1
   ```

## Manual Setup Instructions
If the installer cannot be used, setup can be done manually as follows. Set up on Linux or Mac should be possible with the following steps, replacing any components with their Linux or Mac equivalents, but this is untested. 
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

## Support for Other Media Players
Any media player which supports external DirectShow filters should be able to run these models, by using [avisynth_filter](https://github.com/CrendKing/avisynth_filter) to get VapourSynth running in the video player. 
