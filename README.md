# Upscaling Anime in mpv with 2x_AnimeJaNai V2

![2x animejanai v2 logo demo7](https://github.com/the-database/mpv-upscale-2x_animejanai/assets/25811902/7f293066-ece0-4c4b-b12c-a49cb95680b7)

## Overview
This project provides a set of Real-ESRGAN Compact ONNX upscaling models, and a custom build of mpv video player (currently Windows only) which supports realtime upscaling of 1080p to 4k by running those models with TensorRT (NVIDIA only). Intented to use the 2x_AnimeJaNai V2 models but any Real-ESRGAN Compact ONNX models can be used. 

## 2x_AnimeJaNai V2 Models
2x_AnimeJaNai V2 is a set of realtime 2x Real-ESRGAN Compact, UltraCompact, and SuperUltraCompact models intended to upscale 1080p anime to 4k with an emphasis on correcting the inherit blurriness of anime while preserving details and colors. The models can also work with SD anime by running the models twice, first from SD to HD, and then HD to UHD.

The V2 models offer several improvements over the V1 models, including fixed oversharpening, more accurate colors including line colors, better artifact handling, and better enhancement and preservation of background detail and grain. Overall the V2 models produce a much more faithful result than the V1 models. 

## Support for Other Media Players
Any media player which supports external DirectShow filters should be able to run these models, by using [avisynth_filter](https://github.com/CrendKing/avisynth_filter) to get VapourSynth running in the video player. 

## Prerendering Videos using Other Graphics Cards
The 2x_AnimeJaNai_V2 ONNX models can be used on a PC with any graphics card to render upscaled videos, even when using graphics cards not fast enough for realtime playback. Please see the file `shaders/animejanai_v2_encode.vpy` included in the release package for more details on how to set this up. Alternatively, any program that supports ONNX models can be used, such as [chaiNNer](https://github.com/chaiNNer-org/chaiNNer) or [VSGAN-tensorrt-docker](https://github.com/styler00dollar/VSGAN-tensorrt-docker).

For chaiNNer, the TensorRT backend is recommended for NVIDIA users for fastest rendering performance. AMD users should use the NCNN backend instead. Templates for chaiNNer are available for [NVIDIA](animejanai-nvidia.chn?raw=1) and [AMD](animejanai-amd.chn?raw=1) users. Simply download and open the appropriate `chn` file in chaiNNer, and select the ONNX model file and the input video file to upscale. 
