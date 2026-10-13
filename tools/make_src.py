"""원본 ISO에서 번역 대상 원문을 결정적 순서로 추출 (번역표는 번호만 담고 원문은 여기서 로컬 생성)

ui: chars.bum(루트, 셸) → 셸 SCR(이름순) → 레벨 PauseScr.scr 의 고유 문자열, 등장 순서대로 번호 0..
subs: 모든 ABK(경로순)의 SMUL 블록(5개 언어 묶음) 고유값, 등장 순서대로 번호 0..
"""
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ext, viv, bum, scr, smul, levels


def ui_strings():
    out = {}
    def add(s): out.setdefault(s.decode('latin1'), len(out))
    for s in bum.parse(ext.get('DATA/CHARS.BUM'), ext.get('DATA/BINUM.BUM'))[0]: add(s)
    sh = ext.get('DATA/SHELL/SHELL.VIV'); ent = {n: sh[o:o + s] for n, o, s in viv.parse(sh)}
    for s in bum.parse(ent['chars.bum'], ent['binum.bum'])[0]: add(s)
    for n in sorted(ent, key=str.lower):
        if n.upper().endswith('.SCR'):
            for _, t, l, o, s in scr.strings(ent[n]): add(s)
    lv = ext.get(levels.LEVELS[0] + '/LEVEL.VIV')
    for n, o, s in viv.any_parse(lv):
        if n == 'PauseScr.scr':
            for _, t, l, oo, ss in scr.strings(lv[o:o + s]): add(ss)
    return list(out)


def sub_keys():
    U = {}
    for n in sorted(ext.ents):
        if not n.endswith('.ABK'): continue
        for pos, sz, fl, ss in smul.find(ext.get(n)):
            U.setdefault(tuple(x.decode('latin1') for x in ss), len(U))
    return list(U)
