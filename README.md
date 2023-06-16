# Upscaling Anime in mpv with 2x_AnimeJaNai V2

![2x animejanai v2 logo demo6](https://github.com/the-database/mpv-upscale-2x_animejanai/assets/25811902/f7219bd4-b1d7-41a4-8b3b-6385d28c87f2)


## Overview
This project provides a custom build of mpv video player which supports realtime upscaling using Real-ESRGAN Compact ONNX models with TensorRT (NVIDIA only). Intented to use the 2x_AnimeJaNai V2 models but any Real-ESRGAN Compact ONNX models can be used. 

## 2x_AnimeJaNai V2 Models
2x_AnimeJaNai V2 is a set of realtime 2x Real-ESRGAN Compact, UltraCompact, and SuperUltraCompact models intended for high or medium quality 1080p anime to 4k with an emphasis on correcting the inherit blurriness of anime while preserving details and colors. The models can also work with SD anime by running the models twice, first from SD to HD, and then HD to UHD. The release packages in this repository currently support Windows only.

## Support for Other Media Players
Any media player which supports external DirectShow filters should be able to run these models, by using [avisynth_filter](https://github.com/CrendKing/avisynth_filter) to get VapourSynth running in the video player. 

## Prerendering Videos using Other Graphics Cards
The 2x_AnimeJaNai_V1 ONNX models can be used on a PC with any graphics card to render upscaled videos, even when using graphics cards not fast enough for realtime playback. Any program that supports ONNX models can be used, such as [chaiNNer](https://github.com/chaiNNer-org/chaiNNer) or [VSGAN-tensorrt-docker](https://github.com/styler00dollar/VSGAN-tensorrt-docker).

For NVIDIA users, the TensorRT backend is recommended for fastest rendering performance. AMD users should use the NCNN backend instead. Templates for chaiNNer are available for [NVIDIA](animejanai-nvidia.chn?raw=1) and [AMD](animejanai-amd.chn?raw=1) users. Simply download and open the appropriate `chn` file in chaiNNer, and select the ONNX model file and the input video file to upscale. 
