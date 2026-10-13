import struct
def parse(d):
    assert d[:4]==b'BIGF'
    n,hl=struct.unpack_from('>II',d,8);p=16;out=[]
    for i in range(n):
        o,s=struct.unpack_from('>II',d,p);p+=8
        e=d.index(b'\0',p);nm=d[p:e].decode('latin1');p=e+1
        out.append((nm,o,s))
    return out
if __name__=='__main__':
    import sys
    d=open(sys.argv[1],'rb').read()
    for nm,o,s in parse(d): print(nm,hex(o),s)

def parse_c0fb(d):
    assert d[:2]==b'\xc0\xfb'
    hl,n=struct.unpack_from('>HH',d,2);p=6;out=[]
    for i in range(n):
        o=int.from_bytes(d[p:p+3],'big');s=int.from_bytes(d[p+3:p+6],'big');p+=6
        e=d.index(b'\0',p);nm=d[p:e].decode('latin1');p=e+1
        out.append((nm,o,s))
    return out
def any_parse(d):
    return parse(d) if d[:4]==b'BIGF' else parse_c0fb(d)

def rebuild(d, repl, align=64):
    """repl: {name: bytes}. 항목 순서·헤더 길이 유지, 데이터는 원래 오프셋 순으로 재배치"""
    big = d[:4] == b'BIGF'
    L = parse(d) if big else parse_c0fb(d)
    first = min(o for n, o, s in L)
    out = bytearray(d[:first])
    newpos = {}
    for n, o, s in sorted(L, key=lambda x: x[1]):
        b = repl.get(n, d[o:o+s])
        p = len(out)
        if p % align: out += bytes(align - p % align); p = len(out)
        newpos[n] = (p, len(b)); out += b
    # 원본 끝 정렬 패딩 유지
    if big:
        p = 16
        n_, = struct.unpack_from('>I', d, 8)
        for i in range(n_):
            e = d.index(b'\0', p + 8); nm = d[p+8:e].decode('latin1')
            struct.pack_into('>II', out, p, *newpos[nm]); p = e + 1
        old, = struct.unpack_from('>I', d, 4)
        struct.pack_into('>I', out, 4, old + len(out) - len(d))
    else:
        hl, n_ = struct.unpack_from('>HH', d, 2); p = 6
        for i in range(n_):
            e = d.index(b'\0', p + 6); nm = d[p+6:e].decode('latin1')
            o, s = newpos[nm]
            assert o < 1 << 24 and s < 1 << 24
            out[p:p+3] = o.to_bytes(3, 'big'); out[p+3:p+6] = s.to_bytes(3, 'big'); p = e + 1
    return bytes(out)

def to_bigf(d, repl, align=64):
    """C0FB 를 BIGF 로 다시 작성(16MB 초과 대응). 항목 순서 유지"""
    L = any_parse(d)
    hdr = bytearray(b'BIGF' + bytes(12))
    for n, o, s in L: hdr += bytes(8) + n.encode('latin1') + b'\0'
    hl = len(hdr)
    out = bytearray(hdr)
    while len(out) % align: out += b'\0'
    pos = {}; tot = 0
    for n, o, s in sorted(L, key=lambda x: x[1]):
        b = repl.get(n, d[o:o+s])
        while len(out) % align: out += b'\0'
        pos[n] = (len(out), len(b)); out += b; tot += len(b)
    struct.pack_into('>III', out, 4, tot, len(L), hl)
    p = 16
    for n, o, s in L:
        struct.pack_into('>II', out, p, *pos[n]); p += 8 + len(n) + 1
    return bytes(out)
