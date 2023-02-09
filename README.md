# Upscaling Anime in mpv with 2x_AnimeJaNai

## Overview
This project provides a PowerShell script (Windows only) to set up mpv to run ONNX upscaling models in realtime with TensorRT (NVIDIA only). Linux and Mac may work with manual setup described below. Originally intented to use the 2x_AnimeJaNai models but any provided ONNX model can be selected during setup. 

## 2x_AnimeJaNai Model
Video Samples (Select 4K quality on YouTube)

[![Demo 3](demothumb1.png)](https://www.youtube.com/watch?v=gkE-uPPGzmA&list=PLcrA746sMVSi6t0PYXEDOkhocuDd31zC7&index=1)
[![Demo 2](demothumb2.png)](https://www.youtube.com/watch?v=CzGaLGjYSpQ&list=PLcrA746sMVSi6t0PYXEDOkhocuDd31zC7&index=2)
[![Demo 1](demothumb3.png)](https://www.youtube.com/watch?v=m1WMDn4FK8I&list=PLcrA746sMVSi6t0PYXEDOkhocuDd31zC7&index=3)

Additional Screenshots: https://imgsli.com/MTUxMDYx

Comparisons of all 2x_AnimeJaNai variants to Anime4K + other upscalers and compact models: https://imgsli.com/MTUxMjY4

2x_AnimeJaNai is a set of realtime 2x Real-ESRGAN Compact, UltraCompact, and SuperUltraCompact models intended for high or medium quality 1080p anime to 4k with an emphasis on correcting the inherit blurriness of anime while preserving details and colors. These models are not suitable for artifact-heavy or highly compressed content as they will just sharpen artifacts. The models can also work with SD anime by running the models twice, first from SD to HD, and then HD to UHD. The installer in this repository can set these models up to run with mpv on Windows.

|  |   |   |   |
|---|---|---|---|
|  | **Compact**<br>Highest quality models which are also the sharpest and have the most detail enhancement. Requires minimum of RTX 4090 for realitime playback, so it is most suitable for pre-rendering upscales.  | **UltraCompact**<br>High quality models which trade slight quality for major performance gains. The UltraCompact models have the best balance of quality and performance. Requires minimum of RTX 3080 for realtime playback.   | **SuperUltraCompact**<br>Fastest performance models which sacrifice a bit more quality and sharpness, primarily in background detail. Use if running any card slower than the RTX 3080 for realtime playback. Minimum card required for realtime playback has yet to be determined.  |
| **Strong**<br>Sharpest models which may oversharpen some images, but can offer a pleasant amount of sharpness when viewing from a distance on a display such as a TV or projector.  | 2x_AnimeJaNai_Strong_V1_ Compact_net_g_120000  | 2x_AnimeJaNai_Strong_V1_ UltraCompact_net_g_100000  |  2x_AnimeJaNai_Strong_V1_ SuperUltraCompact_net_g_100000 |
| **Standard**<br>Offers a middle ground in sharpness between the soft and strong models. Still includes a moderate amount of sharpening and detail enhancement, but may be too strong depending on the source video and viewing distance.   | 2x_AnimeJaNai_Standard_V1_ Compact_net_g_120000  | 2x_AnimeJaNai_Standard_V1_ UltraCompact_net_g_100000  | (To be released)  |
| **Soft**<br>Softest models which should prevent oversharpening as much as possible, but has significantly reduced sharpening in backgrounds and detail enhancement. Most suited for viewing up close on a monitor.  | (To be released)  | (To be released)  | (To be released)  |

## Installer Instructions
1. Download and extract the [latest release](https://github.com/the-database/mpv-upscale-2x_animejanai/releases/download/1.0.0/mpv-upscale-2x_animejanai_v1.zip). 
2. Optionally add any custom ONNX models to the extracted directory, which should contain `install.ps1`.
3. Run Powershell with Admin rights, navigate to the extracted directory containing `install.ps1`, execute installer with commands: 
   ```
   Set-ExecutionPolicy unrestricted
   .\install.ps1
   ```
4. Run mpv.net from `C:\mpv.net` and play any video. Upscaling is automatically applied. Toggle using `v` keyboard shortcut. 

## Simplified Setup Instructions using MPV_lazy
[MPV_lazy](https://github.com/hooke007/MPV_lazy) prepackages most of the required components (Python, VapourSynth, vs-mlrt) so it simplifies the initial setup. 
1. Download the latest MPV_lazy exe and vsCuda.7z file from the [releases page](https://github.com/hooke007/MPV_lazy/releases).
3. Run the MPV_lazy exe to self extract into a newly created mpv-lazy directory. Move the mpv-lazy directory to a permanent location. Extract vsCuda into the same mpv-lazy directory. 
4. Optionally, delete everything inside the portable_config directory in the mpv-lazy directory if you want to remove the mpv-lazy config customizations.
5. Optionally, download latest beta mpv.net from https://github.com/mpvnet-player/mpv.net/releases and extract its contents to the mpv-lazy directory if you would like to use mpv.net over mpv. 
6. Download ONNX models and move to `mpv-lazy/vapoursynth64/plugins/vsmlrt-cuda`.
7. Inside the `%APPDATA%\VapourSynth\plugins64\vsmlrt-cuda` run this command, replacing {MODEL_NAME} with the name of the ONNX model: ```.\trtexec --fp16 --onnx={MODEL_NAME}.onnx --minShapes=input:1x3x8x8 --optShapes=input:1x3x1080x1920 --maxShapes=input:1x3x1080x1920 --saveEngine={MODEL_NAME}.engine --tacticSources=+CUDNN,-CUBLAS,-CUBLAS_LT```
8. Download contents of this repository and extract to `mpv-lazy`.
9. Open `%APPDATA%\mpv.net\shaders\2x_SharpLines.vpy`. 
   1. Set the HD_ENGINE_NAME and SD_ENGINE_NAME to the name of the engines you created in step 4. 
   2. Ensure that the `engine_path` on line 26 points to the correct location. It should point to the directory where your engines were created. 

## Full Manual Setup Instructions
If the installer cannot be used, and MPV_lazy is setup can be done manually as follows. Set up on Linux or Mac should be possible with the following steps, replacing any components with their Linux or Mac equivalents, but this is untested. 
1. Install latest Python 3.10.x from https://www.python.org/downloads/windows/
1. Install latest Vapoursynth64 from https://github.com/vapoursynth/vapoursynth/releases
2. Install latest pre-release vs-mlrt from https://github.com/AmusementClub/vs-mlrt/releases
   1. Download vsmlrt-windows-x64-cuda.v12.7z and extract contents to `%APPDATA%\VapourSynth\plugins64`
3. Download ONNX models and move to `%APPDATA%\VapourSynth\plugins64\vsmlrt-cuda`
4. Inside the `%APPDATA%\VapourSynth\plugins64\vsmlrt-cuda` run this command for each model that you want to use, replacing {MODEL_NAME} with the name of the ONNX model(s): ```.\trtexec --fp16 --onnx={MODEL_NAME}.onnx --minShapes=input:1x3x8x8 --optShapes=input:1x3x1080x1920 --maxShapes=input:1x3x1080x1920 --saveEngine={MODEL_NAME}.engine --tacticSources=+CUDNN,-CUBLAS,-CUBLAS_LT```
5. Download latest beta mpv.net from https://github.com/mpvnet-player/mpv.net/releases
   1. Extract to a permanent location such as `C:\`
   2. Run `mpvnet.exe` once and then close it
7. Download contents of this repository and extract to `%APPDATA%\mpv.net`
8. Open `%APPDATA%\mpv.net\shaders\2x_SharpLines.vpy`. 
   1. Set the HD_ENGINE_NAME and SD_ENGINE_NAME to the name of the engines you created in step 4. 
   2. Ensure that the `engine_path` on line 26 points to the correct location. It should point to the directory where your engines were created. 

## Support for Other Media Players
Any media player which supports external DirectShow filters should be able to run these models, by using [avisynth_filter](https://github.com/CrendKing/avisynth_filter) to get VapourSynth running in the video player. 

## Prerendering Videos using Other Graphics Cards
The 2x_AnimeJaNai_V1 ONNX models can be used on a PC with any graphics card to render upscaled videos, even when using graphics cards not fast enough for realtime playback. Any program that supports ONNX models can be used, such as [chaiNNer](https://github.com/chaiNNer-org/chaiNNer) or [VSGAN-tensorrt-docker](https://github.com/styler00dollar/VSGAN-tensorrt-docker).

For NVIDIA users, the TensorRT backend is recommended for fastest rendering performance. AMD users should use the NCNN backend instead. Templates for chaiNNer are available for [NVIDIA](animejanai-nvidia.chn?raw=1) and [AMD](animejanai-amd.chn?raw=1) users. Simply download and open the appropriate `chn` file in chaiNNer, and select the ONNX model file and the input video file to upscale. 
