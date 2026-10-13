import sys,struct,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)));import mdis
d=mdis.d;va,off,fs,ms=mdis.SEG[0]
W=struct.unpack_from('<%dI'%(fs//4),d,off)
def xrefs(target,win=12):
    res=[]
    for i,w in enumerate(W):
        if (w>>26)==0x0f:
            rt=(w>>16)&31;hi=w&0xffff
            for j in range(i+1,min(i+win,len(W))):
                x=W[j];op=x>>26
                if op in(0x09,0x23,0x21,0x25,0x24,0x20,0x2b,0x29,0x28,0x37,0x3f,0x31,0x39,0x0d) and ((x>>21)&31)==rt:
                    lo=x&0xffff;lo=lo-0x10000 if lo&0x8000 and op!=0x0d else lo
                    if (hi<<16)+lo==target: res.append(va+j*4)
    return res
if __name__=='__main__':
    for a in sys.argv[1:]: print(a,[hex(x) for x in xrefs(int(a,16))])
def callers(t):
    j=(3<<26)|((t>>2)&0x3ffffff)
    return [va+i*4 for i,w in enumerate(W) if w==j]
