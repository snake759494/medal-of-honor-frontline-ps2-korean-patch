import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ssh
import numpy as np, cv2


def detect(data, thr=205):
    im = ssh.parse(data)[0]; a = ssh.to_rgba(im)[..., :3]
    g = a.astype(int).mean(-1); m = (g > thr).astype(np.uint8)
    k = cv2.dilate(m, np.ones((3, 5), np.uint8))
    nn, lab, st, _ = cv2.connectedComponentsWithStats(k)
    comps = []
    for i, (x, y, w, h, ar) in enumerate(st[1:], 1):
        if h < 8 or w < 6: continue
        dens = m[y:y + h, x:x + w].sum() / (w * h)
        if dens < 0.12 or (w > 5 * h and dens < 0.2 and h < 10): continue
        if w < 9 and h > 3 * w: continue
        comps.append([x, y, x + w, y + h])
    comps.sort(key=lambda b: b[0])
    lines = []
    for b in comps:
        for L in lines:
            ov = min(L[3], b[3]) - max(L[1], b[1])
            if ov > 0.5 * min(L[3] - L[1], b[3] - b[1]) and b[0] - L[2] <= 14:
                L[0] = min(L[0], b[0]); L[1] = min(L[1], b[1]); L[2] = max(L[2], b[2]); L[3] = max(L[3], b[3]); break
        else: lines.append(list(b))
    lines.sort(key=lambda b: (b[1], b[0]))
    return lines
