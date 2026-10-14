"""MPC 동영상에 한국어 자막을 입힌다(블랙 한글패치 movie_sub.py 방식).

python tools/movie_sub.py [이름 ...]    자막 translation/movies/<이름>.tsv -> movie/enc/<이름>.MPC

원본 영상: MPEG-2 640x448 29.97fps 프로그레시브, 시퀀스 헤더는 맨 앞 한 번, 닫힌 GOP 15장(I B B P ...).
방법: 자막이 걸린 GOP가 이어지는 구간만 디코드 -> 자막 합성 -> 같은 구조로 재인코딩해 원래 GOP 자리에 끼운다.
      재인코딩 결과의 시퀀스 헤더는 버리고 GOP(0xB8)부터만 쓴다. 구간마다 고정 q를 낮은 값부터 시도해
      원본 구간 바이트 이하인 가장 고운 q를 쓰고, 남는 바이트는 0으로 채운다(시작 코드 앞 0 채움은 허용).
      영상 ES 길이가 원본과 같으므로 MPCh 청크 크기·오디오 청크 배치를 그대로 유지한다.
자막: 게임 자막과 같은 나눔스퀘어 네오 ExtraBold, 흰 글자 + 검은 외곽선, 화면 아래 가운데(블랙 한글패치와 같은 형식).
tsv: 시작초 <TAB> 끝초 <TAB> 한국어(줄바꿈은 \\n)
"""
import os, sys, subprocess
import numpy as np
import av
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ext, mpc

ROOT = os.path.join(HERE, '..')
M = os.path.join(ROOT, 'movie')
SUBS = os.path.join(ROOT, 'translation', 'movies')
FONT = os.path.join(ROOT, 'NanumSquareNeo-dEb.ttf')
W, H = 640, 448
SIZE = 20
STROKE = 2
LINE_H = 24
BOTTOM = H - 34
MAXW = 600
FPS = 30000 / 1001
Q_STEPS = [2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 17, 20, 24, 28, 31]
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
_font = ImageFont.truetype(FONT, SIZE)


def wrap(text):
    out = []
    for para in text.split('\\n'):
        words, cur = para.split(' '), ''
        for w in words:
            t = (cur + ' ' + w).strip()
            if _font.getlength(t) > MAXW and cur:
                out.append(cur); cur = w
            else:
                cur = t
        out.append(cur)
    return out


def render(text):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lines = wrap(text)
    y = BOTTOM - LINE_H * len(lines)
    for ln in lines:
        d.text((W // 2, y + LINE_H / 2), ln, font=_font, anchor='mm', fill=(255, 255, 255, 255),
               stroke_width=STROKE, stroke_fill=(0, 0, 0, 255))
        y += LINE_H
    return im


def load_subs(name):
    p = os.path.join(SUBS, name + '.tsv')
    subs = []
    for ln in open(p, encoding='utf8').read().splitlines():
        if ln.strip() and not ln.startswith('#'):
            s, e, t = ln.split('\t', 2)
            s, e = float(s), float(e)
            e = min(e, s + max(3.0, 1.0 + 0.16 * len(t)))   # 긴 침묵 구간에 자막이 오래 남지 않게
            subs.append((s, e, t))
    return subs


def split_gops(es):
    starts, i = [], 0
    while True:
        i = es.find(b'\x00\x00\x01\xb8', i)
        if i < 0: break
        starts.append(i); i += 4
    end = len(es) - 4 if es.endswith(b'\x00\x00\x01\xb7') else len(es)
    return [(s, (starts[k + 1] if k + 1 < len(starts) else end)) for k, s in enumerate(starts)]


def gop_frames(es, gops):
    return [es.count(b'\x00\x00\x01\x00', a, b) for a, b in gops]


def _enc1(frames, q):
    """한 GOP(닫힌 GOP) 인코딩, 고정 양자화 q. 시퀀스 헤더는 버리고 GOP 헤더부터 반환"""
    cmd = [FFMPEG, '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-s', f'{W}x{H}', '-r', '30000/1001', '-i', '-',
           '-c:v', 'mpeg2video', '-pix_fmt', 'yuv420p', '-qscale:v', str(q), '-qmin', '1', '-qmax', '31',
           '-g', '15', '-bf', '2', '-flags', '+cgop', '-sc_threshold', '1000000000',
           '-intra_vlc', '1', '-dc', '8', '-aspect', f'{W}:{H}', '-seq_disp_ext', 'never',
           '-f', 'mpeg2video', '-']
    r = subprocess.run(cmd, input=b''.join(f.tobytes() for f in frames), capture_output=True)
    if r.returncode: raise RuntimeError(r.stderr.decode())
    es = r.stdout
    if es.endswith(b'\x00\x00\x01\xb7'): es = es[:-4]
    return es[es.find(b'\x00\x00\x01\xb8'):]


def process(name):
    """MPC는 MPCh 청크 하나가 픽처 하나다(앞의 시퀀스/GOP 헤더 포함). 자막이 걸린 GOP를 GOP마다 다시 인코딩하고
    픽처 단위로 나눠 원래 청크 자리에 넣는다(청크 크기는 바뀌어도 되고 오디오 청크 배치는 그대로).
    GOP마다 원본 GOP 바이트 이하가 되는 가장 고운 q를 쓰고, 픽처 하나가 원본 최대 픽처 크기를 넘지 않게 한다."""
    data = ext.get(f'DATA/MOVIES/{name}.MPC')
    es = mpc.video(data)
    opics = mpc.split_pictures(es)
    pic_start = [0]
    for x in opics: pic_start.append(pic_start[-1] + len(x))
    maxpic = max(len(x) for x in opics)
    gops = split_gops(es)
    nf = gop_frames(es, gops)
    first = np.cumsum([0] + nf)
    total = int(first[-1])
    sub_at = [None] * total
    for s, e, t in load_subs(name):
        # 처음 두 GOP는 건드리지 않는다(재생 시작 판정 구간). 그 구간에 걸친 자막은 셋째 GOP부터 표시.
        for fi in range(max(int(first[2]), int(round(s * FPS))), min(total, int(round(e * FPS)))):
            sub_at[fi] = t
    hit = [any(sub_at[first[g]:first[g + 1]]) for g in range(len(gops))]
    todo = [g for g in range(len(gops)) if hit[g]]
    newpics = list(opics)
    cache = {}
    tmp = os.path.join(M, 'tmp_' + name + '.m2v'); os.makedirs(M, exist_ok=True)
    open(tmp, 'wb').write(es)
    c = av.open(tmp); dec = enumerate(c.decode(video=0))
    qs = []
    for g in todo:
        seg = []
        for i, fr in dec:
            if i < first[g]: continue
            img = fr.to_ndarray(format='rgb24'); t = sub_at[i]
            if t:
                if t not in cache: cache[t] = render(t)
                base = Image.fromarray(img).convert('RGBA'); base.alpha_composite(cache[t])
                img = np.asarray(base.convert('RGB'))
            seg.append(img)
            if i == first[g + 1] - 1: break
        n = nf[g]
        # 이 GOP의 원본 픽처 번호 범위(코딩 순서 = 청크 순서)
        p0 = int(first[g]); p1 = p0 + n
        budget = sum(len(x) for x in opics[p0:p1])
        enc = None
        for q in Q_STEPS:
            e = _enc1(seg, q)
            ps = mpc.split_pictures(e)
            if len(e) <= budget and max(len(x) for x in ps) <= maxpic: enc = e; break
        if enc is None: enc = e
        enc = bytearray(enc); enc[4:8] = es[gops[g][0] + 4:gops[g][0] + 8]   # GOP 헤더(타임코드)는 원본 값
        ps = mpc.split_pictures(bytes(enc))
        assert len(ps) == n, (name, g, len(ps), n)
        newpics[p0:p1] = ps
        qs.append(q)
    c.close(); os.remove(tmp)
    newmpc = mpc.rebuild(data, newpics)
    os.makedirs(os.path.join(M, 'enc'), exist_ok=True)
    open(os.path.join(M, 'enc', name + '.MPC'), 'wb').write(newmpc)
    print(name, 'gops', len(todo), 'q', (min(qs), max(qs)) if qs else None, 'size', len(data), '->', len(newmpc), flush=True)
    return newmpc


def preview(name, t, path):
    es = mpc.video(open(os.path.join(M, 'enc', name + '.MPC'), 'rb').read())
    tmp = os.path.join(M, 'tmp_prev.m2v'); open(tmp, 'wb').write(es)
    c = av.open(tmp)
    for i, fr in enumerate(c.decode(video=0)):
        if i == int(t * FPS): fr.to_image().save(path); break
    c.close(); os.remove(tmp)


if __name__ == '__main__':
    for n in sys.argv[1:]:
        process(n)
