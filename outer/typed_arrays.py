from array import array

class FloatArray:
    def __init__(self,a):
        #a is an array or a writeable memoryview
        #elements better be 4 bytes in size
        self.a = a
    def __len__(self):
        return len(self.a)
    def __add__(self,o):
        assert len(self) == len(o)
        if type(o) == FloatArray:
            a_floatAdd(self.a,self.a,o.a,len(self.a))

        
        
@micropython.asm_thumb
def a_floatAdd(r0,r1,r2,r3):
    cmp(r3,0)
    beq(end)
    label(loop)
    vldr(s0,[r1,0])
    add(r1,4)
    vldr(s1,[r2,0])
    add(r2,4)

    vadd(s0,s0,s1)
    
    vstr(s0,[r0,0])
    add(r0,4)
    sub(r3,1)
    bne(loop)
    label(end)
