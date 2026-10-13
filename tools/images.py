"""이미지 번역 사양 및 적용"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ssh, imgko

# (파일, 한국어, 모드, 임계, 서체, 추가 옵션)
PLATE = dict(mode='bright', thr=150, face='sans', shadow=(0, 0, 0))
ARROW = dict(mode='bright', thr=150, face='sans', shadow=(0, 0, 0))
GREY = dict(mode='bright', thr=135, face='sansEB', shadow=(40, 40, 40), angle=3, dil=3)
LABEL = dict(mode='dark', thr=90, face='sansEB')
SHELL = [
    ('Audio_TXT', '오디오', PLATE), ('Bonus_TXT', '보너스', PLATE), ('Controller_TXT', '컨트롤러', PLATE),
    ('Credits_TXT', '제작진', PLATE), ('Diff_TXT', '난이도', PLATE), ('Extras_TXT', '부가 영상', PLATE),
    ('History_TXT', '역사', PLATE), ('Making_TXT', '제작 과정', PLATE), ('Mission_TXT', '미션', PLATE),
    ('Password_TXT', '암호', PLATE), ('subtitle_TXT', '자막', PLATE),
    ('folder_TXT', '플레이', ARROW), ('Options_TXT', '옵션', ARROW), ('Gallery_TXT', '갤러리', ARROW),
    ('Next_Mission_TXT', '다음 미션', ARROW), ('Personal_Recs_TXT', '개인 기록', ARROW),
    ('mission_1_TXT', '항구의\n폭풍', GREY), ('mission_2_TXT', '건초 더미\n속 바늘', GREY),
    ('mission_3_TXT', '머나먼\n다리들', GREY), ('mission_4_TXT', '질주하는\n천둥', GREY),
    ('mission_5_TXT', '호르텐의\n둥지', GREY), ('mission_6_TXT', '디데이', GREY),
    ('extras_1_TXT', '애니메이터의\n책상에서', GREY), ('extras_2_TXT', '죽기\n좋은 날', GREY),
    ('extras_3_TXT', '팀 화면', GREY), ('extras_4_TXT', '전쟁의\n관현악', GREY), ('extras_5_TXT', '짧은 대화', GREY),
    ('Contr_1', 'MOH\n저격수', dict(PLATE, face='sansH', shadow=(20, 20, 20), shoff=2)),
    ('Contr_2', '클래식\nMOH', dict(PLATE, face='sansH', shadow=(20, 20, 20), shoff=2)),
    ('Contr_3', '간편\n사격', dict(PLATE, face='sansH', shadow=(20, 20, 20), shoff=2)),
    ('Contr_4', '간편\n재장전', dict(PLATE, face='sansH', shadow=(20, 20, 20), shoff=2)),
    ('Contr_5', '클래식\nMOH 플러스', dict(PLATE, face='sansH', shadow=(20, 20, 20), shoff=2)),
    ('Contr_6', '사용자\n설정', dict(PLATE, face='sansH', shadow=(20, 20, 20), shoff=2)),
]
# 상자를 직접 지정하는 것: (파일, [(box, 한국어, 옵션)])
SHELL_BOX = [
    ('Mono_HL', [((12, 8, 108, 27), '모노', LABEL)]), ('Music_HL', [((12, 8, 108, 27), '음악', LABEL)]),
    ('Stereo_HL', [((12, 8, 108, 27), '스테레오', LABEL)]), ('DolbyS_HL', [((10, 8, 110, 27), '돌비 서라운드', LABEL)]),
    ('sfx_HL', [((10, 8, 110, 27), '효과음', LABEL)]),
    ('Cross_hair_HL', [((14, 7, 118, 40), '조준선', LABEL), ((14, 41, 62, 57), '켬', LABEL), ((66, 41, 118, 57), '끔', LABEL)]),
    ('Invert_HL', [((14, 7, 118, 40), 'Y축 반전', LABEL), ((14, 41, 62, 57), '켬', LABEL), ((66, 41, 118, 57), '끔', LABEL)]),
    ('grenade_HL', [((14, 7, 118, 40), '수류탄\n쿠킹', LABEL), ((14, 41, 62, 57), '켬', LABEL), ((66, 41, 118, 57), '끔', LABEL)]),
    ('Vibrate_off', [((12, 5, 148, 36), '진동: 끔', dict(mode='dark', thr=60, face='sansEB', color=(30, 50, 30)))]),
    ('Vibrate_on', [((12, 5, 148, 36), '진동: 켬', dict(mode='dark', thr=60, face='sansEB', color=(30, 50, 30)))]),
    ('Vibrate_off_HL', [((12, 4, 148, 32), '진동: 끔', dict(mode='bright', thr=170, face='sansEB', color=(220, 255, 200)))]),
    ('Vibrate_on_HL', [((12, 4, 148, 32), '진동: 켬', dict(mode='bright', thr=170, face='sansEB', color=(220, 255, 200)))]),
]


def auto_box(rgb, mode, thr):
    a = rgb[..., :3].astype(int).mean(-1); h, w = a.shape
    mx, my = int(w * .08), int(h * .12)
    sub = a[my:h - my, mx:w - mx]; m = (sub > thr) if mode == 'bright' else (sub < thr)
    ys, xs = np.where(m)
    return [int(xs.min() + mx) - 2, int(ys.min() + my) - 2, int(xs.max() + mx) + 3, int(ys.max() + my) + 3], m


def text_color(rgb, box, mode, thr):
    x0, y0, x1, y1 = box; r = rgb[y0:y1, x0:x1, :3].reshape(-1, 3).astype(int)
    g = r.mean(1)
    sel = r[g >= np.percentile(g, 92)] if mode == 'bright' else r[g <= np.percentile(g, 8)]
    return tuple(int(v) for v in sel.mean(0))


def spec_auto(data, text, opt):
    im = ssh.parse(data)[0]; rgba = ssh.to_rgba(im)
    box, _ = auto_box(rgba, opt['mode'], opt['thr'])
    h, w = rgba.shape[:2]
    box = [max(0, box[0]), max(0, box[1]), min(w, box[2]), min(h, box[3])]
    sp = dict(opt); sp['box'] = box; sp['text'] = text
    sp.setdefault('color', text_color(rgba, box, opt['mode'], opt['thr']))
    # 글 영역은 조금 넓게
    cx = (box[0] + box[2]) / 2; bw = max(box[2] - box[0], w * 0.6)
    sp['tbox'] = [int(max(4, cx - bw / 2)), box[1], int(min(w - 4, cx + bw / 2)), box[3]]
    if opt.get('mode') == 'dark': sp['color'] = opt.get('color', (25, 25, 25))
    return sp


def build_shell(ent, preview_dir=None):
    out = {}
    for name, text, opt in SHELL:
        fn = name + '.ssh'; d = ent[fn]
        sp = spec_auto(d, text, opt)
        out[fn], prev = imgko.apply(d, [sp])
        if preview_dir: imgko.preview(prev, os.path.join(preview_dir, name + '.png'))
    for name, items in SHELL_BOX:
        fn = name + '.ssh'; d = ent[fn]; im = ssh.parse(d)[0]; rgba = ssh.to_rgba(im)
        sps = []
        for box, text, opt in items:
            sp = dict(opt); sp['box'] = list(box); sp['text'] = text
            sp.setdefault('color', (25, 25, 25) if opt['mode'] == 'dark' else (255, 255, 255))
            sps.append(sp)
        out[fn], prev = imgko.apply(d, sps)
        if preview_dir: imgko.preview(prev, os.path.join(preview_dir, name + '.png'))
    return out

# ---------------- 결과·로딩 BMP (512x256 24비트)
LOADING = lambda box: ((box[0] - 2, box[1] - 2, box[2] + 3, box[3] + 3), '불러오는 중...', dict(maskall=True, face='sans', color=(150, 150, 155)))
ACC = lambda col, y1=24: ((180, 4, 508, y1), '임무 완수!', dict(mode='bright', thr=60, face='sansEB', color=col, dil=2))
BMPS = {
    'VICT1_4': [ACC((214, 120, 50)), LOADING((402, 217, 479, 225))],
    'VICT2_3': [ACC((150, 160, 180), 31), LOADING((401, 212, 479, 221))],
    'VICT3_3': [ACC((160, 160, 160)), LOADING((393, 214, 471, 223))],
    'VICT4_3': [ACC((110, 150, 90), 31), LOADING((411, 210, 489, 218))],
    'VICT6_2': [ACC((190, 190, 190)), LOADING((409, 221, 487, 230))],
    'VICT5_4': [((50, 15, 266, 92), '승리!\n모두 집으로 돌아가자', dict(maskall=True, face='sansH', color=(230, 170, 30), shadow=(60, 40, 0), shoff=2)),
                LOADING((403, 226, 480, 235))],
    'FINAL': [((50, 15, 266, 92), '승리!\n모두 집으로 돌아가자', dict(maskall=True, face='sansH', color=(230, 170, 30), shadow=(60, 40, 0), shoff=2))],
    'RETURN': [((240, 4, 508, 24), '기지로 귀환', dict(mode='bright', thr=60, face='sansEB', color=(200, 200, 200))), LOADING((397, 215, 475, 224))],
    'VICTORY': [((250, 4, 508, 24), '전투는 계속된다', dict(mode='bright', thr=60, face='sansEB', color=(220, 190, 80))), LOADING((407, 219, 484, 228))],
    'DEFEAT': [((30, 45, 200, 95), '전사자를\n기리며', dict(maskall=True, face='sansEB', color=(220, 110, 30))),
               ((125, 140, 290, 172), '임무 실패.', dict(maskall=True, face='serif', color=(120, 60, 50))),
               LOADING((416, 241, 493, 250))],
    'START': [((110, 200, 375, 228), '불러오는 중', dict(maskall=True, face='serifEB', color=(40, 60, 50), fill=None))],
    'DDAY': [((10, 8, 400, 35), '"프랑스에 온 걸 환영한다, 병사!"', dict(maskall=True, face='serif', color=(220, 220, 225), shadow=(40, 40, 50))),
             ((225, 35, 480, 55), '자네는 임무를 완수했다.', dict(maskall=True, face='serif', color=(245, 245, 245), shadow=(40, 40, 50)))],
}


def build_bmp(name, data, preview_dir=None):
    from PIL import Image
    import io
    im = Image.open(io.BytesIO(data)).convert('RGB')
    a = np.dstack([np.array(im), np.full(im.size[::-1], 255, np.uint8)])
    for box, text, opt in BMPS[name]:
        sp = dict(opt); sp['box'] = list(box); sp['text'] = text; a = imgko.render(a, sp)
    out = Image.fromarray(a[..., :3])
    if preview_dir: out.save(os.path.join(preview_dir, name + '.png'))
    b = io.BytesIO(); out.save(b, 'BMP'); nb = b.getvalue()
    if len(nb) < len(data): nb += bytes(len(data) - len(nb))
    # 원본 헤더 크기 유지 확인
    return nb


# ---------------- 로딩 화면(640x448 8bpp) 미션 제목
LOAD_TITLES = {'1_1': '해안의 밀항자', '1_2': '특수 화물', '1_3': '폭풍의 눈', '1_4': '우연한 만남',
               '2_1': '거친 착륙', '2_2': '황금 사자', '2_3': '라푼첼 작전', '3_1': '네이메헌 다리',
               '3_2': '한 걸음씩', '3_3': '아른험의 기사들', '4_1': '궤도 위에서', '4_2': '폭풍을 뚫고',
               '4_3': '탈선!', '5_1': '날개를 꺾어라', '5_2': '적의 광산', '5_3': '레이더를 피해',
               '5_4': '쇼를 훔쳐라', '6_1': '가장 빛나는 순간', '6_2': '돌파구로'}


def build_loading(key, data, preview_dir=None):
    im = ssh.parse(data)[0]; rgba = ssh.to_rgba(im)
    g = rgba[:90, :, :3].astype(int).mean(-1)
    bg = np.median(rgba[:90, :, :3].reshape(-1, 3), 0).astype(int)
    ys, xs = np.where(g > bg.mean() + 25)
    box = [int(xs.min()) - 3, int(ys.min()) - 3, int(xs.max()) + 4, int(ys.max()) + 4]
    col = tuple(int(v) for v in rgba[ys, xs, :3][rgba[ys, xs, :3].astype(int).mean(1) >= np.percentile(rgba[ys, xs, :3].astype(int).mean(1), 80)].mean(0))
    sp = dict(box=box, text=LOAD_TITLES[key], fill=tuple(int(v) for v in bg), face='serif', color=col,
              tbox=[150, box[1] - 4, 490, box[3] + 4], maxpx=24)
    out, prev = imgko.apply(data, [sp])
    if preview_dir: imgko.preview(prev[:120], os.path.join(preview_dir, 'LOAD' + key + '.png'))
    return out


# ---------------- 레벨 32비트 알파 이미지(PAUSE, 디데이 시구)
DDAY_LINES = {1: '그가 천국에 이르러', 2: '성 베드로에게 아뢰리라:', 3: '"병사 하나 더 보고합니다 -',
              4: '지옥에서 복무를 마쳤습니다."', 5: '1944년 6월 6일', 6: '오마하 해변', 7: '프랑스 노르망디'}


def alpha_text(data, text, face, color, stroke=0, stroke_col=(0, 0, 0), maxpx=None, preview=None):
    from PIL import Image, ImageDraw
    im = ssh.parse(data)[0]; w, h = im.w, im.h
    src = ssh.to_rgba(im)
    f, px = imgko.fit_font(face, [text], w - 4 - stroke * 2, h - 2 - stroke * 2, maxpx or h)
    L = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    bb = d.textbbox((0, 0), text, font=f, stroke_width=stroke)
    x = (w - (bb[2] - bb[0])) / 2 - bb[0]; y = (h - (bb[3] - bb[1])) / 2 - bb[1]
    d.text((x, y), text, font=f, fill=tuple(color) + (255,), stroke_width=stroke, stroke_fill=tuple(stroke_col) + (255,))
    a = np.array(L).astype(np.float32)
    out = np.zeros((h, w, 4), np.uint8)
    out[..., :3] = a[..., :3].astype(np.uint8)
    out[..., 3] = np.round(a[..., 3] / 255 * 0x80).astype(np.uint8)
    if preview: imgko.preview(out, preview)
    return ssh.write(data, im, out)


# ---------------- 컨트롤러 설정 화면(640x448 8bpp): 자동 검출한 줄 번호 -> 한국어
import cfgdetect
_C = {'CROUCH': '앉기', 'CALL HQ': '본부 호출', 'RELOAD': '재장전', 'PAUSE': '일시정지', 'AIM': '조준', 'FIRE': '사격',
      'SNIPER ZOOM': '저격 확대', 'JUMP': '점프', 'NEXT WEAPON': '다음 무기', 'TOGGLE HUD': 'HUD 켜기/끄기',
      'ACTION': '행동', 'PREV. WEAPON': '이전 무기', 'MOVE/STRAFE': '이동/옆걸음', 'LOOK/TURN': '시점/회전',
      'L3 BUTTON': 'L3 버튼', 'R3 BUTTON': 'R3 버튼', 'CENTER VIEW': '시점 중앙', 'MELEE ATTACK': '근접 공격',
      'STRAFE LEFT': '왼쪽 옆걸음', 'STRAFE RIGHT': '오른쪽 옆걸음', 'AIM/LOOK': '조준/시점', 'RELOAD/ACTION': '재장전/행동',
      'MOVE/TURN': '이동/회전', 'LOOK': '시점', 'LOOK/STRAFE': '시점/옆걸음'}
_STD = lambda t, s, a: [t, s] + a
CONFIG = {
    'Config_1': ['MOH 저격수', '최고의 조작감을 위한 투 스틱 조작', 'CROUCH', 'CALL HQ', 'RELOAD', 'PAUSE', 'AIM', 'FIRE', 'SNIPER ZOOM',
                 'JUMP', 'NEXT WEAPON', 'TOGGLE HUD', 'ACTION', 'PREV. WEAPON', 'MOVE/STRAFE', 'LOOK/TURN', 'L3 BUTTON',
                 'R3 BUTTON', 'CENTER VIEW', 'MELEE ATTACK'],
    'Config_2': ['클래식 MOH', '쉬운 이동을 위한 전통적인 원 스틱 조작', 'CROUCH', 'CALL HQ', 'AIM/LOOK', 'PAUSE', 'STRAFE LEFT',
                 'STRAFE RIGHT', 'SNIPER ZOOM', 'JUMP', 'NEXT WEAPON', 'TOGGLE HUD', 'FIRE', 'RELOAD/ACTION', 'MOVE/TURN',
                 'LOOK', 'L3 BUTTON', 'R3 BUTTON', 'CENTER VIEW', 'MELEE ATTACK'],
    'Config_3': ['간편 사격', '큰 트리거를 선호하는 이를 위한 투 스틱 조작', 'CALL HQ', 'AIM', 'PAUSE', 'FIRE', 'CROUCH', 'RELOAD',
                 'SNIPER ZOOM', 'JUMP', 'NEXT WEAPON', 'TOGGLE HUD', 'ACTION', 'PREV. WEAPON', 'MOVE/STRAFE', 'LOOK/TURN',
                 'L3 BUTTON', 'R3 BUTTON', 'CENTER VIEW', 'MELEE ATTACK'],
    'Config_4': ['간편 재장전', '재장전이 편리한 투 스틱 조작', 'CALL HQ', 'AIM', 'PAUSE', 'FIRE', 'CROUCH', 'MELEE ATTACK',
                 'SNIPER ZOOM', 'JUMP', 'NEXT WEAPON', 'TOGGLE HUD', 'ACTION', 'PREV. WEAPON', 'MOVE/STRAFE', 'LOOK/TURN',
                 'L3 BUTTON', 'R3 BUTTON', 'CENTER VIEW', 'RELOAD'],
    'Config_5': ['클래식 MOH 플러스', '클래식 MOH의 안정감을 갖춘 투 스틱 조작', 'CROUCH', 'CALL HQ', 'RELOAD', 'PAUSE', 'AIM', 'FIRE',
                 'SNIPER ZOOM', 'JUMP', 'NEXT WEAPON', 'TOGGLE HUD', 'ACTION', 'PREV. WEAPON', 'MOVE/TURN', 'LOOK/STRAFE',
                 'L3 BUTTON', 'R3 BUTTON', 'CENTER VIEW', 'MELEE ATTACK'],
    'Config_6': ['사용자 설정'],
    'ConfigCustom_master': ['사용자 설정', 'CALL HQ', 'PAUSE', 'SNIPER ZOOM', 'TOGGLE HUD', 'L3 BUTTON', 'R3 BUTTON'],
}
# 직접 상자: 컨트롤러 선택 화면
CHOICE_TXT = ['컨트롤러 설정 선택', 'MOH 저격수', '클래식 MOH', '옵션 화면에서 다른 설정도', '선택할 수 있습니다']
CHOICE_DARK = [((60, 236, 278, 292), '최고의 조작감을 위한\n투 스틱 조작'), ((356, 236, 598, 292), '쉬운 이동을 위한\n전통적인 원 스틱 조작')]


def build_config(ent, preview_dir=None):
    out = {}
    for name, texts in CONFIG.items():
        fn = name + '.ssh'; d = ent[fn]; lines = cfgdetect.detect(d)
        assert len(lines) >= len(texts), (name, len(lines))
        sps = []
        for i, t in enumerate(texts):
            x0, y0, x1, y1 = lines[i]; ko = _C.get(t, t)
            big = (y1 - y0) > 20
            sps.append(dict(box=[x0 - 8, y0 - 2, x1 + 8, y1 + 3] if big else [x0 - 7, y0 - 1, x1 + 7, y1 + 2], text=ko, mode='bright',
                            thr=140 if big else 185, dil=4 if big else 2,
                            face='sansH' if big else 'sansEB', color=(240, 240, 240), shadow=(0, 0, 0),
                            shoff=2 if big else 1, tbox=[x0 - 6, y0 - 1, x1 + 6, y1 + 2]))
        out[fn], prev = imgko.apply(d, sps)
        if preview_dir: imgko.preview(prev, os.path.join(preview_dir, name + '.png'))
    for name, title, sub in [('Config_Choice_MS', 'MOH 저격수', '최고의 조작감을 위한\n투 스틱 조작'),
                             ('Config_Choice_CM', '클래식 MOH', '쉬운 이동을 위한\n전통적인 원 스틱 조작')]:
        fn = name + '.ssh'; d = ent[fn]; (x0, y0, x1, y1), = cfgdetect.detect(d)[:1]
        im = ssh.parse(d)[0]; W, H = im.w, im.h
        sps = [dict(box=[x0 - 6, y0 - 2, x1 + 6, y1 + 3], text=title, mode='bright', thr=140, dil=3, face='sansEB',
                    color=(240, 240, 240), shadow=(0, 0, 0), maxpx=y1 - y0 + 2),
               dict(box=[CHOICE_DARK[0 if name.endswith('MS') else 1][0][0] - (20 if name.endswith('MS') else 320), CHOICE_DARK[0][0][1] - 79, CHOICE_DARK[0 if name.endswith('MS') else 1][0][2] - (20 if name.endswith('MS') else 320), CHOICE_DARK[0][0][3] - 79], text=sub, mode='dark', thr=110, dil=2, face='sansEB',
                    color=(50, 40, 30), maxpx=19)]
        out[fn], prev = imgko.apply(d, sps)
        if preview_dir: imgko.preview(prev, os.path.join(preview_dir, name + '.png'))
    for name in ['Config_Choice_master']:
        fn = name + '.ssh'; d = ent[fn]; L = cfgdetect.detect(d); sps = []
        t0 = [min(L[0][0], L[1][0]), min(L[0][1], L[1][1]), max(L[0][2], L[1][2]), max(L[0][3], L[1][3])]
        boxes = [t0, L[2], L[3], L[4], L[5]]
        for (x0, y0, x1, y1), ko in zip(boxes, CHOICE_TXT):
            big = (y1 - y0) > 20
            sps.append(dict(box=[x0 - 6, y0 - 2, x1 + 6, y1 + 3], text=ko, mode='bright', thr=140, dil=3,
                            face='sansH' if big else 'sansEB', color=(240, 240, 240), shadow=(0, 0, 0), shoff=2 if big else 1, maxpx=min(y1 - y0 + 2, 30) if ko != CHOICE_TXT[3] and ko != CHOICE_TXT[4] else 21))
        for box, ko in CHOICE_DARK:
            sps.append(dict(box=list(box), text=ko, mode='dark', thr=110, dil=2, face='sansEB', color=(50, 40, 30), maxpx=19))
        out[fn], prev = imgko.apply(d, sps)
        if preview_dir: imgko.preview(prev, os.path.join(preview_dir, name + '.png'))
    return out


# ---------------- 문서·간판 이미지(직접 좌표)
RED = (165, 60, 60)
DOCS = {
    'Player_stats_award': [((6, 8, 230, 92), '훈장 수여', dict(mode='red', thr=25, dil=2, face='serifEB', color=(185, 45, 60), angle=10, tbox=(14, 4, 214, 60)))],
    'Save_master': [((133, 154, 513, 191), '코드네임 선택:', dict(maskall=True, face='sansH', color=(25, 25, 25))),
                    ((196, 193, 450, 215), 'SEND를 눌러 시작', dict(maskall=True, face='sansEB', color=(25, 25, 25)))],
    'MissionLog_master': [((38, 10, 198, 46), '미션 로그', dict(maskall=True, face='serifEB', color=RED))],
    'market_master': [((40, 17, 212, 49), '마켓 가든', dict(maskall=True, face='serifEB', color=RED)),
                      ((262, 14, 352, 44), '디데이', dict(maskall=True, face='serifEB', color=RED))],
    'Perf_Eval_master': [((190, 19, 474, 44), '성과 평가', dict(maskall=True, face='serifEB', color=(150, 55, 55), tbox=(230, 14, 434, 48)))],
    'secretcodes_master': [((82, 42, 178, 73), '보너스:', dict(maskall=True, face='serifEB', color=RED)),
                           ((405, 64, 448, 85), '켬', dict(maskall=True, face='sansEB', color=(30, 30, 30))),
                           ((470, 64, 530, 85), '끔', dict(maskall=True, face='sansEB', color=(30, 30, 30)))],
    'Main_Master': [((168, 60, 330, 92), '시작', dict(mode='bright', thr=150, face='sans', color=(235, 235, 235), shadow=(0, 0, 0)))],
}


def build_docs(ent, preview_dir=None):
    out = {}
    for name, items in DOCS.items():
        fn = name + '.ssh'
        if fn not in ent: continue
        sps = [dict(opt, box=list(b), text=t) for b, t, opt in items]
        out[fn], prev = imgko.apply(ent[fn], sps)
        if preview_dir: imgko.preview(prev, os.path.join(preview_dir, name + '.png'))
    return out
