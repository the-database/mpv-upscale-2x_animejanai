import vapoursynth as vs
import os
import subprocess
import logging
import configparser
import sys
from logging.handlers import RotatingFileHandler

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import rife_cuda
import animejanai_v2_config
# import gmfss_cuda

# trtexec num_streams
TOTAL_NUM_STREAMS = 4

core = vs.core
core.num_threads = 4  # can influence ram usage

plugin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           r"..\..\vapoursynth64\plugins\vsmlrt-cuda")
model_path = os.path.join(plugin_path, r"..\models\animejanai")

formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('animejanai_v2')

config = {}


def init_logger():
    global logger
    logger.setLevel(logging.DEBUG)
    rfh = RotatingFileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'animejanai_v2.log'),
                              mode='a', maxBytes=1 * 1024 * 1024, backupCount=2, encoding=None, delay=0)
    rfh.setFormatter(formatter)
    rfh.setLevel(logging.DEBUG)
    logger.addHandler(rfh)


# model_type: HD or SD
# binding: 1 through 9
def find_model(model_type, binding):
    section_key = f'slot_{binding}'
    key = f'{model_type.lower()}_model'

    if section_key in config:
        if key in config[section_key]:
            return config[section_key][key]
    return None


def create_engine(onnx_name):
    onnx_path = os.path.join(model_path, f"{onnx_name}.onnx")
    if not os.path.isfile(onnx_path):
        raise FileNotFoundError(onnx_path)

    engine_path = os.path.join(model_path, f"{onnx_name}.engine")

    subprocess.run([os.path.join(plugin_path, "trtexec"), "--fp16", f"--onnx={onnx_path}",
                    "--minShapes=input:1x3x8x8", "--optShapes=input:1x3x1080x1920", "--maxShapes=input:1x3x1080x1920",
                    f"--saveEngine={engine_path}", "--tacticSources=+CUDNN,-CUBLAS,-CUBLAS_LT"],
                   cwd=plugin_path)


def scale_to_1080(clip, w=1920, h=1080):
    if clip.width / clip.height > 16 / 9:
        prescalewidth = w
        prescaleheight = w * clip.height / clip.width
    else:
        prescalewidth = h * clip.width / clip.height
        prescaleheight = h
    return vs.core.resize.Bicubic(clip, width=prescalewidth, height=prescaleheight)


def upscale2x(clip, sd_engine_name, hd_engine_name, num_streams):
    engine_name = sd_engine_name if clip.height < 720 else hd_engine_name
    if engine_name is None:
        return clip
    engine_path = os.path.join(model_path, f"{engine_name}.engine")

    message = f"upscale2x: scaling 2x from {clip.width}x{clip.height} with engine={engine_name}; num_streams={num_streams}"
    logger.debug(message)
    print(message)

    if not os.path.isfile(engine_path):
        create_engine(engine_name)

    return core.trt.Model(
        clip,
        engine_path=engine_path,
        num_streams=num_streams,
    )


def run_animejanai(clip, sd_engine_name, hd_engine_name, resize_factor_before_first_2x,
                   resize_height_before_first_2x, resize_720_to_1080_before_first_2x, do_upscale,
                   resize_to_1080_before_second_2x, upscale_twice, use_rife):
    if do_upscale:
        colorspace = "709"
        colorlv = clip.get_frame(0).props._ColorRange
        fmt_in = clip.format.id

        if clip.height < 720:
            colorspace = "170m"

        if resize_height_before_first_2x != 0:
            resize_factor_before_first_2x = 1

        try:
            # try half precision first
            clip = vs.core.resize.Bicubic(clip, format=vs.RGBH, matrix_in_s=colorspace,
                                          width=clip.width/resize_factor_before_first_2x,
                                          height=clip.height/resize_factor_before_first_2x)

            clip = run_animejanai_upscale(clip, sd_engine_name, hd_engine_name, resize_factor_before_first_2x,
                                          resize_height_before_first_2x, resize_720_to_1080_before_first_2x, do_upscale,
                                          resize_to_1080_before_second_2x, upscale_twice, use_rife, colorspace, colorlv,
                                          fmt_in)
        except:
            clip = vs.core.resize.Bicubic(clip, format=vs.RGBS, matrix_in_s=colorspace,
                                          width=clip.width/resize_factor_before_first_2x,
                                          height=clip.height/resize_factor_before_first_2x)
            clip = run_animejanai_upscale(clip, sd_engine_name, hd_engine_name, resize_factor_before_first_2x,
                                          resize_height_before_first_2x, resize_720_to_1080_before_first_2x, do_upscale,
                                          resize_to_1080_before_second_2x, upscale_twice, use_rife, colorspace, colorlv,
                                          fmt_in)

    if use_rife:
        clip = rife_cuda.rife(clip, clip.width, clip.height, clip.fps)

    clip.set_output()


def run_animejanai_upscale(clip, sd_engine_name, hd_engine_name, resize_factor_before_first_2x,
                          resize_height_before_first_2x, resize_720_to_1080_before_first_2x, do_upscale,
                          resize_to_1080_before_second_2x, upscale_twice, use_rife, colorspace, colorlv, fmt_in):

    if resize_height_before_first_2x != 0:
        clip = scale_to_1080(clip, resize_height_before_first_2x * 16 / 9, resize_height_before_first_2x)

    # pre-scale 720p or higher to 1080
    if resize_720_to_1080_before_first_2x:
        if (clip.height >= 720 or clip.width >= 1280) and clip.height < 1080 and clip.width < 1920:
            clip = scale_to_1080(clip)

    upscale_twice = upscale_twice and clip.height < 1080 and clip.width < 1920
    num_streams = TOTAL_NUM_STREAMS
    if upscale_twice:
        num_streams /= 2

    # upscale 2x
    clip = upscale2x(clip, sd_engine_name, hd_engine_name, num_streams)

    # upscale 2x again if necessary
    if upscale_twice:
        # downscale down to 1080 if first 2x went over 1080,
        # or scale up to 1080 if enabled
        if resize_to_1080_before_second_2x or clip.height > 1080 or clip.width > 1920:
            clip = scale_to_1080(clip)

        # upscale 2x again
        clip = upscale2x(clip, sd_engine_name, hd_engine_name, num_streams)

    fmt_out = fmt_in
    if fmt_in not in [vs.YUV410P8, vs.YUV411P8, vs.YUV420P8, vs.YUV422P8, vs.YUV444P8, vs.YUV420P10, vs.YUV422P10,
                      vs.YUV444P10]:
        fmt_out = vs.YUV420P10

    return vs.core.resize.Bicubic(clip, format=fmt_out, matrix_s=colorspace, range=1 if colorlv == 0 else None)

# keybinding: 1-9
def run_animejanai_with_keybinding(clip, keybinding):
    sd_engine_name = find_model("SD", keybinding)
    hd_engine_name = find_model("HD", keybinding)
    section_key = f'slot_{keybinding}'
    do_upscale = config[section_key].get(f'upscale_2x', True)
    upscale_twice = config[section_key].get(f'upscale_4x', True)
    use_rife = config[section_key].get(f'rife', False)
    resize_720_to_1080_before_first_2x = config[section_key].get(f'resize_720_to_1080_before_first_2x', True)
    resize_factor_before_first_2x = config[section_key].get(f'resize_factor_before_first_2x', 1)
    resize_height_before_first_2x = config[section_key].get(f'resize_height_before_first_2x', 0)
    resize_to_1080_before_second_2x = config[section_key].get(f'resize_to_1080_before_second_2x', True)

    if do_upscale:
        if sd_engine_name is None and hd_engine_name is None:
            raise FileNotFoundError(
                f"2x upscaling is enabled but no SD model and HD model defined for slot {keybinding}. Expected at least one of SD or HD model to be specified with sd_model or hd_model in animejanai.conf.")

    run_animejanai(clip, sd_engine_name, hd_engine_name, resize_factor_before_first_2x,
                   resize_height_before_first_2x, resize_720_to_1080_before_first_2x, do_upscale,
                   resize_to_1080_before_second_2x, upscale_twice, use_rife)


def init():
    global config
    config = animejanai_v2_config.read_config()
    if config['global']['logging']:
        init_logger()


init()
