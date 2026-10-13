"""메달 오브 아너 프론트라인 한글 패치 빌드: 원본 ISO -> 한글 ISO (원본과 같은 폴더)"""
import os, sys, re, glob, json, struct
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ext, viv, scr, bum, smul, kfont, fontcfg, isobuild, levels, images, ssh, make_src

ROOT = os.path.join(HERE, '..')
TR = os.path.join(ROOT, 'translation')
OUT = os.path.join(ROOT, 'Medal of Honor - Frontline (Korean).iso')
SHELL_FONTS = ['SecretCodesFont_Garamond18.sfn', 'MissionLogFont.sfn', 'PlayerStatsFont.sfn', 'SaveContReplay.sfn',
               'CustomControllerLarge.sfn', 'CustomController.sfn', 'SaveLoadFont.sfn', 'Medals.sfn',
               'PopupDisplay.sfn', 'MissionLogMsnName.sfn', 'Difficulty_.sfn', 'MissionLogRatingInfo.sfn']
LEVEL_MAIN = ['objFont.sfn', 'subtitleFont.sfn', 'comicFont.sfn', 'PopupDisplay.sfn', 'DDayIntro.sfn']


def unesc(s): return s.replace('\\r', '\r').replace('\\n', '\n')


def load_ui():
    src = make_src.ui_strings()
    d = {}
    for f in sorted(glob.glob(os.path.join(TR, 'ui_*.tsv'))):
        for ln in open(f, encoding='utf-8').read().split('\n'):
            if not ln or ln.startswith('#'): continue
            i, ko = ln.split('\t')
            d[src[int(i)]] = unesc(ko)
    return d


def load_subs():
    d = {}
    for f in sorted(glob.glob(os.path.join(TR, 'subs_*.tsv'))):
        for ln in open(f, encoding='utf-8').read().split('\n'):
            if not ln or ln.startswith('#'): continue
            i, ko = ln.split('\t'); d[int(i)] = ko
    return d


UI = load_ui(); SUBS = load_subs()
ALLK = sorted(set(c for t in list(UI.values()) + list(SUBS.values()) for c in t if '가' <= c <= '힣'))
IDX = {c: i for i, c in enumerate(ALLK)}
errors = []


def enc(s):
    o = bytearray()
    for c in s:
        if c in IDX: o += kfont.code_of(IDX[c]).to_bytes(2, 'big')
        else:
            try: o += c.encode('ascii')
            except UnicodeEncodeError: errors.append(f'문자 {c!r} in {s}'); o += b'?'
    return bytes(o)


def check_fmt(en, ko):
    if re.findall(r'%[ds]', en) != re.findall(r'%[ds]', ko): errors.append(f'서식 불일치: {en!r} / {ko!r}')


for en, ko in UI.items(): check_fmt(en, ko)
kchars = lambda texts: sorted(set(c for t in texts for c in t if c in IDX))

# ---------- chars.bum
def patch_bum(c, b, used):
    ss, _ = bum.parse(c, b)
    out = []
    for s in ss:
        k = UI.get(s.decode('latin1'))
        if k is not None:
            used.append(k); e = enc(k)
            if len(e) > 255: errors.append(f'bum 255 초과: {k}'); e = e[:255]
            out.append(e)
        else: out.append(s)
    return bum.build(out)

# ---------- SCR
def patch_scr(b, used):
    b = bytearray(b); n, to = struct.unpack_from('<II', b, 8)
    for i in range(n):
        t, l, o = struct.unpack_from('<III', b, to + i * 12)
        s = bytes(b[o:o + l]).decode('latin1')
        if s in UI: e = enc(UI[s]); used.append(UI[s])
        elif 'DoNotTranslate' in s or s.startswith('~_') or s.startswith('Undefined Local'):
            e = s.encode('latin1') + b'_' * max(l, 10)          # 실행 중 채워지는 버퍼: 용량 확대
        else: continue
        if len(e) <= l and not e.startswith(b'~') and not e.startswith(b'Undefined'):
            b[o:o + len(e)] = e; b[o + len(e)] = 0; nl, no = len(e), o
        else:
            no = len(b); b += e + b'\0'
            while len(b) % 4: b += b'\xff'
            nl = len(e)
        struct.pack_into('<II', b, to + i * 12 + 4, nl, no)
    return bytes(b)


def scr_fonts(b):
    n, to = struct.unpack_from('<II', b, 8)
    return {m.group(1)[0] for m in re.finditer(rb'([\x00-\x0b])\x00\x09\x00', b[:to]) if m.start() % 4 == 0}


def main():
    files = {}
    log = print
    # ---- 셸
    sh = ext.get('DATA/SHELL/SHELL.VIV'); ent = {n: sh[o:o + s] for n, o, s in viv.parse(sh)}
    rep = {}; font_txt = {f: [] for f in ent if f.endswith('.sfn')}
    for n, d in ent.items():
        if n.upper().endswith('.SCR'):
            used = []; rep[n] = patch_scr(d, used)
            fs = scr_fonts(d)
            for k in fs: font_txt[SHELL_FONTS[k]] += used
            font_txt['PopupDisplay.sfn'] += used
            if n.startswith(('Market', 'MissionLog')): font_txt['MissionLogMsnName.sfn'] += used
            if n.startswith('CustomController'):
                for f in ('CustomController.sfn', 'CustomControllerLarge.sfn', 'configMovement.sfn', 'configFont.sfn'): font_txt[f] += used
    bused = []
    rep['chars.bum'], rep['binum.bum'] = patch_bum(ent['chars.bum'], ent['binum.bum'], bused)
    rc, rb = patch_bum(ext.get('DATA/CHARS.BUM'), ext.get('DATA/BINUM.BUM'), bused)
    files['DATA/CHARS.BUM'] = rc; files['DATA/BINUM.BUM'] = rb
    ctrl = [UI[k] for k in ['MOVE', 'LOOK', 'TURN', 'STRAFE', 'JUMP', 'CROUCH', 'AIM', 'FIRE', 'RELOAD', 'NEXT WEAPON',
                            'PREVIOUS WEAPON', 'MELEE', 'ACTION', 'CENTER VIEW', 'ACCEPT CHANGES', 'NEXT', 'PREV', 'CENTER', 'ACCEPT', 'Loading...']]
    for f in ('CustomController.sfn', 'CustomControllerLarge.sfn', 'configMovement.sfn', 'configFont.sfn', 'PopupDisplay.sfn'): font_txt[f] += ctrl
    mem = [v for k, v in UI.items() if 'emory card' in k or 'MEMORY CARD' in k or 'controller' in k or 'saving' in k or 'continue' in k or 'free space' in k or k.startswith('Press ') and len(k) < 12]
    for f in ('memorycardFont.sfn', 'unpluggedFont.sfn', 'PopupDisplay.sfn', 'SaveLoadFont.sfn'): font_txt[f] += mem
    for f, txt in font_txt.items():
        ch = kchars(txt)
        if not ch or f not in fontcfg.FACE: continue
        rep[f] = fontcfg.build_font(f, ent[f], [(IDX[c], c) for c in ch])[0]
        log(f'  셸 폰트 {f}: {len(ch)}자 {len(ent[f])}->{len(rep[f])}')
    rep.update(images.build_shell(ent)); rep.update(images.build_config(ent)); rep.update(images.build_docs(ent))
    files['DATA/SHELL/SHELL.VIV'] = viv.rebuild(sh, rep)
    for n in images.BMPS: files[f'DATA/{n}.BMP'] = images.build_bmp(n, ext.get(f'DATA/{n}.BMP'))
    for k in images.LOAD_TITLES: files[f'DATA/LOADING/LOAD{k}.SSH'] = images.build_loading(k, ext.get(f'DATA/LOADING/LOAD{k}.SSH'))

    # ---- 자막
    U = make_src.sub_keys()
    keymap = {}
    for i, k in enumerate(U):
        if i in SUBS: keymap[tuple(k)] = SUBS[i]
    abk = {}
    for n in sorted(ext.ents):
        if not n.endswith('.ABK'): continue
        d = ext.get(n); bl = smul.find(d)
        if not bl: continue
        a = bytearray(d); ch = False
        for pos, sz, fl, ss in bl:
            k = tuple(x.decode('latin1') for x in ss)
            if k in keymap:
                if not smul.patch(a, pos, sz, enc(keymap[k])): errors.append(f'자막 공간 부족 {n} {keymap[k]}')
                ch = True
        if ch: files[n] = bytes(a)
    lvl_txt = list(SUBS.values()) + bused
    # ---- 레벨
    pause_used = []
    for L in levels.LEVELS:
        d = ext.get(L + '/LEVEL.VIV'); rep = {}
        lent = {n: d[o:o + s] for n, o, s in viv.any_parse(d)}
        if 'PauseScr.scr' in lent: rep['PauseScr.scr'] = patch_scr(lent['PauseScr.scr'], pause_used)
        if 'Pause.ssh' in lent: rep['Pause.ssh'] = images.alpha_text(lent['Pause.ssh'], '일시정지', 'sansH', (230, 230, 90), stroke=2)
        for i, t in images.DDAY_LINES.items():
            n = f'DDayIntro_Line{i}.ssh'
            if n in lent:
                src = ssh.to_rgba(ssh.parse(lent[n])[0]); c = src[..., :3][src[..., 3] > 0x60].mean(0).astype(int)
                rep[n] = images.alpha_text(lent[n], t, 'serif', c)
        for n in lent:
            if n in LEVEL_MAIN: txt = lvl_txt + pause_used
            elif n == 'PauseScreenFont.sfn': txt = pause_used
            else: continue
            rep[n] = fontcfg.build_font(n, lent[n], [(IDX[c], c) for c in kchars(txt)])[0]
        try: files[L + '/LEVEL.VIV'] = viv.rebuild(d, rep)
        except AssertionError: files[L + '/LEVEL.VIV'] = viv.to_bigf(d, rep)
        log(f'  {L}/LEVEL.VIV {len(d)}->{len(files[L + "/LEVEL.VIV"])}')
    log(f'한글 {len(ALLK)}자, 오류 {len(errors)}')
    for e in errors[:50]: log('  !', e)
    if '--check' in sys.argv: return
    isobuild.build(ext.ISO, OUT, files, log)
    log('완료:', OUT)


if __name__ == '__main__':
    main()
