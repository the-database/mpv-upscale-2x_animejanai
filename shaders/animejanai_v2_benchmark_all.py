import os, subprocess, sys, re, pathlib

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import animejanai_v2_config
import time

table = {}


def get_engine(conf, height):
    model = conf['sd_model'] if height < 720 else conf['hd_model']
    m = re.search(r'_([a-zA-Z]*Compact)[_-]', model)
    return f'2x_{m.group(1)}' if m is not None else model


def printtable(table):
    with open('benchmark.txt', 'w') as f:
        columns = ['480x360', '640x480', '768x576', '1280x720', '1920x1080']
        keys = ['(2x_Compact)',
                '(2x_UltraCompact)',
                '(2x_SuperUltraCompact)',
                '(2x_Compact+2x_Compact)',
                '(2x_Compact+2x_UltraCompact)',
                '(2x_Compact+2x_SuperUltraCompact)',
                '(2x_UltraCompact+2x_SuperUltraCompact)',
                '(2x_UltraCompact+2x_UltraCompact)',
                '(2x_SuperUltraCompact+2x_SuperUltraCompact)']

        f.write('||' + '|'.join(columns) + '|\n')
        f.write('|-|' + '|'.join(['-' for _ in columns]) + '|\n')
        for key in keys:
            value = table[key]
            newrow = []
            for col in columns:
                try:
                    newrow.append(value[col][4])
                except KeyError:
                    newrow.append('')
            f.write('|'+('4x ' if '+' in key else '2x ')+key+'|'+'|'.join(newrow)+'\n')


slots = range(10, 19)
mpv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), r"..\..")
config = animejanai_v2_config.read_config()

start = time.time()
for filename in os.listdir('./benchmarks'):
    if not filename.endswith('.ffindex'):
        for slot in slots:
            conf = config[f'slot_{slot}']
            if conf['upscale_4x'] and filename.startswith('1920x1080'):
                continue

            basename = pathlib.Path(filename).stem
            resolution = basename.split('x')
            height = int(resolution[1])
            key = f"({get_engine(conf, height)}{'+' + get_engine(conf, height * 2) if conf['upscale_4x'] else ''})"
            scale = '4x' if conf['upscale_4x'] else '2x'

            if key not in table:
                table[key] = {}

            if basename in table[key]:
                continue

            p = subprocess.run([os.path.join(mpv_path, "vspipe.exe"), "--arg", f"video_path=benchmarks\\{filename}",
                                "--arg", f"slot={slot}", "--start", "0", "--end", "500",
                                "./portable_config/shaders/animejanai_v2_benchmark.vpy",
                                "-p", "."], cwd=mpv_path, capture_output=True)
            # Output x frames in y seconds (z fps)
            outputline = p.stderr.decode().splitlines()[-1]
            resultfps = re.search(r'\((.+)\)', outputline).group(1)

            print(basename, scale, key, resultfps)

            table[key][basename] = [basename, scale, height, key, resultfps]

end = time.time()
print(f'Completed in {end - start:.2f} seconds.')

printtable(table)