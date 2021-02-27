#basically bfTools for the new assembler

#intermediate forms (stereo & mono versions for each (actually probably just n-channel)):
# size
#  32  float           (1.8.23)
#  16  halffloat       (1.5.10)
### 8  a-law           (1.3.4 (+.5 ulp))
### 8  µ-law           (1.3.4 (+33, no subnormal))
#   8  minifloat       (1.3.4) instead of a-law or mu-law
#  32  int / fixed pt
#  16  half 
#   8  byte

#operations:
# 1-op:
#   sqrt, scale, add const, abs, etc
#   channel remap (m->n matrix mult?),
#   convert between types,
#   bit-convert between types (nop),
#   filter,
#   resample, ...
# 2-op:
#   add/sub / mul/div/mod ...
#   and, or, xor, bic,

from array import array
import struct
from small_floats import *
TYPECODE_LENGTHS = {'b':1,'B':1,'mf':1,
                    'h':2,'H':2,'hf':2,
                    'i':4,'I':4, 'f':4,
                    }
def typecode_size(tc):
    if tc in TYPECODE_LENGTHS:
        return TYPECODE_LENGTHS[tc]
    raise Exception("Unknown typecode "+repr(tc))

def address(buf):
    return underlying_bytes(buf)
def typecode(buf):
    if type(buf) is tarray:
        return buf.type
    elif type(buf) is memoryview:
        return buf.format
    elif type(buf) is array:
        return buf.typecode
    elif type(buf) is bytearray:
        return 'B'
    else:
        raise Exception("Unknown buffer type "+repr(buf))

def underlying_bytes(buf):
    if type(buf) is tarray:
        return buf.buf
    else:
        return memoryview(buf).cast('B')

    
def conv_to_pythonic(buf,tc):
    if len(tc) < 2:
        return struct.unpack(tc,buf)[0]
    if tc == 'hf':
        return halffloat(struct.unpack('H',buf)[0],1)
    elif tc == 'mf':
        return minifloat(struct.unpack('B',buf)[0],1)
    else:
        raise Exception("Unknown typecode "+repr(tc))

def conv_from_pythonic(v,tc,dest=None,offs=0):
    if len(tc) < 2:
        if dest is None:
            return struct.pack(tc,v)
        return struct.pack_into(tc,dest,offs,v)
    if tc == 'hf':
        if dest is None:
            return struct.pack('H',halffloat(v).v)
        return struct.pack_into('H',dest,offs,halffloat(v).v)
    elif tc == 'mf':
        if dest is None:
            return struct.pack('B',minifloat(v).v)
        return struct.pack_into('B',dest,offs,minifloat(v).v)
    else:
        raise Exception("Unknown typecode "+repr(tc))
    
class tarray:
    def __init__(self,buf,typec=None,copy=False):
        if copy:
            init = buf
            buf = len(init)
        else:
            init = None
        if type(buf) is int:
            assert typec != None#need to declare type when giving length to init
            buf = bytearray(typecode_size(typec)*buf)
            self.btype = 'B'
        elif type(buf) is list:#convert to bytes_like
            init = buf
            buf = bytearray(typecode_size(typec)*len(buf))
            self.btype = 'B'
        else:
            self.btype = typecode(buf)
        self.type = btype if typec is None else typec
        self.type_length = typecode_size(self.type)
        self.buf = underlying_bytes(buf)
        self.byte_length = len(buf)
        assert self.byte_length%typecode_size(self.type) == 0#buffer byte length must be integer multiple of type byte length
        self.length = self.byte_length//typecode_size(self.type)
        if init is not None:
            for i in range(len(init)):
                self[i] = init[i]
    def __len__(self):
        return self.length
    def __getitem__(self,i):
        if type(i) is slice:
            assert False #unimplemented
        else:
            i %= len(self)
            return conv_to_pythonic(self.buf[self.type_length*i:self.type_length*(i+1)],self.type)
    def __setitem__(self,i,v):
        if type(i) is slice:
            assert False #unimplemented
        else:
            i %= len(self)
            conv_from_pythonic(v,self.type,self.buf,self.type_length*i)
    def __iter__(self):
        i = 0
        while i < self.length:
            yield self[i]
            i += 1
    REPR_LEN = 16
    def __repr__(self):
        if len(self) > self.REPR_LEN:
            h = self.REPR_LEN//2
            t = self.REPR_LEN - h
            return "tarray{"+self.type+"}(len="+str(len(self))+")["+', '.join((repr(self[i]) for i in range(h)))+",..., "+\
                ', '.join((repr(self[i-t]) for i in range(t))) + "]"
        return "tarray{"+self.type+"}["+', '.join((repr(v) for v in self))+"]"
    
        







#### CALLING CONVENTIONS ####
# types of routines:
#   processing loops: (exit to python)
#     restore r8 and up, all sn
#   conversion to float:
#     callee save: r0-r3
#     arg: r4, result:r4 
"""
from asm import *
from assembler import *

def mini_to_int(a):#mini to int (then do to float)
    ubfx(a,5,4,4,3)#exponent field
    ubfx(a,6,4,0,4)#mantissa field
    #check if exp = 0
    #if not, mant |= 0x10
    
    
    
    
OB
"""
                
