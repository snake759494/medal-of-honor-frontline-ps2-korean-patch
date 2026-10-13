import struct
def parse(chars, binum):
    n, = struct.unpack_from('<H', binum, 0)
    out = []; p = 0
    for i in range(n):
        pad, ln = binum[2+i*2], binum[3+i*2]
        s = chars[p:p+ln]; out.append(s)
        assert chars[p+ln] == 0, (i, p, s)
        p += ln + 1 + pad
    return out, p
def build(strs):
    c = bytearray(); b = bytearray(struct.pack('<H', len(strs)))
    for s in strs:
        assert len(s) < 256
        pad = 4 - (len(s) + 1) % 4 if (len(s)+1) % 4 else 4
        b += bytes([pad, len(s)]); c += s + bytes(1 + pad)
    return bytes(c), bytes(b)
