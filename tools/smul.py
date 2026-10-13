import struct
LANGS = ('en', 'es', 'it', 'fr', 'de')
def find(d):
    """[(pos, size, flags(a,b), [5 strings bytes])]"""
    out = []; i = 0
    while True:
        i = d.find(b'SMUL', i)
        if i < 0: break
        sz, n, a, b = struct.unpack_from('<4I', d, i + 4)
        if n != 5 or sz > 0x2000 or sz < 0x28:
            i += 4; continue
        offs = struct.unpack_from('<5I', d, i + 20)
        base = i + 0x28
        ss = []
        for o in offs:
            e = d.index(b'\0', base + o); ss.append(d[base + o:e])
        out.append((i, sz, (a, b), ss))
        i += 4
    return out
def patch(d, pos, sz, text, a=1):
    """블록 크기 유지하고 EN 슬롯에 text, 나머지는 빈 문자열"""
    d = bytearray(d) if not isinstance(d, bytearray) else d
    room = sz - 0x28
    need = len(text) + 2
    if need > room: return False
    body = text + b'\0' + b'\0'
    body += bytes(room - len(body))
    d[pos + 0x28:pos + sz] = body
    struct.pack_into('<I', d, pos + 12, a)
    struct.pack_into('<5I', d, pos + 20, 0, len(text) + 1, len(text) + 1, len(text) + 1, len(text) + 1)
    return True
