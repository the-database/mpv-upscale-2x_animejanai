import vapoursynth as vs
import os

SD_ENGINE_NAME = "Compact"
HD_ENGINE_NAME = "UltraCompact"

core = vs.core
core.num_threads = 4  # can influence ram usage
colorspace="709"


def scaleTo1080(clip, w=1920, h=1080):
   if clip.width / clip.height > 16 / 9:
      prescalewidth = w
      prescaleheight = w * clip.height / clip.width
   else:
      prescalewidth = h * clip.width / clip.height
      prescaleheight = h
   return vs.core.resize.Bicubic(clip, width=prescalewidth, height=prescaleheight)


def upscale2x(clip):
   engine_name = SD_ENGINE_NAME if clip.height < 720 else HD_ENGINE_NAME
   return core.trt.Model(
      clip,
      engine_path=f"C:\\mpv.net\\vapoursynth64\\plugins\\vsmlrt-cuda\\{engine_name}.engine",
      num_streams=4,
   )


clip = video_in

if clip.height < 720:
   colorspace = "170m"

clip = vs.core.resize.Bicubic(clip, format=vs.RGBS, matrix_in_s=colorspace,
   # width=clip.width/2.25,height=clip.height/2.25 # pre-downscale
   )

# pre-scale 720p or higher to 1080
if clip.height >= 720 or clip.width >= 1280:
   clip = scaleTo1080(clip)

# upscale 2x
clip = upscale2x(clip)

# upscale 2x again if necessary
if clip.height < 2160 and clip.width < 3840:

   # downscale down to 1080 if first 2x went over 1080
   if clip.height > 1080 or clip.width > 1920:
      clip = scaleTo1080(clip)

   # upscale 2x again
   clip = upscale2x(clip)


clip = vs.core.resize.Bicubic(clip, format=vs.YUV420P8, matrix_s=colorspace)

clip.set_output()
