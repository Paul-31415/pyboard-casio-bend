import pyb
class Spi:
    def __init__(self,clk,mosi,miso,falses=[1,0,0]):
        self.clk = clk
        self.mosi = mosi
        self.miso = miso
        self.f = falses
    def examine(self,n=8,delay=1000):
        arr = []
        for i in range(n):
            self.clk(self.f[0])
            pyb.udelay(delay)
            arr += [(self.clk(),self.mosi(),self.miso())]
            self.clk(not self.f[0])
            pyb.udelay(delay)
            arr += [(self.clk(),self.mosi(),self.miso())]
        return arr
    def sendBits(self,bits,delay = 10000):
        r = []
        for b in bits:
            self.clk(self.f[0])
            self.mosi(self.f[1]^b)
            r += [self.miso()]
            pyb.udelay(delay)
            self.clk(not self.f[0])
            pyb.udelay(delay)
        return r
    def sendBytes(self,byts,delay=1000):
        r = self.sendBits(((b&(1<<i))!=0 for b in byts for i in range(7,-1,-1)),delay)
        return [sum((r[i+j]<<(7-j) for j in range(8))) for i in range(0,len(r),8)]

    def allign(self,delay=1000):
        while sendBits([0],delay)[0] != 1:
            pass
    def sendCmd(self,cmd=0xcd,argstr = "0",extra=[],delay=1000):
        self.allign(delay)
        self.sendBytes([cmd],delay)
        pyb.udelay(delay)
        if argstr != None:
            l = len(argstr)
            self.sendBytes([(l>>(8*i))&0xff for i in range(4)],delay)
            pyb.udelay(delay)
            self.sendBytes([ord(c) for c in argstr],delay)
            pyb.udelay(delay)
        return self.sendBytes(extra,delay)
