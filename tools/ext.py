import sys,os
sys.path.insert(0,os.path.dirname(__file__))
import isofs
ISO=os.path.join(os.path.dirname(__file__),'..','Medal of Honor - Frontline (Korea).iso')
f=open(ISO,'rb')
ents={e[0]:e for e in isofs.walk(f)}
def get(name):
    _,l,s,_=ents[name];f.seek(l*2048);return f.read(s)
if __name__=='__main__':
    for n in sys.argv[1:]:
        os.makedirs(os.path.dirname('x/'+n) or '.',exist_ok=True);open('x/'+n,'wb').write(get(n))
