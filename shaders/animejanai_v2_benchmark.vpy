import sys, os, pathlib
import vapoursynth as vs

sys.path.append(str(pathlib.Path().absolute()))

import animejanai_v2

# Instructions for running this benchmarking tool
# 1. First time setup, open a command window in your main mpv directory and run:
#     .\python.exe .\vsrepo.py -p update
#     .\python.exe .\vsrepo.py install ffms2
# 2. Edit the path of the source video below, from ./video.mkv to the path of 
#    the video you want to benchmark upscaling on
# 3. Set the keybinding below, to a value between 1-9 to select the onnx model 
#    you want to benchmark
# 4. Run the following command from the main mpv directory:
#     .\VSPipe.exe --start 0 --end 2000 ./portable_config/shaders/animejanai_v2_benchmark.vpy -p .

clip = vs.core.ffms2.Source(source=r"./[FFF] Saenai Heroine no Sodatekata - OP01 [BD][1080p-FLAC][C3FE525F].mkv")
keybinding = 1 

animejanai_v2.run_animejanai_with_keybinding(clip, video_in_dw, video_in_dh, container_fps, keybinding)