#
from array import array
#notes:
#with the fpv4:
#  no VSEL, VMAXNM, VMINNM, VCVTA, VCVTN, VCVTP, VCVTM, VRINTA, VRINTN, VRINTP, VRINTM, VRINTZ, VRINTR
#  no double precision opcodes

#sp = r13?
#lr = r14
#pc = r15



@micropython.asm_thumb
def addr(r0):
    pass

class AsmLen:
    def __init__(self):
        self.l = 0
    def __len__(self):
        return self.l
    def write(self,v):
        self.l += 1
    def pc(self):
        return self.l*2
class AsmCode:
    pyArgPass = array('I',[0,0,0,0])
    def __init__(self,l):
        if type(l) == int:
            self.content = array('H',[0])*l
        else:
            self.content = l
        assert (self.addr()&1)==0
        self.pos = 0
        self.ready = False
    def __len__(self):
        return len(self.content)
    def remaining(self):
        return len(self)-self.pos
    def write(self,v):
        self.content[self.pos] = v
        self.pos += 1
    def addr(self):
        return addr(self.content)
    def pc(self):
        return self.addr()+2*self.pos
    def split(self):
        #cuts self off at pos and makes a new asmcode object
        m = memoryview(self.content)
        self.content = m[:self.pos]
        return AsmCode(m[self.pos:])
    def __call__(self,r0=0,r1=0,r2=0,r3=0):
        assert self.ready
        AsmCode.pyArgPass[0] = addr(r0)
        AsmCode.pyArgPass[1] = addr(r1)
        AsmCode.pyArgPass[2] = addr(r2)
        AsmCode.pyArgPass[3] = addr(r3)
        self._call(AsmCode.pyArgPass,self.content)
    @staticmethod
    @micropython.asm_thumb
    def _call(r0,r1):
        b(start)
        label(call)
        bx(r4)
        label(start)
        mov(r4,r1)
        ldr(r3,[r0,12])
        ldr(r2,[r0,8])
        ldr(r1,[r0,4])
        ldr(r0,[r0,0])
        bl(start)

def asm(func):
    l = AsmLen()
    func(l)
    c = AsmCode(len(l))
    func(c)
    return c




def sign_extend(n,bits=8):
    return (n&((1<<(bits-1))-1))|(-(n&(1<<(bits-1))))




#conditions:           flags
# 0000   EQ              z (zero)
# 0001   NE             nz
# 0010   CS              c (carry)
# 0011   CC             nc
# 0100   MI              s (negative)
# 0101   PL             ns
# 0110   VS              v (overflow)
# 0111   VC             nv
# 1000   HI             c,nz
# 1001   LS            nc,z
# 1010   GE             s=v
# 1011   LT             s^v
# 1100   GT             nz,s=v
# 1101   LE             ~GT
# 1110   AL (don't use in IT instructions)


#all these branches go to 2-byte alligned locations (so all the imms are in units of halfwords)
def b8(dest,cond,imm8):
    assert imm8 == sign_extend(imm8,8)
    dest.write(0xd000|(cond<<8)|(imm8&0xff))
def b11(dest,imm11):#use at end of it block for cond
    assert imm11 == sign_extend(imm11,11)
    dest.write(0xe000|(imm11&0x7ff))
def b20(dest,cond,imm20):
    assert imm20 == sign_extend(imm20,20)
    imm20 &= 0xfffff
    imm11 = imm20&0x7ff
    imm6 = (imm20>>11)&0x3f
    j1 = (imm20>>17)&1
    j2 = (imm20>>18)&1
    S = (imm20>>19)
    dest.write(0xf000|imm6|(cond<<6)|(S<<10))
    dest.write(0x8000|imm11|(j2<<11)|(j1<<13))
def b24(dest,imm24):#use at end of it block
    assert imm24 == sign_extend(imm24,24)
    imm24 &= 0xffffff
    imm11 = imm24&0x7ff
    imm10 = (imm24>>11)&0x3ff
    I2 = (imm24>>21)&1
    I1 = (imm24>>22)&1
    S = imm24>>23
    J1 = (~I1)^S
    J2 = (~I2)^S
    dest.write(0xf000|imm10|(S<<10))
    dest.write(0x9000|imm11|(J2<<11)|(J1<<13))
def bl(dest,imm24):#use at end of it block
    assert imm24 == sign_extend(imm24,24)
    imm24 &= 0xffffff
    imm11 = imm24&0x7ff
    imm10 = (imm24>>11)&0x3ff
    I2 = (imm24>>21)&1
    I1 = (imm24>>22)&1
    S = imm24>>23
    J1 = (~I1)^S
    J2 = (~I2)^S
    dest.write(0xf000|imm10|(S<<10))
    dest.write(0xd000|imm11|(J2<<11)|(J1<<13))
def blx(dest,reg):#branch to reg subroutine, for conditional, put at end of it block
    dest.write(0x4780|(reg<<3))
def bx(dest,reg):#branch to reg, for conditional, put at end of it block
    dest.write(0x4700|(reg<<3))
    
# mask looks like this:
#             let c = cond&1
#             let n = not c
#          for it: mask = 1000
#        for itet: mask = nc10
#       for ittee: mask = cnn1
# since cond | 1 is opposite of cond & 14,
#  it can be seen as
#      if (else|then) x (1-4)
#     with cond[0] being first clause
#         and only even conds allowed
def it(dest,cond,mask):
    dest.write(0xbf00|(cond<<4)|mask)
    

#Floating point stuff
# supported by pyb asm:
#  vadd,vsub,vneg,vmul,vdiv,vsqrt, vmov between r and s,vmrs, vldr, vstr, vcmp, vcvt between float and 32 bit int
# fp instructions not supported:
# (it looks like half precision is just rounded to or converted from (using vcvtb), it's not used as an internal representation)
# vabs,vcmp with 0,vcmpe,vcvt,vcvtr,vcvtb,vcvtt,vdiv,vfma,vfms,vfnma,vfnms,vmla,vmls,vmov,vmul,vneg,vnmla,vnmls,vnmul,vsqrt,vsub
def v3arg(dest,p0=0,p1=0,Sd=0,Sm=0,Sn=0):
    dest.write(p0|((Sd&1)<<6)|(Sn>>1))
    dest.write(p1|((Sd&0x1e)<<11)|((Sm&1)<<5)|(Sm>>1)|((Sn&1)<<7))
# vabs:                      sz-. is 0 because no double
#  1110 1110 1D11 0000  dddd 1010 11M0 mmmm
#    sddddD = |smmmmM|
def vabs(dest,Sd,Sm):
    v3arg(dest,0xeeb0,0x0ac0,Sd,Sm)
# vadd:
#  1110 1110 0D11 nnnn  dddd 1010 N0M0 mmmm (pyb has this)
#    sd = sn+sm
def vadd(dest,Sd,Sm,Sn):
    v3arg(dest,0xee30,0x0a00,Sd,Sm,Sn)
# vcmp:
#  1110 1110 1D11 0100  dddd 1010 E1M0 mmmm (pyb has this version)
def vcmp(dest,Sd,Sm,E=0):
    v3arg(dest,0xeeb4,0x0a40|(E<<7),Sd,Sm)
#  1110 1110 1D11 0101  dddd 1010 E1O0 OOOO where O is (0)
#   cmp with 0
#    E is whether any nan should throw or just loud ones (1 for any)
def vcmp0(dest,Sd,E=0):
    v3arg(dest,0xeeb5,0x0a40|(E<<7),Sd)
# vcvt:
#  1111 1110 1D11 1op2  dddd 1010 o1M0 mmmm
def vcvt(dest,Sd,Sm,op,round_to_0=False):
    v3arg(dest,0xfeb8|op,0x0a40|(round_to_0<<7),Sd,Sm)
#   op2 = 101 is vcvt_s32_f32(Sd,Sm) (pyb has this)
#    o is whether to use rounding towards 0 (1) or the FPSCR specified mode (0)
def vcvt_s32_f32(dest,Sd,Sm):
    vcvt(dest,Sd,Sm,5)
#   op2 = 100 is vcvt_u32_f32(Sd,Sm)
#    o is same as above
def vcvt_u32_f32(dest,Sd,Sm):#use specified round
    vcvt(dest,Sd,Sm,4)
#   op2 = 000 is vcvt_f32_(Tm)(Sd,Sm)     ddddD, mmmmM
#                           ^- [u32,s32][o]
def vcvt_f32_u32(dest,Sd,Sm):
    vcvt(dest,Sd,Sm,0,0)
def vcvt_f32_s32(dest,Sd,Sm):
    vcvt(dest,Sd,Sm,0,1)
#  1110 1110 1D11 1o1U  dddd 1010 x1i0 imm4
#   conv between floating and fixed point
#    unsigned = U, reg is ddddD (converts in place)
#    size = [16,32][x]
#    frac_bits = size-(imm4:i)
#      unpredictable if frac_bits < 0
#    o is direction of conversion (1 for to fixed)
def vcvt_f32_fixed32(dest,Sd,fix=0,unsigned=0):
    v3arg(dest,0xeeba|unsigned,0x0ac0,Sd,fix)
def vcvt_fixed32_f32(dest,Sd,fix=0,unsigned=0):
    v3arg(dest,0xeebe|unsigned,0x0ac0,Sd,fix)
def vcvt_f32_fixed16(dest,Sd,fix=0,unsigned=0):
    v3arg(dest,0xeeba|unsigned,0x0a40,Sd,fix)
def vcvt_fixed16_f32(dest,Sd,fix=0,unsigned=0):
    v3arg(dest,0xeebe|unsigned,0x0a40,Sd,fix)
#    
# vcvtb and vcvtt: (convert bottom and top between half and single prec)
#  1110 1110 1D11 001o  dddd 1010 T1M0 mmmm
#   half to single is o = 0, single to half is o = 1
#   T is 1 for vcvtt and 0 for vcvtb
#   sddddD, smmmmM
def vcvtb(dest,Sd,Sm,toHalf=1):
    v3arg(dest,0xeeb2|toHalf,0x0a40,Sd,Sm)
def vcvtt(dest,Sd,Sm,toHalf=1):
    v3arg(dest,0xeeb2|toHalf,0x0ac0,Sd,Sm)
# vdiv: pyb has this
#  1110 1110 1D00 nnnn  dddd 1010 N0M0 mmmm
def vdiv(dest,Sd,Sm,Sn):
    v3arg(dest,0xee80,0x0a00,Sd,Sm,Sn)
# vfma vfms:
#  1110 1110 1D10 nnnn  dddd 1010 NoM0 mmmm
#    sddddD ±= snnnnN*smmmmM
#           o = 1 for sub
def vfma(dest,Sd,Sm,Sn):
    v3arg(dest,0xeea0,0x0a00,Sd,Sm,Sn)
def vfms(dest,Sd,Sm,Sn):
    v3arg(dest,0xeea0,0x0a40,Sd,Sm,Sn)
# vfnma vfnms:
#  1110 1110 1D01 nnnn  dddd 1010 NoM0 mmmm
#    sddddD = -sddddD + ((-snnnnN)*smmmmM)   : o = 1
#    sddddD = -sddddD + ((snnnnN)*smmmmM)    : o = 0
#    basically fm(a/s) followed by vneg(Sd,Sd)
def vfnma(dest,Sd,Sm,Sn):
    v3arg(dest,0xee90,0x0a00,Sd,Sm,Sn)
def vfnms(dest,Sd,Sm,Sn):
    v3arg(dest,0xee90,0x0a40,Sd,Sm,Sn)
# vldm: floating point load multiple 
#  1110 110P UDW1 nnnn  dddd 1011 [imm8   ]
#    PUW == 011 and n = 1101 is vpop
#    PW = 10 is vldr
#    imm0<0> == 1 is fldmx
#    PW = U1 is undefined
#    valid: PUW = 010, 011, 101
#     U is add
#     W is write-back
#     Sd is Ddddd (!) because this is the double prec variant
#  1110 110P UDW1 nnnn  dddd 1010 [imm8   ]
#    Sd = ddddD, Rn = nnnn
#    regs = imm8
#    PU = 01 is the mem starts at (Rn) and goes up
#    PU = 10 is the mem starts at (Rn-1) and goes down
#    W is required for descending
#     it makes the instruction modify Rn
#    imm8 is how many to read into Sd,S(d+1),S(d+2)..., (note that it is undefined if it has to wrap S(d+i8))
#      has to have at least 1
def vldm(dest,Sd,Rn,num):
    v3arg(dest,0xec90,0x0a00|num,Sd,0,Rn<<1)
# vldr: pyb has this
#  1110 1101 UD01 nnnn  dddd 1010 [imm8   ]
def vldr(dest,Sd,Rn,offs=0):
    v3arg(dest,0xed10|((offs>=0)<<7),0x0a00|(offs&0xff),Sd,0,Rn<<1)
# vmla/s:
#  1110 1110 0D00 nnnn  dddd 1010 NoM0 mmmm
#   o=0 is a, o=1 is s
#   same as fma, fms, but it rounds the multiply
def vmla(dest,Sd,Sm,Sn):
    v3arg(dest,0xee00,0x0a00,Sd,Sm,Sn)
def vmls(dest,Sd,Sm,Sn):
    v3arg(dest,0xee00,0x0a40,Sd,Sm,Sn)
# vmov imm:
#  1110 1110 1D11 aaaa  dddd 1010 O0O0 bbbb (O is (0))
#   imm8 = aaaabbbb -> abcdefgh
#   SddddD = aBbbbbbcd efgh0000000000000000000
#     i.e. you can specify sign, exp between 01111100 and 10000011, and 4 msbits of the mantissa
#     so: ± 1/8 to ±31 (last ones in steps of 1)
#     kinda like reading imm8 as a seeemmmm tinyfloat with no inf/nan or denormal
def vmov_imm(dest,Sd,imm8):
    if type(imm8) == float:
        v = imm8
        imm8 = addr(imm8)
        ab = (imm8>>30)^1
        cdefgh = (imm8>>19)&0x3f
        re = ((ab^1)<<30)|((ab&1)*0x3e000000)|(cdefgh<<19)
        if re != imm8:
            raise Exception("unencodeable immediate float",v)
        imm8 = (ab<<6)|cdefgh
    v3arg(dest,0xeeb0|(imm8>>4),0x0a00|(imm8&0xf),Sd)
# vmov reg:
#  1110 1110 1D11 0000  dddd 1010 01M0 mmmm
#   SddddD = SmmmmM
def vmov_ss(dest,Sd,Sm):
    v3arg(dest,0xeeb0,0x0a40,Sd,Sm)
# vmov R to S and S to R: pyb has this
#  1110 1110 000o dddd  tttt 1010 D001 0000
# o = 1 is s to r, 0 is r to s
def vmov_sr(dest,Sd,Rn):
    v3arg(dest,0xee00,0x0a10,Sd,0,Rn<<1)
def vmov_rs(dest,Sd,Rn):
    v3arg(dest,0xee10,0x0a10,Sd,0,Rn<<1)
# vmov 2 at once:
#  1110 1100 010o bbbb  aaaa 1010 00M1 mmmm
#   to R is o=1, from is o=0
#   m = 31 is unpredictable (as are 13 or 15 as a or b), the S regs have to be consequative
#   SmmmmM = Ra; S(mmmmM+1) = Rb   for o = 0
def vmov2_sr(dest,Ra,Sm,Rb):
    v3arg(dest,0xec40,0x0a10,Ra<<1,Sm,Rb<<1)
def vmov2_rs(dest,Ra,Sm,Rb):
    v3arg(dest,0xec50,0x0a10,Ra<<1,Sm,Rb<<1)
# The flags move one can also move flags to an R reg: pyb has this.
def vmrs_r_FPSCR(dest,R=15):
    v3arg(dest,0xeef1,0x0a10,0,0,R)
# and the other way (can't move APSR, R shouldn't be 13 or 15)
def vmrs_FPSCR_r(dest,R):
    v3arg(dest,0xeee1,0x0a10,0,0,R)
# vmul: pyb has this
#  1110 1110 0D10 nnnn  dddd 1010 N0M0 mmmm
def vmul(dest,Sd,Sm,Sn):
    v3arg(dest,0xee20,0x0a00,Sd,Sm,Sn)
# vneg: pyb has this
#  1110 1110 1d11 0001  dddd 1010 01M0 mmmm
def vneg(dest,Sd,Sm):
    v3arg(dest,0xeeb1,0x0a40,Sd,Sm)
# vnmla, vnmls, vnmul:
#   nmla does Sd = -Sd+-(Sn*Sm)
#   nmls does Sd = -Sd+(Sn*Sm)
#   nmul does Sd = -(Sn*Sm)
#  1110 1110 0D01 nnnn  dddd 1010 NoM0 mmmm
#    o = 0 is nmls, else nmla
def vnmla(dest,Sd,Sm,Sn):
    v3arg(dest,0xee10,0x0a40,Sd,Sm,Sn)
def vnmls(dest,Sd,Sm,Sn):
    v3arg(dest,0xee10,0x0a00,Sd,Sm,Sn)
#  1110 1110 0D10 nnnn  dddd 1010 N1M0 mmmm
#    nmul
def vnmul(dest,Sd,Sm,Sn):
    v3arg(dest,0xee20,0x0a40,Sd,Sm,Sn)
# vpop:
#   pops a reg list from the stack
#  1110 1100 1D11 1101  dddd 1010 [imm8   ]
#     consecutive Ses (no wrap)
def vpop(dest,Sd,imm8):
    v3arg(dest,0xecbd,0x0a00|imm8,Sd)
# vpush:
#  1110 1101 0D10 1101  dddd 1010 [imm8   ]
def vpush(dest,Sd,imm8):
    v3arg(dest,0xed2d,0x0a00|imm8,Sd)
# vsqrt: pyb has this
#  1110 1110 1D11 0001  dddd 1010 11M0 mmmm
def vsqrt(dest,Sd,Sm):
    v3arg(dest,0xeeb1,0x0ac0,Sd,Sm)
# vstm:
#  store multiple
#  1110 110P UDW0 nnnn  dddd 1010 [imm8   ]
#    like vldr
def vstm(dest,Sd,Rn,num):
    v3arg(dest,0xec80,0x0a00|num,Sd,0,Rn<<1)
# vstr: pyb has this
def vstr(dest,Sd,Rn,offs=0):
    v3arg(dest,0xed00|((offs>=0)<<7),0x0a00|(offs&0xff),Sd,0,Rn<<1)
# vsub: pyb has this
def vsub(dest,Sd,Sn,Sm):
    v3arg(dest,0xee30,0x0a40,Sd,Sm,Sn)

