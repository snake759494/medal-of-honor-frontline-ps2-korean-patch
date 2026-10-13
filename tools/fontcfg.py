"""폰트별 한글 서체·크기 설정"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import sfn as sfnmod, kfont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
T = lambda n: os.path.join(ROOT, n)
SANS_R = T('NanumSquareNeo-bRg.ttf')
SANS_B = T('NanumSquareNeo-cBd.ttf')
SANS_EB = T('NanumSquareNeo-dEb.ttf')
SERIF_M = T('SeoulHangangM.ttf')
SERIF_B = T('SeoulHangangB.ttf')
SERIF_EB = T('SeoulHangangEB.ttf')

# 원본 서체: Garamond 계열(세리프) -> 서울한강체, 고딕 계열 -> 나눔스퀘어 네오
FACE = {
    'CustomController.sfn': SERIF_B, 'CustomControllerLarge.sfn': SERIF_B,
    'Difficulty_.sfn': SERIF_B, 'JournalFont.sfn': SERIF_B, 'Medals.sfn': SERIF_EB,
    'MissionLogFont.sfn': SERIF_B, 'MissionLogMsnName.sfn': SERIF_B,
    'MissionLogRatingInfo.sfn': SERIF_B, 'PlayerStatsFont.sfn': SERIF_B,
    'SaveContReplay.sfn': SERIF_B, 'SaveLoadFont.sfn': SERIF_B,
    'SecretCodesFont_Garamond18.sfn': SERIF_B, 'unpluggedFont.sfn': SERIF_B,
    'DDayIntro.sfn': SERIF_B, 'PauseScreenFont.sfn': SERIF_B,
    'PopupDisplay.sfn': SANS_B, 'configMovement.sfn': SANS_B, 'configFont.sfn': SANS_B,
    'memorycardFont.sfn': SANS_B, 'objFont.sfn': SANS_B, 'subtitleFont.sfn': SANS_B,
    'debugFont.sfn': SANS_R, 'comicFont.sfn': SANS_B,
    'LANGFONT.SFN': SANS_B, 'OBJFONT.SFN': SANS_B,
}
SCALE = {'objFont.sfn': 1.3, 'subtitleFont.sfn': 1.3, 'OBJFONT.SFN': 1.3}
STYLE = {'objFont.sfn': 'bin', 'subtitleFont.sfn': 'bin', 'memorycardFont.sfn': 'bin', 'OBJFONT.SFN': 'bin', 'comicFont.sfn': 'comic'}   # 이름별 한글 높이 배율(대문자 높이 대비)


def metrics(raw):
    f = sfnmod.SFN(raw)
    H = [g for g in f.glyphs if g[0] == ord('H')][0]
    return f, H[2], H[7]          # cap height, cap top(yo)


_px_cache = {}


def pick_px(ttf, target_h):
    key = (ttf, target_h)
    if key in _px_cache: return _px_cache[key]
    best = None
    for px in range(6, 80):
        fnt = ImageFont.truetype(ttf, px)
        b = fnt.getbbox('한', anchor='ls')
        h = b[3] - b[1]
        if best is None or abs(h - target_h) < abs(best[1] - target_h):
            best = (px, h)
    _px_cache[key] = best[0]
    return best[0]


def build_font(name, raw, chars, tex_w=None):
    """chars: [(idx, ch)]"""
    f, cap, top = metrics(raw)
    ttf = FACE[name]
    sc = SCALE.get(name, 1.12)
    target = max(7, round(cap * sc))
    px = pick_px(ttf, target)
    fnt = ImageFont.truetype(ttf, px)
    # 기준선: 원본 대문자 바닥. 한글은 기준선 아래로 약간 내려옴
    asc = -fnt.getbbox('한', anchor='ls')[1]
    desc = max(fnt.getbbox('한글', anchor='ls')[3], 0)
    base = asc + 1
    cell_h = asc + desc + 2
    baseline = top + cap
    cell_top = baseline - base + max(0, round((target - cap) * 0.35))
    spacing = 1 if cap < 20 else 2
    return kfont.build(raw, chars, ttf, px, cell_top, cell_h, base, spacing=spacing, tex_w=tex_w, style=STYLE.get(name))
