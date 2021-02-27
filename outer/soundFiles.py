from array import array
from bfTools import BufFiller,mute
import asm_tools


class sfile(BufFiller):
    def __init__(self,n):
        f = open(n,'rb')
        self.name = n
        self.file = soundfileParser(f,n)
        self.func = self.file
    def seek(self,*a):
        return self.file.seek(*a)
    def tell(self,*a):
        return self.file.tell(*a)
    def __repr__(self):
        return "sfile"
        

class sraw(BufFiller):
    def __init__(self,f,fn):
        self.file = f
        self.func = fn
    def seek(self,*a):
        return self.file.seek(*a)
    def tell(self,*a):
        return self.file.tell(*a)
    def __repr__(self):
        return "sraw"
    
def soundfileParser(f,n):
    if n[-4:] == ".hfs":
        return sraw(f,fileNb(f))
    if n[-4:] == ".8bm":
        return sraw(f,fileNb(f,1,asm_tools.a_u8_to_float))
    if n[-5:] == ".16bm":
        return sraw(f,fileNb(f,2,asm_tools.a_s16_to_float))
    raise Exception("unknown file type")

"""
def file8b(f,bl = 512):
    b = bytearray(bl)
    def fill(arr,a=[b,0,f]):
        dm = memoryview(arr)
        bm = memoryview(a[0])
        while len(dm):
            if a[1] == 0:
                a[1] = a[2].readinto(a[0])
                if a[1] == 0:
                    return
            l = min(len(dm),a[1])
            a[1] -= l   
            asm_tools.a_u8_to_float(bm,dm,l)
            bm = bm[l:]
            dm = dm[l:]
    return fill
def file16b(f,bl = 512):
    b = array('h',bytearray(bl<<1))
    def fill(arr,a=[b,0,f]):
        amt = len(arr)
        while amt > 0:
            if a[1] == 0:
                a[1] = a[2].readinto(a[0]) >> 1
                if a[1] == 0:
                    return
            l = min(amt,a[1])
            a[1] -= l
            asm_tools.a_s16_to_float(a[0],arr,l,(len(arr)-amt)*4)
            amt -= l
    return fill
"""

def fileNb(f,n=2,rout=asm_tools.a_half_to_float,bl = 512):
    b = bytearray(bl*n)
    def fill(arr,a=[b,0,f]):
        dm = memoryview(arr)
        sm = memoryview(a[0])
        while len(dm):
            if a[1] == 0:
                a[1] = a[2].readinto(a[0]) // n
                if a[1] == 0:
                    #zero pad to avoid ear rape on filters whose dest is arr
                    mute(dm)
                    return
            l = min(len(dm),a[1])
            rout(sm,dm,l)
            sm[:(a[1]-l)*n] = sm[l*n:a[1]*n]
            a[1] -= l
            dm = dm[l:]
    return fill

