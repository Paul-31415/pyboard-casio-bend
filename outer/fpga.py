
import pyb

class file_with_buffer_protocol:
    def __init__(self,f):
        self.f = f
    



class FPGA:
    def __init__(self): #hardcoded pins, sorry
        self.power = pyb.Pin("X19",mode = pyb.Pin.OUT)
        self.spi = pyb.SPI(2)
        self.alt1 = pyb.Pin("Y1") #23
        self.hold = pyb.Pin("Y2") #SPI_IO3
        self.rst = pyb.Pin("Y3")  #rst
        self.cs = pyb.Pin("Y4")   #cs
        self.alt2 = pyb.Pin("Y5") #24 (soft ss)
        self.sclk = pyb.Pin("Y6")
        self.miso = pyb.Pin("Y7")
        self.mosi = pyb.Pin("Y8")
        #self.cdone = pyb.Pin("X?") not exposed on fpga bx
    def detach(self):
        self.spi.deinit()
        for p in (self.alt1,self.alt2,self.cs,self.rst,self.hold,self.sclk,self.miso,self.mosi):
            p.init(pyb.Pin.IN,pull=pyb.Pin.PULL_NONE)
    def off(self):
        #depower all pins before power to avoid eov
        self.detach()
        self.power(0)
    def on(self):
        #turns on the fpga
        self.power(1)
    def load(self,f=None):
        self.on()
        self.rst.init(pyb.Pin.OUT_OD)
        self.rst(0)
        self.spi.init(pyb.SPI.MASTER,polarity=1,firstbit=pyb.SPI.MSB,phase=1,prescaler=16)
        if f != None:
            self.cs.init(pyb.Pin.OUT_OD)
            self.cs(0)
            pyb.udelay(1) #≥200ns
            self.rst(1)
            self.hold.init(pyb.Pin.OUT_OD)
            self.hold(0)#avoid talking to the flash for now
            pyb.udelay(1200)
            self.cs(1)
            b = bytearray(1)
            self.spi.send(b)
            self.cs(0)
            while f.readinto(b):
                self.spi.send(b)
            self.cs(1)
            self.hold(1)#ok we can talk to flash if we want
            self.spi.send(b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0')
        else:
            pyb.udelay(1)
            self.rst(1)
        self.spi.deinit()
    def soft_load(self,f=None): #uses software spi
        self.on()
        self.rst.init(pyb.Pin.OUT_OD)
        self.rst(0)
        if f != None:
            self.hold.init(pyb.Pin.OUT_OD)
            self.hold(0)#avoid talking to the flash for now
            self.sclk.init(pyb.Pin.OUT_PP)
            self.sclk(0)
            self.miso.init(pyb.Pin.IN,pull=pyb.Pin.PULL_UP)
            self.mosi.init(pyb.Pin.OUT_PP)
            self.mosi(0)
            self.cs.init(pyb.Pin.OUT_OD)
            self.cs(0)
            self.sclk(1)
            pyb.udelay(1) #≥200ns
            self.rst(1)
            pyb.udelay(1200)
            #send 8 dummy clocks:
            self.cs(1)
            for i in range(8):
                self.sclk(0)
                self.sclk(1)
            self.cs(0)
            #send file
            b = bytearray(1)
            while f.readinto(b):
                v = b[0]
                for i in range(8):
                    self.mosi(v&0x80 != 0)
                    self.sclk(0)
                    v <<= 1
                    self.sclk(1)
            #done
            self.mosi(0)
            for i in range(200):
                self.sclk(0)
                self.sclk(1)
            self.cs(1)
        else:
            pyb.udelay(1)
            self.rst(1)
    @micropython.viper
    def viper_load(self,f): #uses software spi
        self.on()
        self.rst.init(pyb.Pin.OUT_OD)
        self.rst(0)

        self.hold.init(pyb.Pin.OUT_OD)
        self.hold(0)#avoid talking to the flash for now
        self.sclk.init(pyb.Pin.OUT_PP)
        self.sclk(0)
        self.miso.init(pyb.Pin.IN,pull=pyb.Pin.PULL_UP)
        self.mosi.init(pyb.Pin.OUT_PP)
        self.mosi(0)
        self.cs.init(pyb.Pin.OUT_OD)
        self.cs(0)
        self.sclk(1)
        pyb.udelay(1) #≥200ns
        self.rst(1)
        pyb.udelay(1200)
        #send 8 dummy clocks:
        b = bytearray(1)
        bp = ptr8(b)
        out = ptr16(stm.GPIOB+stm.GPIO_ODR)
        clock_mask = const(1<<13)
        mosi_mask = const(1<<15)
        cs_mask = const(1<<9)
        out[0] ^= cs_mask
        for i in range(16):
            out[0] ^= clock_mask
        out[0] ^= cs_mask
        #send file
        while f.readinto(b):
            v = bp[0]
            for i in range(8):
                if v&0x80:
                    out[0] |= mosi_mask
                else:
                    out[0] &= ~mosi_mask
                out[0] ^= clock_mask
                v <<= 1
                out[0] ^= clock_mask
        #done
        out[0] &= ~mosi_mask
        for i in range(400):
            out[0] ^= clock_mask
        out[0] ^= cs_mask
        

fpga = FPGA()
        
        
        
#fpga_init = b'\xE4\xff'


#
