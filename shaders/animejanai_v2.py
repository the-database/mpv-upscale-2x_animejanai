import vapoursynth as vs
import os
import subprocess
import logging
import configparser
import itertools
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import rife_cuda

# trtexec num_streams
TOTAL_NUM_STREAMS = 4

core = vs.core
core.num_threads = 4  # can influence ram usage

plugin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           r"..\..\vapoursynth64\plugins\vsmlrt-cuda")

formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('animejanai_v2')

config = {}


def init_logger():
    global logger
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'animejanai_v2.log'))
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)


def read_config():
    dummy_key = 'config'
    slots_range = range(1, 10)
    bools = {
        'logging',
        *{f'upscale_4x_{i}' for i in slots_range},
        *{f'resize_720_to_1080_before_first_2x_{i}' for i in slots_range},
        *{f'upscale_2x_{i}' for i in slots_range},
        *{f'resize_to_1080_before_second_2x_{i}' for i in slots_range},
        *{f'rife_{i}' for i in slots_range}
    }
    floats = {
        *{f'resize_factor_before_first_2x_{i}' for i in slots_range},
        *{f'resize_height_before_first_2x_{i}' for i in slots_range}
    }

    parser = configparser.ConfigParser()
    conf = {}
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "./animejanai_v2.conf")) as lines:
        lines = itertools.chain((f"[{dummy_key}]",), lines)
        parser.read_file(lines)

    for key in parser[dummy_key]:
        if key in bools:
            conf[key] = True if parser[dummy_key][key].casefold() == 'yes'.casefold() else False
        elif key in floats:
            conf[key] = float(parser[dummy_key][key])
        else:
            conf[key] = parser[dummy_key][key]

    return conf


# model_type: HD or SD
# binding: 1 through 9
def find_model(model_type, binding):
    key = f'{model_type.lower()}_model_{binding}'
    if key in config:
        return config[key]
    return None


def create_engine(onnx_name):
    onnx_path = os.path.join(plugin_path, f"{onnx_name}.onnx")
    if not os.path.isfile(onnx_path):
        raise FileNotFoundError(onnx_path)

    subprocess.run([os.path.join(plugin_path, "trtexec"), "--fp16", f"--onnx={onnx_name}.onnx",
                    "--minShapes=input:1x3x8x8", "--optShapes=input:1x3x1080x1920", "--maxShapes=input:1x3x1080x1920",
                    f"--saveEngine={onnx_name}.engine", "--tacticSources=+CUDNN,-CUBLAS,-CUBLAS_LT"],
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
    engine_path = os.path.join(plugin_path, f"{engine_name}.engine")

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


def run_animejanai(clip, container_fps, sd_engine_name, hd_engine_name, resize_factor_before_first_2x,
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

        clip = vs.core.resize.Bicubic(clip, format=vs.RGBS, matrix_in_s=colorspace,
                                      width=clip.width/resize_factor_before_first_2x,
                                      height=clip.height/resize_factor_before_first_2x)

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

        clip = vs.core.resize.Bicubic(clip, format=fmt_out, matrix_s=colorspace, range=1 if colorlv == 0 else None)

    if use_rife:
        clip = rife_cuda.rife(clip, clip.width, clip.height, container_fps)

    clip.set_output()


# keybinding: 1-9
def run_animejanai_with_keybinding(clip, container_fps, keybinding):
    sd_engine_name = find_model("SD", keybinding)
    hd_engine_name = find_model("HD", keybinding)
    do_upscale = config.get(f'upscale_2x_{keybinding}', True)
    upscale_twice = config.get(f'upscale_4x_{keybinding}', True)
    use_rife = config.get(f'rife_{keybinding}', False)
    resize_720_to_1080_before_first_2x = config.get(f'resize_720_to_1080_before_first_2x_{keybinding}', True)
    resize_factor_before_first_2x = config.get(f'resize_factor_before_first_2x_{keybinding}', 1)
    resize_height_before_first_2x = config.get(f'resize_height_before_first_2x_{keybinding}', 0)
    resize_to_1080_before_second_2x = config.get(f'resize_to_1080_before_second_2x_{keybinding}', True)

    if do_upscale:
        if sd_engine_name is None:
            raise FileNotFoundError(
                f"No SD model found for keybinding ctrl+{keybinding}. Expected to find an onnx model with filename containing 'SD-{keybinding}' in the following path: {plugin_path}")

        if hd_engine_name is None:
            raise FileNotFoundError(
                f"No HD model found for keybinding ctrl+{keybinding}. Expected to find an onnx model with filename containing 'HD-{keybinding}' in the following path: {plugin_path}")

    run_animejanai(clip, container_fps, sd_engine_name, hd_engine_name, resize_factor_before_first_2x,
                   resize_height_before_first_2x, resize_720_to_1080_before_first_2x, do_upscale,
                   resize_to_1080_before_second_2x, upscale_twice, use_rife)


def init():
    global config
    config = read_config()
    if config['logging']:
        init_logger()


init()
