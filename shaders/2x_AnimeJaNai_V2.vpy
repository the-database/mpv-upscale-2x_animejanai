import vapoursynth as vs
import os, subprocess

SD_ENGINE_NAME = "2x_AnimeJaNai_V1.13_Compact_net_g_27200"
HD_ENGINE_NAME = SD_ENGINE_NAME

core = vs.core
core.num_threads = 4  # can influence ram usage
colorspace="709"

plugin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
   "..\\..\\vapoursynth64\\plugins\\vsmlrt-cuda")


def createEngine(onnx_name):
   onnx_path = os.path.join(plugin_path, f"{onnx_name}.onnx")
   if not os.path.isfile(onnx_path):
      raise FileNotFoundError(onnx_path)

   subprocess.run([os.path.join(plugin_path, "trtexec"), "--fp16", f"--onnx={onnx_name}.onnx",
      "--minShapes=input:1x3x8x8", "--optShapes=input:1x3x1080x1920", "--maxShapes=input:1x3x1080x1920",
      f"--saveEngine={onnx_name}.engine", "--tacticSources=+CUDNN,-CUBLAS,-CUBLAS_LT"], 
      cwd=plugin_path)


def scaleTo1080(clip, w=1920, h=1080):
   if clip.width / clip.height > 16 / 9:
      prescalewidth = w
      prescaleheight = w * clip.height / clip.width
   else:
      prescalewidth = h * clip.width / clip.height
      prescaleheight = h
   return vs.core.resize.Bicubic(clip, width=prescalewidth, height=prescaleheight)


def upscale2x(clip, num_streams=2):
   engine_name = SD_ENGINE_NAME if clip.height < 720 else HD_ENGINE_NAME
   engine_path = os.path.join(plugin_path, f"{engine_name}.engine")

   if not os.path.isfile(engine_path):
      createEngine(engine_name)

   return core.trt.Model(
      clip,
      engine_path=engine_path,
      num_streams=num_streams,
   )


clip = video_in
colorlv = clip.get_frame(0).props._ColorRange
fmt_in = input.format.id

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

   # add slight blur before second upscale, since model expects slight blur
   # this helps prevent oversharpening when upscaling twice
   clip = core.std.BoxBlur(clip)
   clip = core.std.BoxBlur(clip)

   # upscale 2x again
   clip = upscale2x(clip)

fmt_out = fmt_in
if fmt_in not in [vs.YUV410P8, vs.YUV411P8, vs.YUV420P8, vs.YUV422P8, vs.YUV444P8, vs.YUV420P10, vs.YUV422P10, vs.YUV444P10] :
   fmt_out = vs.YUV420P10

clip = vs.core.resize.Bicubic(clip, format=fmt_out, matrix_s=colorspace, range=1 if colorlv==0 else None)
clip.set_output()
