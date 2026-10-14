"""EA MPC 동영상: [태그 4][u32 크기(헤더 포함)] 청크 연속
MPCh = MPEG-2 영상 ES 조각(본문은 +8부터), SCHl/SCCl/SCDl/SCEl = EA 오디오
"""
import struct


def chunks(d):
    p = 0; out = []
    while p + 8 <= len(d):
        tag = d[p:p + 4]; sz, = struct.unpack_from('<I', d, p + 4)
        if sz < 8: break
        out.append((tag, p, sz)); p += sz
    return out


def video(d):
    return b''.join(d[p + 8:p + sz] for t, p, sz in chunks(d) if t == b'MPCh')


def audio(d):
    """EA SCxl 스트림(ffmpeg -f ea 로 디코드 가능)"""
    return b''.join(d[p:p + sz] for t, p, sz in chunks(d) if t != b'MPCh')


def replace_video(d, es):
    """새 영상 ES 를 원래 MPCh 청크 크기대로 다시 나눠 넣는다(길이 같아야 함)"""
    cs = chunks(d); out = bytearray(d); q = 0
    total = sum(sz - 8 for t, p, sz in cs if t == b'MPCh')
    assert len(es) == total, (len(es), total)
    for t, p, sz in cs:
        if t == b'MPCh':
            n = sz - 8; out[p + 8:p + sz] = es[q:q + n]; q += n
    return bytes(out)


def split_pictures(es):
    """영상 ES -> 픽처 단위 조각(앞의 시퀀스/GOP 헤더는 뒤 픽처에 붙임). 원본 MPCh 청크와 같은 단위"""
    import re
    pics = [m.start() for m in re.finditer(b'\x00\x00\x01\x00', es)]
    bounds = []
    for p in pics:
        b = p
        for code in (b'\x00\x00\x01\xb8', b'\x00\x00\x01\xb3'):
            q = es.rfind(code, bounds[-1] if bounds else 0, b)
            if q >= 0 and es.find(b'\x00\x00\x01\x00', q, p) < 0 and es.find(b'\x00\x00\x01\x01', q, p) < 0:
                b = min(b, q)
        if not bounds: b = 0
        bounds.append(b)
    bounds.append(len(es))
    return [es[bounds[i]:bounds[i + 1]] for i in range(len(pics))]


def rebuild(d, pictures):
    """MPCh 청크 k 를 pictures[k] 로 바꿔 다시 쓴다(청크 크기 가변, 오디오 청크 순서 그대로)"""
    out = bytearray(); k = 0
    for t, p, sz in chunks(d):
        if t == b'MPCh':
            b = pictures[k]; k += 1
            out += b'MPCh' + struct.pack('<I', 8 + len(b)) + b
        else:
            out += d[p:p + sz]
    assert k == len(pictures)
    return bytes(out)
