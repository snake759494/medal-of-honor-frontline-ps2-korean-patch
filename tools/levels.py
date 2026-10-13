import sys,os,hashlib
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import ext,viv
LEVELS=sorted(set(e.rsplit('/',1)[0] for e in ext.ents if e.endswith('LEVEL.VIV')))
