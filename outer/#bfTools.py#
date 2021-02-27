
from array import array
import asm_tools
import filt
import math

class BufFiller:
    def __init__(self,func):
        self.func = func
    def __call__(self,buf):
        self.func(buf)
    def __add__(self,o):
        return BFSum(self,o)
    def __radd__(self,o):
        return BFSum(o,self)
    def __sub__(self,o):
        return BFDif(self,o)
    def __rsub__(self,o):
        return BFDif(o,self)
    def __mul__(self,o):
        return BFProd(self,o)
    def __rmul__(self,o):
        return BFProd(o,self)
    def __div__(self,o):
        return BFQuot(self,o)
    def __rdiv__(self,o):
        return BFQuot(o,self)
    def __lshift__(self,n):
        b = array('f',[0]*256)
        while n > len(b):
            self(b)
            n -= len(b)
        self(memoryview(b)[:n])
        return self
    def __neg__(self):
        return BFNeg(self)
    def __pos__(self):
        return self
    def sqrt(self):
        return BFSqrt(self)
    def floor(self):
        return BFFloor(self)
    def filt(self,bq):
        return BFFilt(self,bq)
    def sfilt(self,b0=[1,0,0,1],b1=[0,0,0,0],b2=[0,0,0,0],a1=[0,0,0,0],a2=[0,0,0,0],s0=[0,0],s1=[0,0]):
        assert len(b0) == len(b1) == len(b2) == len(a1) == len(a2) == 4
        assert len(s0) == len(s1) == 2
        return BFSFilt(self,array('f',a1+a2+b0+b1+b2+s0+s1))
              
    def nrr(self,n,d):
        return BFNRR(self,n,d)
    
    def __repr__(self):
        return "bf_"+repr(self.func)

    def split(self,n=2):
        shared = [array('f',[])]+[0]+[0 for i in range(n)]
        def makedo(ii,f):
            def do(buf,s=shared,i=(ii+2)):
                mv = memoryview(buf)
                av = memoryview(s[0])
                while len(mv):
                    M = s[1]
                    common = M-s[i]
                    #print(len(s[0]),common,s[1:],s[0])
                    if common == 0:
                        #make new data
                        f(mv)
                        c = len(s[0])-s[i]
                        if c < len(mv):
                            av[s[i]:] = mv[:c]
                            s[0] += mv[c:]
                        else:
                            av[s[i]:s[i]+len(mv)] = mv
                        s[i] += len(mv)
                        s[1] += len(mv)
                        mv = mv[len(mv):]
                    else:
                        #take data
                        l = min(len(mv),common)
                        mv[:l] = s[0][s[i]:s[i]+l]
                        mv = mv[l:]
                        s[i] += l
                        m = min(s[2:])
                        if m != 0:
                            #shift buff
                            av[0:M-m] = av[m:M]
                            for j in range(1,len(s)):
                                s[j] -= m
            return do
        return [BufFiller(makedo(i,self)) for i in range(n)]
        
        

        
class DC(BufFiller):
    def __init__(self,v):
        if type(v) == complex:
            self.attrs = array('f',[v.real,v.imag])
        else:
            self.attrs = array('f',[v])
    def __repr__(self):
        if len(self.attrs) == 1:
            return "DC("+repr(self.attrs[0])+")"
        return "DC("+repr(self.attrs[0])+"+"+repr(self.attrs[1])+"j)"
    def __call__(self,buf):
        if len(buf):
            self._fill(buf,self.attrs,len(buf),len(self.attrs))
    @staticmethod
    @micropython.asm_thumb
    def _fill(r0,r1,r2,r3):
        mov(r5,r3)
        mov(r6,r1)
        label(loop)
        ldr(r4,[r1,0])
        add(r1,4)
        sub(r5,1)
        itt(eq)
        mov(r5,r3)
        mov(r1,r6)
        str(r4,[r0,0])
        add(r0,4)
        sub(r2,1)
        bgt(loop)
mute = DC(0)

        
def bfify(v):
    if issubclass(type(v),BufFiller):
        return v
    try:
        return DC(float(v))
    except:
        return BufFiller(v)

    
class BufFillerFold(BufFiller):
    def __init__(self,a=mute,*s):
        self.start = bfify(a)
        self.parts = [bfify(e) for e in s]
        self.buf = array('f',[])
    def __call__(self,buf):
        if len(buf):
            if len(self.buf) < len(buf):
                self.buf += array('f',[0]*(len(buf)-len(self.buf)))
            m = memoryview(self.buf)[:len(buf)]
            self.start(buf)
            for p in self.parts:
                p(m)
                self._func(buf)
    def _func(self,b):
        pass
    def __repr__(self,f=' op '):
        return "("+repr(self.start)+f+f.join((repr(p) for p in self.parts))+")"
class BFSum(BufFillerFold):
    def __repr__(self):
        return super().__repr__("+")
    def _func(self,b):
        self._sum(b,self.buf,len(b))
    def __add__(self,o):
        return BFSum(self.start,*(self.parts+[o]))
    def __radd__(self,o):
        return BFSum(o,self.start,*self.parts)
    @staticmethod
    @micropython.asm_thumb
    def _sum(r0,r1,r2):
        label(loop)
        vldr(s1,[r1,0])
        vldr(s0,[r0,0])
        vadd(s0,s0,s1)
        vstr(s0,[r0,0])
        add(r0,4)
        add(r1,4)
        sub(r2,1)
        bgt(loop)
class BFDif(BufFillerFold):
    def __repr__(self):
        return super().__repr__("-")
    def _func(self,b):
        self._dif(b,self.buf,len(b))
    def __sub__(self,o):
        return BFDif(self.start,*(self.parts+[o]))
    @staticmethod
    @micropython.asm_thumb
    def _dif(r0,r1,r2):
        label(loop)
        vldr(s1,[r1,0])
        vldr(s0,[r0,0])
        vsub(s0,s0,s1)
        vstr(s0,[r0,0])
        add(r0,4)
        add(r1,4)
        sub(r2,1)
        bgt(loop)
class BFProd(BufFillerFold):
    def __repr__(self):
        return super().__repr__("*")
    def _func(self,b):
        self._prod(b,self.buf,len(b))
    def __mul__(self,o):
        return BFProd(self.start,*(self.parts+[o]))
    def __rmul__(self,o):
        return BFProd(o,self.start,*self.parts)
    @staticmethod
    @micropython.asm_thumb
    def _prod(r0,r1,r2):
        label(loop)
        vldr(s1,[r1,0])
        vldr(s0,[r0,0])
        vmul(s0,s0,s1)
        vstr(s0,[r0,0])
        add(r0,4)
        add(r1,4)
        sub(r2,1)
        bgt(loop)
class BFQuot(BufFillerFold):
    def __repr__(self):
        return super().__repr__("/")
    def _func(self,b):
        self._quot(b,self.buf,len(b))
    def __sub__(self,o):
        return BFQuot(self.start,*(self.parts+[o]))
    @staticmethod
    @micropython.asm_thumb
    def _quot(r0,r1,r2):
        label(loop)
        vldr(s1,[r1,0])
        vldr(s0,[r0,0])
        vdiv(s0,s0,s1)
        vstr(s0,[r0,0])
        add(r0,4)
        add(r1,4)
        sub(r2,1)
        bgt(loop)



class BFNRR(BufFiller):
    def __init__(self,f,n,d=1):
        super().__init__(f)
        self.args = array('I',[n,d,0,0])
        self.buf = array('f',[])
        self.mv =  memoryview(self.buf)
        self.bufFilled = 0
    def __call__(self,buf): #example: 1/2 goes down an octave
        n,d = self.args[0:2]
        l = len(buf)
        bl = len(self.buf)
        f = 1-((-l*n)//d)
        #(n/d)*l is how much we need
        # f is how much we need max
        if f > bl:
            #expand buf, but if we need more than twice l, do it in multiple stages
            if bl < l and l < f:
                self.buf += array('f',(0 for i in range(l - bl)))
                self.mv = memoryview(self.buf)
                bl = len(self.buf)
            if f > max(bl,l<<1):
                m = memoryview(buf)
                self(m[:l>>1])
                self(m[l>>1:])
                return
            self.buf += array('f',(0 for i in range(f - bl)))
            self.mv = memoryview(self.buf)
        #now make sure it's filled to at least f
        if f > self.bufFilled:
            self.func(self.mv[self.bufFilled:f])
            self.bufFilled = f
        #now do the thing
        d = asm_tools.a_sah_resample(buf,self.buf,self.args,l)>>2
        #copy the rest
        if f!=d:
            self.mv[0:f-d] = self.mv[d:f]
        self.bufFilled -= d
    def __repr__(self):
        return "nrr("+str(self.args[0])+"/"+str(self.args[1])+" "+repr(self.func)+")"
        
        

        

class BufFillerMonop(BufFiller):
    def __init__(self,a=mute):
        self.fill = bfify(a)
    def __call__(self,buf):
        if len(buf):
            self.fill(buf)
            self._func(buf)
    def _func(self,b):
        pass
    def __repr__(self,f="(op ",s=')'):
        return f+repr(self.fill)+s
class BFNeg(BufFillerMonop):
    def __repr__(self):
        return super().__repr__("(-")
    def _func(self,b):
        self._neg(b,b,len(b))
    def __neg__(self):
        return self.fill
    @staticmethod
    @micropython.asm_thumb
    def _neg(r0,r1,r2):
        label(loop)
        vldr(s1,[r1,0])
        vneg(s0,s1)
        vstr(s0,[r0,0])
        add(r0,4)
        add(r1,4)
        sub(r2,1)
        bgt(loop)
class BFSqrt(BufFillerMonop):
    def __repr__(self):
        return super().__repr__("√(")
    def _func(self,b):
        self._sqrt(b,b,len(b))
    @staticmethod
    @micropython.asm_thumb
    def _sqrt(r0,r1,r2):
        label(loop)
        vldr(s1,[r1,0])
        vsqrt(s0,s1)
        vstr(s0,[r0,0])
        add(r0,4)
        add(r1,4)
        sub(r2,1)
        bgt(loop)
class BFFloor(BufFillerMonop):
    def __repr__(self):
        return super().__repr__("int(")
    def _func(self,b):
        self._floor(b,b,len(b))
    @staticmethod
    @micropython.asm_thumb
    def _floor(r0,r1,r2):
        label(loop)
        vldr(s1,[r1,0])
        vcvt_s32_f32(s0,s1)
        vcvt_f32_s32(s0,s0)
        vstr(s0,[r0,0])
        add(r0,4)
        add(r1,4)
        sub(r2,1)
        bgt(loop)
        
        
class BFFilt(BufFillerMonop):
    def __init__(self,f=mute,*bqs):#bq1=filt.biquad_pass,bq2=filt.biquad_pass,bq3=filt.biquad_pass,bq4=filt.biquad_pass):
        self.args = array('f',[0,0,1,0,0,0,0]*4)
        m = memoryview(self.args)
        if len(bqs) > 4:
            i = (len(bqs)//4-((len(bqs)%4)==0))*4
            super().__init__(BFFilt(f,*bqs[:i]))
            bqs = bqs[i:]
        else:
            super().__init__(f)
        self.bqs = [i for i in bqs]
        self.mvs = [m[i*7:(i+1)*7] for i in range(4)]
    def __repr__(self):
        return super().__repr__("filt"+str(len(self.bqs))+"(")
    def filt(self,bq):
        return BFFilt(self.fill,*(self.bqs+[bq]))
    def _func(self,b):
        for i in range(len(self.bqs)):
            self.bqs[i].put(self.mvs[i])
        for i in range(i,4):
            filt.biquad_pass.put(self.mvs[i])
        asm_tools.a_biquads(b,b,self.args,len(b))

class BFSFilt(BufFillerMonop):
    def __init__(self,f=mute,args = None):
        super().__init__(f)
        if args == None:
            self.args = array('f',[0,0,0,0, 0,0,0,0, 1,0,0,1, 0,0,0,0, 0,0,0,0, 0,0, 0,0])
        self.args = args
    def __repr__(self):
        return super().__repr__("sfilt(")
    def _func(self,b):
        if len(b):
            for i in range(20,24):
                if (math.isnan(self.args[i])):
                    self.args[i] = 0
            asm_tools.as_mat_biquad(b,b,self.args,len(b))

                       
class noise(BufFiller):
    def __init__(self,gain=1,offset=0,*bqs):
        self.args = array('f',[offset,gain/(1<<31)]+[0,0,1,0,0,0,0]*4)
        m = memoryview(self.args)
        assert len(bqs) <= 4
        self.bqs = [i for i in bqs]
        self.mvs = [m[2+i*7:2+(i+1)*7] for i in range(4)]
    def gain(self):
        return self.args[1]*(1<<31)
    def offset(self):
        return self.args[0]
    def __repr__(self):
        return "noise(gain="+repr(self.gain())+",offs="+repr(self.offset())+",filts:"+str(len(self.bqs))+")"
    def filt(self,bq):
        if len(self.bqs) < 4:
            return noise(self.gain(),self.offset(),*(self.bqs+[bq]))
        return super().filt(bq)
    def __call__(self,buf):
        if len(buf):
            for i in range(len(self.bqs)):
                self.bqs[i].put(self.mvs[i])
            for i in range(i,4):
                filt.biquad_pass.put(self.mvs[i])
            asm_tools.a_filtered_noise(buf,self.args,len(buf))
