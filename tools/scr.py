import struct
def strings(b):
    n,to=struct.unpack_from('<II',b,8)
    out=[]
    for i in range(n):
        t,l,o=struct.unpack_from('<III',b,to+i*12)
        s=b[o:o+l] if t==1 else None
        out.append((i,t,l,o,s))
    return out
