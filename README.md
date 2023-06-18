# Upscaling Anime in mpv with 2x_AnimeJaNai V2

![2x animejanai v2 logo demo7](https://github.com/the-database/mpv-upscale-2x_animejanai/assets/25811902/7f293066-ece0-4c4b-b12c-a49cb95680b7)

## Overview
This project provides a collection of Real-ESRGAN Compact ONNX upscaling models, along with a custom build of mpv video player. The video player (currently Windows only), enables real-time upscaling of 1080p content to 4K by running these models using TensorRT (NVIDIA only). While the default configuration upscales using the 2x_AnimeJaNai V2 models, it can be easily customized to utilize any Real-ESRGAN Compact ONNX models.

## 2x_AnimeJaNai V2 Models
The 2x_AnimeJaNai V2 models are a collection of real-time 2x Real-ESRGAN Compact, UltraCompact, and SuperUltraCompact models designed specifically for upscaling 1080p anime to 4K resolution. These models prioritize correcting the inherent blurriness often found in anime while preserving essential details and colors. Although trained on 1080p anime and optimized for upscaling from 1080p to 4K, the models can still produce worthwhile results when upscaling some lower-resolution anime. SD anime can be upscaled to HD, or the model can be run twice to upscale SD content to UHD.

Typically, most HD anime are [not produced in native 1080p resolution]((https://guide.encode.moe/encoding/descaling.html)) but rather have a production resolution between 720p to 1080p. During distribution, the video is scaled up to 1080p, leading to scaling artifacts and a loss of image clarity. The aim of these models was to address these scaling and blur-related issues while upscaling to deliver a result that appears as if the anime was originally mastered in 4K resolution.

The development of the V2 models spanned over four months, during which over 200 release candidate models were trained and meticulously refined. The V2 models introduce several notable improvements compared to their V1 counterparts, including corrected oversharpening artifacts, more accurate colors including line colors, improved artifact handling, and better preservation and enhancement of background details and grain. Overall, the V2 models yield significantly more natural and faithful results compared to the V1 models.


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
