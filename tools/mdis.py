import sys,os,capstone,struct
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
import ext
d=ext.get('MOH2RDVD.ELF')   # 분석용: 원본 ISO에서 직접 읽음
phoff,=struct.unpack_from('<I',d,0x1c);phn,=struct.unpack_from('<H',d,0x2c)
SEG=[]
for i in range(phn):
    t,off,va,pa,fs,ms=struct.unpack_from('<6I',d,phoff+i*32)
    if t==1: SEG.append((va,off,fs,ms))
def v2o(a):
    for va,off,fs,ms in SEG:
        if va<=a<va+fs: return a-va+off
def o2v(o):
    for va,off,fs,ms in SEG:
        if off<=o<off+fs: return o-off+va
def u32(a): return struct.unpack_from('<I',d,v2o(a))[0]
md=capstone.Cs(capstone.CS_ARCH_MIPS,capstone.CS_MODE_MIPS64+capstone.CS_MODE_LITTLE_ENDIAN)
R=['zero','at','v0','v1','a0','a1','a2','a3','t0','t1','t2','t3','t4','t5','t6','t7','s0','s1','s2','s3','s4','s5','s6','s7','t8','t9','k0','k1','gp','sp','fp','ra']
def ee(w):
    op=w>>26;rs=(w>>21)&31;rt=(w>>16)&31;rd=(w>>11)&31;fn=w&63;imm=w&0xffff
    simm=imm-0x10000 if imm&0x8000 else imm
    if op==0 and fn in(0x18,0x19) and rd: return ('mult' if fn==0x18 else 'multu')+f" ${R[rd]}, ${R[rs]}, ${R[rt]}"
    if op==0x1c:
        m={0x18:'mult1',0x19:'multu1',0x1a:'div1',0x1b:'divu1',0x10:'mfhi1',0x12:'mflo1',0x11:'mthi1',0x13:'mtlo1',0x0:'madd',0x20:'madd1'}
        if fn in m: return m[fn]+f" ${R[rd]}, ${R[rs]}, ${R[rt]}"
        return f"mmi.{fn:x} ${R[rd]}, ${R[rs]}, ${R[rt]} sa={(w>>6)&31}"
    if op==0x1e: return f"lq ${R[rt]}, {simm:#x}(${R[rs]})"
    if op==0x1f: return f"sq ${R[rt]}, {simm:#x}(${R[rs]})"
    return None
def dis(a,b):
    out=[]
    for k in range(0,b-a,4):
        o=v2o(a+k);w=struct.unpack_from('<I',d,o)[0];x=ee(w)
        if x is None:
            l=list(md.disasm(d[o:o+4],a+k))
            x=f"{l[0].mnemonic} {l[0].op_str}" if l else f".word {w:#010x}"
        out.append(f"{a+k:08x} {x}")
    return out
if __name__=='__main__':
    for l in dis(int(sys.argv[1],16),int(sys.argv[2],16)): print(l)
