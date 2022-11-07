# mpv-upscale
## Installer Instructions
1. Download `install.ps1` from this repository
2. Download ONNX model and move to same directory as `install.ps1`
3. Run Powershell with Admin rights, navigate to directory containing `install.ps1`, execute installer with command: `.\install.ps1`

## Manual Setup Instructions
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
