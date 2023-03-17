import sys, os, pathlib
import vapoursynth as vs

sys.path.append(str(pathlib.Path().absolute()))

import animejanai_v2

# Instructions for running this encoding script tool
# 1. First time setup, open a command window in your main mpv directory and run:
#     .\python.exe .\vsrepo.py -p update
#     .\python.exe .\vsrepo.py install ffms2
# 2. Edit the path of the source video below, from ./video.mkv to the path of 
#    the video you want to encode an upscale for
# 3. Set the slot below, to a value between 1-9 to select the slot, configured in animejanai_v2.conf,
#    which sets up the upscaling settings for your encode
# 4. Run the following command from the main mpv directory (adjust the ffmpeg arguments as needed, change upscaled.mkv
     to the output filename you want):
#     .\VSPipe.exe -c y4m ./portable_config/shaders/animejanai_v2_encode.vpy - | ffmpeg -i pipe: -c:v libx265 -crf 16 -preset slow -x265-params "sao=0:bframes=8:psy-rd=1.5:psy-rdoq=2:aq-mode=3:ref=6" upscaled.mkv

clip = vs.core.ffms2.Source(source=r"./video.mkv")
keybinding = 1 

animejanai_v2.run_animejanai_with_keybinding(clip, keybinding)