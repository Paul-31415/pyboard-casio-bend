import pyb
import asm_tools
import math
import micropython
import gc
from bftools import mute
from array import array

class Mix:
    def __init__(self,l=512):
        self.out = lambda x:0
        self.rate = 1
        self._outHBuf1 = array('H',(0 for i in range(l*2)))
        self._outHBuf2 = array('H',self._outHBuf1)
        self._outHTop1 = memoryview(self._outHBuf1)[l:]
        self._outHTop2 = memoryview(self._outHBuf2)[l:]
        self._outFBuf = array('f',self._outHBuf1) #*2 for stereo
        self._outFShift = memoryview(self._outFBuf)[1:]
        self.dac_timer = pyb.Timer(6)#16 bit counter has enough accuracy
        self.buf_timer = pyb.Timer(5)#32 bit for callback
        self.dac1 = pyb.DAC(1,bits=12)
        self.dac2 = pyb.DAC(2,bits=12)
        self._phase = 0
        self.error = None
        self._buffArgs1 = array('f',[0,4095,2048, 0,0,1,0,0,0,0, 0,0,1,0,0,0,0, 0,0,1/(1<<32),0,0,0,0,.9,0, 0])
        self._buffArgs2 = array('f',[0,4095,2048, 0,0,1,0,0,0,0, 0,0,1,0,0,0,0, 0,0,1/(1<<32),0,0,0,0,.9,0, 0])
        self._nanInds = [8,9,15,16,22,23,25]
        self.underrun = 0
    def denan(self):
        for i in self._nanInds:
            if math.isnan(self._buffArgs1[i]):
                self._buffArgs1[i] = 0
            if math.isnan(self._buffArgs2[i]):
                self._buffArgs2[i] = 0
    def update(self):
        pyb.rng()
        self.buf_timer.callback(None)
        self.dac_timer.prescaler(65535)
        self.dac_timer.period(65535)
        self.dac_timer.counter(0)
        self.dac1.init(bits=12)
        self.dac2.init(bits=12)
        self.dac1.write_timed(self._outHBuf1,self.dac_timer,mode=pyb.DAC.CIRCULAR)
        self.dac2.write_timed(self._outHBuf2,self.dac_timer,mode=pyb.DAC.CIRCULAR)
        self.dac_timer.init(freq=self.rate)
        self.buf_timer.init(prescaler=self.dac_timer.prescaler(),\
                            period=(self.dac_timer.period()+1)*(len(self._outFBuf)//2)-1)
        self.buf_timer.callback(self._fillbuf)
        self._phase = 0
        self.ready = True
    def _fillbuf(self,tim):
        asm_tools.s_conv(self._outHTop1 if self._phase else self._outHBuf1,
                         self._outHTop2 if self._phase else self._outHBuf2,
                         self._outFBuf,self._outFShift,self._buffArgs1,self._buffArgs2)
        self._phase ^= 1
        if self.ready:
            self.ready = False
            micropython.schedule(_mix_fillbuf,None)
        else:
            self.underrun += 1
    def stop(self):
        self.buf_timer.callback(None)
        self.dac1.deinit()
        self.dac2.deinit()
        
def _mix_fillbuf(a):
    try:
        mix.out(mix._outFBuf)
    except Exception as e:
        mix.error = e
        mix.out = mute
        mix.out(mix._outFBuf)
    mix.denan()
    mix.ready = True
    gc.collect()        
        

mix = Mix()
update = mix.update
    
micropython.alloc_emergency_exception_buf(256)
