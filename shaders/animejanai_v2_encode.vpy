import sys, os, pathlib
import vapoursynth as vs

sys.path.append(str(pathlib.Path().absolute()))

import animejanai_v2

# Instructions for running this encoding script tool
# 1. Run the following command from the main mpv directory (adjust the ffmpeg arguments as needed). 
#    Make sure to update the video_path to the input path of your video, the output path where you 
#    want to output the video, and set the slot to a value between 1-9 to select the upscaling slot
#    which is configured in animejanai_v2.conf:
#     .\VSPipe.exe -c y4m --arg "slot=1" --arg "video_path=/path/to/input/video.mkv" ./portable_config/shaders/animejanai_v2_encode.vpy - | ffmpeg -i pipe: -c:v libx265 -crf 16 -preset slow -x265-params "sao=0:bframes=8:psy-rd=1.5:psy-rdoq=2:aq-mode=3:ref=6" /path/to/output/video.mkv

args = dict(globals())

required_args = {'video_path', 'slot'}

args = dict(globals())

for arg in required_args:
    if arg not in args:
        raise ValueError(f"{arg} must be defined in globals")
        sys.exit(1)

clip = vs.core.ffms2.Source(source=args["video_path"])
slot = int(args["slot"])
animejanai_v2.run_animejanai_with_keybinding(clip, clip.fps, slot)