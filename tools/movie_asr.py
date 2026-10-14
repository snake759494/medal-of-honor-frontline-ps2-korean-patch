"""동영상 영어 음성 받아쓰기(faster-whisper large-v3) -> movie/asr/<이름>.json [[start, end, text], ...]

python tools/movie_asr.py [이름 ...]   (기본: 음성이 있는 전 동영상)
"""
import os, sys, json, subprocess
import numpy as np
import imageio_ffmpeg
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ext, mpc

ROOT = os.path.join(HERE, '..')
M = os.path.join(ROOT, 'movie')
FF = imageio_ffmpeg.get_ffmpeg_exe()
NAMES = ['INTRO', 'BRIEF11', 'BRIEF21', 'BRIEF31', 'BRIEF41', 'BRIEF51', 'HISTORY1', 'HISTORY2', 'HISTORY3',
         'HISTORY4', 'HISTORY5', 'HISTORY6', 'MAKING1', 'MAKING2', 'MAKING3', 'MAKING4', 'MAKING5', 'MAKING6',
         'EXTRAS1', 'EXTRAS2', 'EXTRAS3', 'EXTRAS5', 'EXTRAS4', 'DEMO', 'FDEMO']


def load16k(name):
    ea = mpc.audio(ext.get(f'DATA/MOVIES/{name}.MPC'))
    r = subprocess.run([FF, '-v', 'error', '-f', 'ea', '-i', '-', '-ac', '1', '-ar', '16000', '-f', 's16le', '-'],
                       input=ea, capture_output=True)
    return np.frombuffer(r.stdout, np.int16).astype(np.float32) / 32768


def main(names):
    from faster_whisper import WhisperModel
    model = WhisperModel('large-v3', device='cpu', compute_type='int8')
    os.makedirs(os.path.join(M, 'asr'), exist_ok=True)
    for name in names:
        out = os.path.join(M, 'asr', name + '.json')
        if os.path.exists(out): continue
        segs, _ = model.transcribe(load16k(name), language='en', beam_size=5, vad_filter=True,
                                  condition_on_previous_text=False)
        res = [[round(s.start, 2), round(s.end, 2), s.text.strip()] for s in segs]
        json.dump(res, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        print(name, len(res), flush=True)


if __name__ == '__main__':
    main(sys.argv[1:] or NAMES)
