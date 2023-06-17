# Upscaling Anime in mpv with 2x_AnimeJaNai V2

![2x animejanai v2 logo demo7](https://github.com/the-database/mpv-upscale-2x_animejanai/assets/25811902/7f293066-ece0-4c4b-b12c-a49cb95680b7)

## Overview
This project provides a set of Real-ESRGAN Compact ONNX upscaling models, and a custom build of mpv video player (currently Windows only) which supports realtime upscaling of 1080p to 4k by running those models with TensorRT (NVIDIA only). Intented to use the 2x_AnimeJaNai V2 models but can be configured to run any Real-ESRGAN Compact ONNX models. 

## 2x_AnimeJaNai V2 Models
2x_AnimeJaNai V2 is a set of realtime 2x Real-ESRGAN Compact, UltraCompact, and SuperUltraCompact models intended to upscale 1080p anime to 4k with an emphasis on correcting the inherit blurriness of anime while preserving details and colors. While the models are trained specifically on 1080p anime and work best upscaling 1080p to 4k, the models can also produce acceptable results with lower resolution anime. SD anime may be upscaled to HD, or the model may be run twice to upscale SD to UHD.

Most HD anime is [not produced in native 1080p resolution](https://guide.encode.moe/encoding/descaling.html), but some resolution between 720p and 1080p. When the anime video is prepared for broadcast, it is scaled to 1080p resolution which results in scaling artifacts and a blurry image. In training these models, the goal was to address these scaling and blur issues and produce a result that appears as if the anime was originally mastered in 4k resolution.

The V2 models offer several improvements over the V1 models, including fixed oversharpening artifacts, more accurate colors including line colors, better artifact handling, and better enhancement and preservation of background detail and grain. Overall the V2 models produce a much more natural and faithful result compared to the V1 models. 


## Support for Other Media Players
Any media player which supports external DirectShow filters should be able to run these models, by using [avisynth_filter](https://github.com/CrendKing/avisynth_filter) to get VapourSynth running in the video player. 

## Prerendering Videos using Other Graphics Cards
The 2x_AnimeJaNai_V2 ONNX models can be used on a PC with any graphics card to render upscaled videos, even when using graphics cards not fast enough for realtime playback. Please see the file `shaders/animejanai_v2_encode.vpy` included in the release package for more details on how to set this up. Alternatively, any program that supports ONNX models can be used, such as [chaiNNer](https://github.com/chaiNNer-org/chaiNNer) or [VSGAN-tensorrt-docker](https://github.com/styler00dollar/VSGAN-tensorrt-docker).

For chaiNNer, the TensorRT backend is recommended for NVIDIA users for fastest rendering performance. AMD users should use the NCNN backend instead. Templates for chaiNNer are available for [NVIDIA](animejanai-nvidia.chn?raw=1) and [AMD](animejanai-amd.chn?raw=1) users. Simply download and open the appropriate `chn` file in chaiNNer, and select the ONNX model file and the input video file to upscale. 

## Acknowledgements
- [Upscale Wiki](https://upscale.wiki/wiki/Main_Page) and associated Discord server
  - 4x-AnimeSharp by Kim2091
  - 1x_HurrDeblur_SuperUltraCompact by Zarxrax
  - SaiyaJin DeJpeg by Twittman
- [422415](https://github.com/422415) for significant assistance in dataset preparation and continuous feedback during development of V2 models
- Community feedback on V1 models
- [MPV_lazy](https://github.com/hooke007/MPV_lazy) and [vs-mlrt](https://github.com/AmusementClub/vs-mlrt)
- [traiNNer-redux](https://github.com/joeyballentine/traiNNer-redux)
- [Dataset Destroyer](https://github.com/Kim2091/helpful-scripts/tree/main/Dataset%20Destroyer)
- [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)
- [OpenModelDB](https://openmodeldb.info/)
- [getnative](https://github.com/Infiziert90/getnative)
