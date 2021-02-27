import math

from array import array

def mag2(z):
    if type(z) == complex:
        return z.real*z.real+z.imag*z.imag
    return z*z
def angle(z):
    return math.atan2(z.imag,z.real)
def quadRoots(a,b,c):
    return -b/(2*a)+(b*b-4*a*c)**.5/(2*a),-b/(2*a)-(b*b-4*a*c)**.5/(2*a)

class biquad:
    def __init__(self,b0=1,b1=0,b2=0,a1=0,a2=0):
        self.a = array('f',[a1,a2])
        self.b = array('f',[b0,b1,b2])
    def put(self,dest):
        dest[0:2] = self.a
        dest[2:5] = self.b
        if math.isnan(dest[5]):
            if math.isnan(dest[6]):
                dest[5:7] = array('f',[0,0])
            else:
                dest[5] = 0
        elif math.isnan(dest[6]):
            dest[6] = 0
    def zeros(self):
        return quadRoots(*self.b)
    def poles(self):
        return quadRoots(1,*self.a)
    def gain(self,z):
        n = (self.b[2]*z+self.b[1])*z+self.b[2]
        d = (self.a[1]*z+self.a[0])*z+1
        return n/d
    def fgain(self,f=None):
        if f==None:
            p = self.poles()[0]
            return max(self.gain(1),self.gain(-1),self.gain(p/abs(p) if p != 0 else 1),key=mag2)
        z = math.e**(1j*f)
        return self.gain(z)
    
biquad_pass = biquad()


def biquadCoeffs(pfreq,pmag,zfreq,zmag,gain,sr=48000):
    pfreq *= 2*math.pi/sr
    zfreq *= 2*math.pi/sr
    #(x-ae^iw) -> x^2-2x*a*cos(w)+a^2
    return -2*math.cos(pfreq)*pmag,pmag*pmag,\
        gain,-gain*2*math.cos(zfreq)*zmag,gain*zmag*zmag
def biquadFromPZ(pole,zero,gain):
    #(x-pole) -> x^2-2x*pole.real+|pole|^2
    return -2*pole.real,(pole*pole.conjugate()).real,\
        gain,-2*gain*zero.real,gain*(zero*zero.conjugate()).real

def storeBiquadCoeffs(pfreq,pmag,zfreq,zmag,gain,where,offs=0,sr=48000):
    pfreq *= 2*math.pi/sr
    zfreq *= 2*math.pi/sr
    
    a1,a2,b1,b2 = -2*math.cos(pfreq)*pmag, pmag*pmag,-2*math.cos(zfreq)*zmag, zmag*zmag
    
    dcg = (1+b1+b2)/(1+a1+a2)
    nfg = (1-b1+b2)/(1-a1+a2)
    pc = math.e**(1j*pfreq)
    pg = (1+b1*pc+b2*pc*pc)/(1+a1*pc+a2*pc*pc)
    maxg = max(abs(dcg),abs(nfg),abs(pg))
    gain /= maxg
    
    #(x-ae^iw) -> x^2-2x*a*cos(w)+a^2
    where[offs]   = a1
    where[offs+1] = a2
    where[offs+2] = gain
    where[offs+3] = gain*b1
    where[offs+4] = gain*b2



