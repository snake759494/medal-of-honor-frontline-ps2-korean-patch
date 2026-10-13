"""이미지 속 영문 -> 한글: 글자 검출, 인페인팅, 한글 렌더, 원 팔레트 양자화"""
import os, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ssh
ROOT = os.path.join(HERE, '..')
FONTS = {k: os.path.join(ROOT, v) for k, v in {
    'sans': 'NanumSquareNeo-cBd.ttf', 'sansEB': 'NanumSquareNeo-dEb.ttf', 'sansH': 'NanumSquareNeo-eHv.ttf',
    'serif': 'SeoulHangangB.ttf', 'serifEB': 'SeoulHangangEB.ttf'}.items()}


def text_mask(rgb, box, mode, thr):
    x0, y0, x1, y1 = box
    g = rgb[..., :3].astype(np.int32).mean(-1)
    m = np.zeros(g.shape, np.uint8)
    sub = g[y0:y1, x0:x1]
    if mode == 'red':
        r = rgb[y0:y1, x0:x1, :3].astype(np.int32); m[y0:y1, x0:x1] = (r[..., 0] - r[..., 1]) > thr
    else:
        m[y0:y1, x0:x1] = (sub > thr) if mode == 'bright' else (sub < thr)
    return m


def fit_font(face, lines, w, h, maxpx, spacing=0.15):
    for px in range(maxpx, 6, -1):
        f = ImageFont.truetype(FONTS[face], px)
        ws = [f.getbbox(l)[2] - f.getbbox(l)[0] for l in lines]
        lh = px * (1 + spacing)
        if max(ws) <= w and lh * len(lines) <= h + px * spacing: return f, px
    return ImageFont.truetype(FONTS[face], 7), 7


def render(rgba, spec):
    """spec: dict(box, text(\n 줄바꿈), mode bright|dark, thr, face, color, shadow, maxpx, dil, tbox, angle)"""
    a = rgba.copy()
    box = spec['box']
    if spec.get('auto'):
        m = text_mask(a, box, spec.get('mode', 'bright'), spec.get('thr', 128))
        ys, xs = np.where(m)
        if len(xs):
            box = [int(xs.min()) - 2, int(ys.min()) - 2, int(xs.max()) + 3, int(ys.max()) + 3]
            spec = dict(spec, tbox=[box[0] - 12, box[1] - 1, box[2] + 2, box[3] + 1])
    if spec.get('fill') is not None:
        x0, y0, x1, y1 = box
        a[y0:y1, x0:x1, :3] = spec['fill']
    else:
        if spec.get('maskall'):
            m = np.zeros(a.shape[:2], np.uint8); x0, y0, x1, y1 = box; m[y0:y1, x0:x1] = 1
        else:
            m = text_mask(a, box, spec.get('mode', 'bright'), spec.get('thr', 128))
        m = cv2.dilate(m, np.ones((3, 3), np.uint8), iterations=spec.get('dil', 2))
        bgr = cv2.inpaint(np.ascontiguousarray(a[..., :3]), m * 255, 5, cv2.INPAINT_TELEA)
        a[..., :3] = bgr
    tb = spec.get('tbox', box)
    Hh, Ww = a.shape[:2]
    x0, y0, x1, y1 = max(0, tb[0]), max(0, tb[1]), min(Ww, tb[2]), min(Hh, tb[3])
    W, H = x1 - x0, y1 - y0
    lines = spec['text'].split('\n')
    f, px = fit_font(spec.get('face', 'sans'), lines, W, H, spec.get('maxpx', H))
    layer = Image.new('RGBA', (W * 3, H * 3), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    lh = px * 1.15
    ty = W * 0 + H + (H - lh * len(lines)) / 2 + px * 0.05
    col = tuple(spec.get('color', (255, 255, 255)))
    for i, l in enumerate(lines):
        bb = f.getbbox(l); tw = bb[2] - bb[0]
        tx = W + (W - tw) / 2 - bb[0]
        y = ty + i * lh - f.getbbox('한')[1] + (lh - (f.getbbox('한')[3] - f.getbbox('한')[1])) / 2 - px * 0.08
        if spec.get('shadow'):
            sc = tuple(spec['shadow'][:3]) + (200,); off = spec.get('shoff', 1)
            d.text((tx + off, y + off), l, font=f, fill=sc)
        d.text((tx, y), l, font=f, fill=col + (255,))
    if spec.get('angle'):
        layer = layer.rotate(spec['angle'], resample=Image.BICUBIC, center=(W * 1.5, H * 1.5))
    layer = layer.crop((W, H, W * 2, H * 2))
    L = np.array(layer).astype(np.float32) / 255
    al = L[..., 3:4]
    reg = a[y0:y1, x0:x1, :3].astype(np.float32)
    a[y0:y1, x0:x1, :3] = (reg * (1 - al) + L[..., :3] * 255 * al).astype(np.uint8)
    return a


def quantize(rgb, pal):
    """rgb(H,W,3) -> 팔레트 색인 (알파는 원래 색인의 알파 유지 위해 같은 알파 군에서만 고름)"""
    P = pal[:, :3].astype(np.int32)
    flat = rgb.reshape(-1, 3).astype(np.int32)
    out = np.empty(len(flat), np.int64)
    for s in range(0, len(flat), 4096):
        d = ((flat[s:s + 4096, None, :] - P[None]) ** 2).sum(-1)
        out[s:s + 4096] = d.argmin(1)
    return out.reshape(rgb.shape[:2])


def apply(data, specs, idx=0):
    ims = ssh.parse(data); im = ims[idx]
    rgba = ssh.to_rgba(im)
    a = rgba.copy()
    for sp in specs: a = render(a, sp)
    if im.type == 5:
        return ssh.write(data, im, a), a
    # 원래 불투명 영역만 바꿈, 알파 0x80 인 팔레트 색만 후보
    pal = im.pal
    opaque = np.where(pal[:, 3] >= 0x70)[0]
    q = quantize(a[..., :3], pal[opaque])
    new = opaque[q]
    changed = (a[..., :3] != rgba[..., :3]).any(-1)
    idxs = im.idx.copy(); idxs[changed] = new[changed]
    return ssh.write(data, im, idxs), pal[idxs]


def preview(rgba, path):
    a = rgba.astype(np.int32); al = np.clip(a[..., 3] * 2, 0, 255)[..., None] / 255
    Image.fromarray((a[..., :3] * al + 60 * (1 - al)).astype(np.uint8)).save(path)
