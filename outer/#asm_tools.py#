#
from array import array


#notes:
#with the fpv4:
#  no VSEL, VMAXNM, VMINNM, VCVTA, VCVTN, VCVTP, VCVTM, VRINTA, VRINTN, VRINTP, VRINTM, VRINTZ, VRINTR
#  no double precision opcodes


# supported by pyb asm:
#  vadd,vsub,vneg,vmul,vdiv,vsqrt, vmov between r and s,vmrs, vldr, vstr, vcmp, vcvt between float and 32 bit int
# fp instructions not supported:
# (it looks like half precision is just rounded to or converted from (using vcvtb), it's not used as an internal representation)
# vabs,vcmp with 0,vcmpe,vcvt,vcvtr,vcvtb,vcvtt,vdiv,vfma,vfms,vfnma,vfnms,vmla,vmls,vmov,vmul,vneg,vnmla,vnmls,vnmul,vsqrt,vsub
def v3arg(p0=0,p1=0,Sd=0,Sm=0,Sn=0):
    return "data(2,"+hex(p0|((Sd&1)<<6)|(Sn>>1))+","+hex(p1|((Sd&0x1e)<<11)|((Sm&1)<<5)|(Sm>>1)|((Sn&1)<<7))+")"
# vabs:                      sz-. is 0 because no double
#  1110 1110 1D11 0000  dddd 1010 11M0 mmmm
#    sddddD = |smmmmM|
def vabs(Sd,Sm):
    return v3arg(0xeeb0,0x0ac0,Sd,Sm)
# vadd:
#  1110 1110 0D11 nnnn  dddd 1010 N0M0 mmmm (pyb has this)
#    sd = sn+sm
# vcmp:
#  1110 1110 1D11 0100  dddd 1010 E1M0 mmmm (pyb has this version)
#  1110 1110 1D11 0101  dddd 1010 E1O0 OOOO where O is (0)
#   cmp with 0
#    E is whether any nan should throw or just loud ones (1 for any)
def vcmp0(Sd):#E=0
    return v3arg(0xeeba,0x0a40,Sd)
# vcvt:
#  1111 1110 1D11 1op2  dddd 1010 o1M0 mmmm
#   op2 = 101 is vcvt_s32_f32(Sd,Sm) (pyb has this)
#    o is whether to use rounding towards 0 (1) or the FPSCR specified mode (0)
#   op2 = 100 is vcvt_u32_f32(Sd,Sm)
#    o is same as above
def vcvt_u32_f32(Sd,Sm):#use specified round
    return v3arg(0xfebc,0x0a40,Sd,Sm)
#   op2 = 000 is vcvt_f32_(Tm)(Sd,Sm)     ddddD, mmmmM
#                           ^- [u32,s32][o]
def vcvt_f32_u32(Sd,Sm):
    return v3arg(0xfeb8,0x0a40,Sd,Sm)
#  1110 1110 1D11 1o1U  dddd 1010 x1i0 imm4
#   conv between floating and fixed point
#    unsigned = U, reg is ddddD (converts in place)
#    size = [16,32][x]
#    frac_bits = size-(imm4:i)
#      unpredictable if frac_bits < 0
#    o is direction of conversion (1 for to fixed)
def vcvt_f32_fixed32(Sd,fix=0,unsigned=0):
    return v3arg(0xeeba|unsigned,0x0ac0,Sd,fix)
def vcvt_fixed32_f32(Sd,fix=0,unsigned=0):
    return v3arg(0xeebe|unsigned,0x0ac0,Sd,fix)
def vcvt_f32_fixed16(Sd,fix=0,unsigned=0):
    return v3arg(0xeeba|unsigned,0x0a40,Sd,fix)
def vcvt_fixed16_f32(Sd,fix=0,unsigned=0):
    return v3arg(0xeebe|unsigned,0x0a40,Sd,fix)
#    
# vcvtb and vcvtt: (convert bottom and top between half and single prec)
#  1110 1110 1D11 001o  dddd 1010 T1M0 mmmm
#   half to single is o = 0, single to half is o = 1
#   T is 1 for vcvtt and 0 for vcvtb
#   sddddD, smmmmM
def vcvtb(Sd,Sm,toHalf=1):
    return v3arg(0xeeb2|toHalf,0x0a40,Sd,Sm)
def vcvtt(Sd,Sm,toHalf=1):
    return v3arg(0xeeb2|toHalf,0x0ac0,Sd,Sm)
# vdiv: pyb has this
# vfma vfms:
#  1110 1110 1D10 nnnn  dddd 1010 NoM0 mmmm
#    sddddD ±= snnnnN*smmmmM
#           o = 1 for sub
def vfma(Sd,Sm,Sn):
    return v3arg(0xeea0,0x0a00,Sd,Sm,Sn)
def vfms(Sd,Sm,Sn):
    return v3arg(0xeea0,0x0a40,Sd,Sm,Sn)
# vfnma vfnms:
#  1110 1110 1D01 nnnn  dddd 1010 NoM0 mmmm
#    sddddD = -sddddD + ((-snnnnN)*smmmmM)   : o = 1
#    sddddD = -sddddD + ((snnnnN)*smmmmM)    : o = 0
#    basically fm(a/s) followed by vneg(Sd,Sd)
def vfnma(Sd,Sm,Sn):
    return v3arg(0xee90,0x0a00,Sd,Sm,Sn)
def vfnms(Sd,Sm,Sn):
    return v3arg(0xee90,0x0a40,Sd,Sm,Sn)
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
def vldm(Sd,Rn,num):
    return v3arg(0xec90,0x0a00|num,Sd,0,Rn<<1)
# vldr: pyb has this
# vmla/s:
#  1110 1110 0D00 nnnn  dddd 1010 NoM0 mmmm
#   o=0 is a, o=1 is s
#   same as fma, fms, but it rounds the multiply
def vmla(Sd,Sm,Sn):
    return v3arg(0xee00,0x0a00,Sd,Sm,Sn)
def vmls(Sd,Sm,Sn):
    return v3arg(0xee00,0x0a40,Sd,Sm,Sn)
# vmov imm:
#  1110 1110 1D11 aaaa  dddd 1010 O0O0 bbbb (O is (0))
#   imm8 = aaaabbbb -> abcdefgh
#   SddddD = aBbbbbbcd efgh0000000000000000000
#     i.e. you can specify sign, exp between 01111100 and 10000011, and 4 msbits of the mantissa
#     so: ± 1/8 to ±31 (last ones in steps of 1)
#     kinda like reading imm8 as a seeemmmm tinyfloat with no inf/nan or denormal
def vmov_imm(Sd,imm8):
    return v3arg(0xeeb0|(imm8>>4),0x0a00|(imm8&0xf),Sd)
# vmov reg:
#  1110 1110 1D11 0000  dddd 1010 01M0 mmmm
#   SddddD = SmmmmM
def vmov_reg(Sd,Sm):
    return v3arg(0xeeb0,0x0a40,Sd,Sm)
# vmov R to S and S to R: pyb has this
# vmov 2 at once:
#  1110 1100 010o bbbb  aaaa 1010 00M1 mmmm
#   to R is o=1, from is o=0
#   m = 31 is unpredictable (as are 13 or 15 as a or b), the S regs have to be consequative
#   SmmmmM = Ra; S(mmmmM+1) = Rb   for o = 0
def vmov2_r_to_s(Ra,Sm,Rb):
    return v3arg(0xec40,0x0a10,Ra<<1,Sm,Rb<<1)
def vmov2_s_to_r(Ra,Sm,Rb):
    return v3arg(0xec50,0x0a10,Ra<<1,Sm,Rb<<1)
# The flags move one can also move flags to an R reg: pyb has this.
# and the other way
# vmul: pyb has this
# vneg: pyb has this
# vnmla, vnmls, vnmul:
#   nmla does Sd = -Sd+-(Sn*Sm)
#   nmls does Sd = -Sd+(Sn*Sm)
#   nmul does Sd = -(Sn*Sm)
#  1110 1110 0D01 nnnn  dddd 1010 NoM0 mmmm
#    o = 0 is nmls, else nmla
#  1110 1110 0D10 nnnn  dddd 1010 N1M0 mmmm
#    nmul
# vpop:
#   pops a reg list from the stack
#  1110 1100 1D11 1101  dddd 1010 [imm8   ]
#     consecutive Ses (no wrap)
# vpush:
#  1110 1101 0D10 1101  dddd 1010 [imm8   ]
# vsqrt: pyb has this
# vstm:
#  store multiple
#  1110 110P UDW0 nnnn  dddd 1010 [imm8   ]
#    like vldr
def vstm(Sd,Rn,num):
    return v3arg(0xec80,0x0a00|num,Sd,0,Rn<<1)
# vstr: pyb has this
# vsub: pyb has this



exec(""" 

@micropython.asm_thumb
def a_u8_to_float(r0,r1,r2):
    label(loop)
    ldrb(r3,[r0,0])
    add(r0,1)
    sub(r3,128)
    vmov(s0,r3)
    """+vcvt_f32_fixed16(0,9)+"""#vcvt f32<-9.7 (s0)
    vstr(s0,[r1,0])
    add(r1,4)
    sub(r2,1)
    bgt(loop)
""")


exec(""" 

@micropython.asm_thumb
def a_s16_to_float(r0,r1,r2,r3):
    add(r1,r1,r3)
    label(loop)
    ldrh(r3,[r0,0])
    add(r0,2)
    vmov(s0,r3)
    """+vcvt_f32_fixed16(0,1)+"""#vcvt f32<-1.15 (s0)
    vstr(s0,[r1,0])
    add(r1,4)
    sub(r2,1)
    bgt(loop)
""")  


exec(""" 

@micropython.asm_thumb
def a_half_to_float(r0,r1,r2):
    label(loop)
    ldrh(r3,[r0,0])
    add(r0,2)
    vmov(s0,r3)
    """+vcvtb(0,0,0)+"""#vcvtb f32<-f16 (s0,s0)
    vstr(s0,[r1,0])
    add(r1,4)
    sub(r2,1)
    bgt(loop)
""")  



rand_addr = const(0x50060808)

def vbiquadAsm(name="",inp=0,out=0,a1=4,a2=5,b0=6,b1=7,b2=8,s0=9,s1=10,t0=31,t1=30):
    if (inp == out):
        return """
    #biquad """+str(name)+""": a = [s"""+str(a1)+""",s"""+str(a2)+"""], b = [s"""+str(b0)+""",s"""+str(b1)+""",s"""+str(b2)+"""], state = [s"""+str(s0)+""",s"""+str(s1)+"""]
    # input/output = s"""+str(inp)+"""
    # uses temp regs s"""+str(t0)+""" and s"""+str(t1)+"""
    vmul(s"""+str(t0)+""",s"""+str(inp)+""",s"""+str(b1)+""") #t0 = inp*b1
    vmul(s"""+str(t1)+""",s"""+str(inp)+""",s"""+str(b2)+""") #t1 = inp*b2
    vmul(s"""+str(inp)+""",s"""+str(inp)+""",s"""+str(b0)+""") #inp *= b0
    vadd(s"""+str(inp)+""",s"""+str(inp)+""",s"""+str(s0)+""") #inp += state0 (and out = inp)
    """+str(vfms(t0,inp,a1))+""" #vfms(s"""+str(t0)+""",s"""+str(inp)+""",s"""+str(a1)+""") #t0 -= out*a1
    vadd(s"""+str(s0)+""",s"""+str(t0)+""",s"""+str(s1)+""") # state0 = t0+state1
    vmul(s"""+str(s1)+""",s"""+str(inp)+""",s"""+str(a2)+""") # state1 = out*a2 
    vsub(s"""+str(s1)+""",s"""+str(t1)+""",s"""+str(s1)+""") # state1 = t1-state1
    #end biquad^"""
    return """
    #biquad """+str(name)+""": a = [s"""+str(a1)+""",s"""+str(a2)+"""], b = [s"""+str(b0)+""",s"""+str(b1)+""",s"""+str(b2)+"""], state = [s"""+str(s0)+""",s"""+str(s1)+"""]
    # input = s"""+str(inp)+""", output = s"""+str(out)+"""
    vmul(s"""+str(out)+""",s"""+str(inp)+""",s"""+str(b0)+""") #out = inp*b0
    vadd(s"""+str(out)+""",s"""+str(out)+""",s"""+str(s0)+""") #out += state0
    vmul(s"""+str(s0)+""",s"""+str(inp)+""",s"""+str(b1)+""") #state0 = inp*b1
    """+str(vfms(s0,out,a1))+""" #vfms(s"""+str(s0)+""",s"""+str(out)+""",s"""+str(a1)+""") #state0 -= out*a1
    vadd(s"""+str(s0)+""",s"""+str(s0)+""",s"""+str(s1)+""") #state0 += state1
    vmul(s"""+str(s1)+""",s"""+str(inp)+""",s"""+str(b2)+""") #state1 = inp*b1
    """+str(vfms(s1,out,a2))+""" #vfms(s"""+str(s1)+""",s"""+str(out)+""",s"""+str(a2)+""") #state1 -= out*a2
    #end biquad^"""

    
    


exec(""" 

@micropython.asm_thumb
def a_biquads(r0,r1,r2,r3): #dest, src, args, len
    #does 4 biquads
    """+vldm(2,2,28)+""" #vldm(s2,r2,28)
    label(loop)
    vldr(s1,[r1,0])
    add(r1,4)
    """+vbiquadAsm('1',1,0, 2,3 ,4,5,6, 7,8)+\
    vbiquadAsm('2',0,1, 9,10 ,11,12,13, 14,15)+\
    vbiquadAsm('3',1,0, 16,17 ,18,19,20, 21,22)+\
    vbiquadAsm('4',0,1, 23,24 ,25,26,27, 28,29)+\
    """
    vstr(s1,[r0,0])
    add(r0,4)
    sub(r3,1)
    bne(loop)
    #write back
    """+vstm(2,2,28)+""" #vstm(s2,r2,28)

""")


exec(""" 

@micropython.asm_thumb
def as_parl_biquads(r0,r1,r2,r3): #dest, src, args, len
    #does 4 biquads, 2 on each channel
    """+vldm(2,2,28)+""" #vldm(s2,r2,28)
    label(loop)
    vldr(s1,[r1,0])
    vldr(s31,[r1,4])
    add(r1,8)
    """+vbiquadAsm('1l',1,0, 2,3 ,4,5,6, 7,8)+\
    vbiquadAsm('2l',0,1, 9,10 ,11,12,13, 14,15)+\
    vbiquadAsm('1r',31,30, 16,17 ,18,19,20, 21,22)+\
    vbiquadAsm('2r',30,31, 23,24 ,25,26,27, 28,29)+\
    """
    vstr(s1,[r0,0])
    vstr(s31,[r0,4])
    add(r0,8)
    sub(r3,2)
    bgt(loop)
    #write back
    """+vstm(2,2,28)+""" #vstm(s2,r2,28)

""")


exec(
""" 

@micropython.asm_thumb
def as_mat_biquad(r0,r1,r2,r3):  #dest, src, args, len
    #does a matrix biquad on a stereo signal
    # a1 = [2,3 4,5], a2 = [6,7 8,9],
    # b0 = [10,11 12,13], b1 = [14,15 16,17], b2 = [18,19 20,21]
    # s0 = [22,23], s1 = [24,25]
    #
    """+vldm(2,2,24)+"""
    label(loop)
    vldr(s0,[r1,0])
    vldr(s1,[r1,4])
    add(r1,8)

    # out <- b0 * in + s0
    # s2*s0+s3*s1, s4*s0+s5*s1
    vmul(s26,s0,s10)
    vmul(s27,s0,s12)
    """+vfma(26,1,11)+"""
    """+vfma(27,1,13)+"""
    vadd(s26,s26,s22)
    vadd(s27,s27,s23)
    #
    # s0 <- b1 * in + s1 - a1*out
    vmul(s22,s0,s14)
    vmul(s23,s0,s16)
    """+vfma(22,1,15)+"""
    """+vfma(23,1,17)+"""
    vadd(s22,s22,s24)
    vadd(s23,s23,s25)
    """+vfms(22,26,2)+"""
    """+vfms(23,26,4)+"""
    """+vfms(22,27,3)+"""
    """+vfms(23,27,5)+"""
    #
    # s1 <- b2*in - a2*out
    vmul(s24,s0,s18)
    vmul(s25,s0,s20)
    """+vfma(24,1,19)+"""
    """+vfma(25,1,21)+"""
    """+vfms(24,26,6)+"""
    """+vfms(25,26,8)+"""
    """+vfms(24,27,7)+"""
    """+vfms(25,27,9)+"""
    #
    
    vstr(s26,[r0,0])
    vstr(s27,[r0,4])
    add(r0,8)
    sub(r3,2)
    bgt(loop)
    """+vstm(2,2,24)+"""

""")

    


exec(""" 

@micropython.asm_thumb
def a_filtered_noise(r0,r1,r2): #dest, args [offset,gain,*filts], len
    #does 4 biquads
    movwt(r3,"""+hex(rand_addr)+""") #rng address  
    """+vldm(1,1,30)+""" #vldm(s1,r1,30)

    label(loop)
    vldr(s31,[r3,0])
    vcvt_f32_s32(s31,s31)
    vmul(s31,s31,s2)
    """+\
    vbiquadAsm('1',31,0, 3,4 ,5,6,7, 8,9)+\
    vbiquadAsm('2',0,31, 10,11 ,12,13,14, 15,16)+\
    vbiquadAsm('3',31,0, 17,18 ,19,20,21, 22,23)+\
    vbiquadAsm('4',0,31, 24,25 ,26,27,28, 29,30)+\
    """
    vadd(s31,s31,s1)
    vstr(s31,[r0,0])
    add(r0,4)
    sub(r2,1)
    bne(loop)
    #write back
    """+vstm(1,1,30)+""" #vstm(s1,r1,30)
""")




def vfeynmanOscAsm(name,sine,cosine,delta,dest=None,destc=None):
    return """
    #feynmanOsc """+str(name)+" #sin,cos,dt = s"+str(sine)+",s"+str(cosine)+",s"+str(delta)+"""
    """+vfma(sine,cosine,delta)+"""# vfma(sine,cosine,dt)
    """+vfms(cosine,sine,delta)+"""# vfms(cosine,sine,dt)
    """+ ("vadd(s"+str(dest)+",s"+str(dest)+",s"+str(sine)+")\n    " if dest != None else "") +"""
    """+ ("vadd(s"+str(destc)+",s"+str(destc)+",s"+str(cosine)+")\n    " if destc != None else "") +\
        "#end osc^"


exec(""" 

@micropython.asm_thumb
def a_osc_synth(r0,r1,r2,r3):
    """+vldm(1,2,30)+""" #vldm(s1,r2,30)
    label(loop)
    vldr(s0,[r0,0])
    add(r0,4)
    """+("".join((vfeynmanOscAsm(i+1,i*3+1,i*3+2,i*3+3,0) for i in range(10))))+"""
    vstr(s0,[r1,0])
    add(r1,4)
    sub(r3,1)
    bgt(loop)
    """+vstm(1,2,30)+""" #vstm(s1,r2,30)
""")


exec(""" 

@micropython.asm_thumb
def as_osc_synth(r0,r1,r2,r3):
    """+vldm(2,2,30)+""" #vldm(s2,r2,30)
    label(loop)
    vldr(s0,[r0,0])
    vldr(s1,[r0,4])
    add(r0,8)
    """+("".join((vfeynmanOscAsm(i+2,i*3+2,i*3+3,i*3+4,0,1) for i in range(10))))+"""
    vstr(s0,[r1,0])
    vstr(s1,[r1,4])
    add(r1,8)
    sub(r3,2)
    bgt(loop)
    """+vstm(2,2,30)+""" #vstm(s2,r2,30)
""")
    

@micropython.asm_thumb
def a_chopped_inv_erf(r0):
    vmov(s0,r0)
    # sign(x) * (abs(x) in (x^2-1) / (x+√((1.033/3)x+√(x+.51√(x+.099√(x))))))

@micropython.asm_thumb
def a_sah_resample(r0,r1,r2,r3): #dest,src,args,len(dest) returns number of source bytes consumed
    #args = array('I',[numerator,denominator,phase,sample (actually a float)])
    # len of input is (d/n)*len(output)
    # so every n input symbols go to d output symbols
    
    ldr(r4,[r2,0])
    ldr(r5,[r2,4])
    ldr(r6,[r2,8])
    vldr(s0,[r2,12])
    mov(r7,r1) #save src ptr to do math with later
    label(destloop) #TODO: use division to avoid loop
    #each iter writes one sample from source to dest
    sub(r6,r6,r4) #sub num from phase
    bge(srcloop_end) #skip loop if phase >= 0
    label(srcloop)
    #grab a new source sample
    add(r1,4)
    add(r6,r6,r5) #add denom to phase
    blt(srcloop) #loop if phase < 0
    
    vldr(s0,[r1,0]) #grab sample here

    label(srcloop_end)

    vstr(s0,[r0,0])
    add(r0,4)

    sub(r3,1)
    bne(destloop)
    label(destloop_end)
    #amount of source bytes consumed
    sub(r0,r1,r7)
    #write back phase,sample
    str(r6,[r2,8])
    vstr(s0,[r2,12])

@micropython.asm_thumb
def as_sah_resample(r0,r1,r2,r3): #dest,src,args,len(dest) returns number of source bytes consumed
    #args = array('I',[numerator,denominator,phase,sampleL (actually a float),sampleR])
    # len of input is (d/n)*len(output)
    # so every n input symbols go to d output symbols
    
    ldr(r4,[r2,0])
    ldr(r5,[r2,4])
    ldr(r6,[r2,8])
    vldr(s0,[r2,12])
    vldr(s1,[r2,16])
    mov(r7,r1) #save src ptr to do math with later
    label(destloop) #TODO: use division to avoid loop
    #each iter writes one sample from source to dest
    sub(r6,r6,r4) #sub num from phase
    bge(srcloop_end) #skip loop if phase >= 0
    label(srcloop)
    #grab a new source sample
    add(r1,8)
    add(r6,r6,r5) #add denom to phase
    blt(srcloop) #loop if phase < 0
    
    vldr(s0,[r1,0]) #grab sample here
    vldr(s1,[r1,4]) #grab sample here

    label(srcloop_end)

    vstr(s0,[r0,0])
    vstr(s1,[r0,4])
    add(r0,8)

    sub(r3,2)
    bgt(destloop)
    label(destloop_end)
    #amount of source bytes consumed
    sub(r0,r1,r7)
    #write back phase,sample
    str(r6,[r2,8])
    vstr(s0,[r2,12])
    vstr(s1,[r2,16])








#"Arm v7-M Architecture Reference Manual"
# 1110 1001 0010 1101  0m0r egis list
#data(2, 0xe92d, 0x0f00) # push r8,r9,r10,r11 #for instructions that arent yet exposed

#int args: [h_offset*2, f_offset*2, n]
#float args: [min_clip,max_clip,dc_offset,      ( 3)
#             a1,a2,b0,b1,b2,s1,s2, - biquad 1  (10)
#             a1,a2,b0,b1,b2,s1,s2, - biquad 2  (17)
#             a1,a2,b0,b1,b2,s1,s2, - dither biquad 1  (24)
#             noise shape,noise state]    (26)



exec(""" 

@micropython.asm_thumb
def a_conv(r0,r1,r2,r3):
    movwt(r6,"""+hex(rand_addr)+""") #rng address

    #load in args
    """+vldm(1,3,26)+""" #vldm(s1,r3,26)
    
    #loop converting
    label(Loop)
    vldr(s0,[r1,0])
    add(r1,4)

    #filter section
    """+vbiquadAsm("1",0,31,4,5,6,7,8,9,10)+"""
    
    """+vbiquadAsm("2",31,0,11,12,13,14,15,16,17)+"""
    
    #dither
    vldr(s31,[r6,0])
    vcvt_f32_s32(s31,s31)
    """+vbiquadAsm("dither 1",31,30,18,19,20,21,22,23,24)+"""
    
    vadd(s0,s0,s30) #add dither
    """+vfma(0,25,26)+""" #vfma(s0,s25,s26) #add error 
    
    vadd(s0,s0,s3) #add offset

    #bound
    vcmp(s0,s1)
    vmrs(APSR_nzcv, FPSCR)
    itee(lt)
    """+vmov_reg(0,1)+""" #vmov(s0,s1)

    vcmp(s0,s2)
    vmrs(APSR_nzcv, FPSCR)
    it(gt)
    """+vmov_reg(0,2)+""" #vmov(s0,s2)
    
    #quantization section
    vcvt_s32_f32(s31, s0)
    vmov(r7,s31)

    #error prop
    vcvt_f32_s32(s31, s31)
    vsub(s26,s0,s31)
    
    strh(r7,[r0,0])
    add(r0,2)
    sub(r2,1)
    bne(Loop)

    #write back to the float arr the states of the biquads
    vstr(s9,[r3,32])
    vstr(s10,[r3,36])
    vstr(s16,[r3,60])
    vstr(s17,[r3,64])
    vstr(s23,[r3,88])
    vstr(s24,[r3,92])
    vstr(s26,[r3,100]) #error
""")


def s_conv(l,r,f,fs,a1,a2):
    a_conv_s2(l,f,len(f)//2,a1)
    a_conv_s2(r,fs,len(f)//2,a2)


exec(""" 

@micropython.asm_thumb
def a_conv_s2(r0,r1,r2,r3): #same as a_conv but with stride 2
    movwt(r6,"""+hex(rand_addr)+""") #rng address

    #load in args
    """+vldm(1,3,26)+""" #vldm(s1,r3,26)
    
    #loop converting
    label(Loop)
    vldr(s0,[r1,0])
    add(r1,8) #stride here

    #filter section
    """+vbiquadAsm("1",0,31,4,5,6,7,8,9,10)+"""
    
    """+vbiquadAsm("2",31,0,11,12,13,14,15,16,17)+"""
    
    #dither
    vldr(s31,[r6,0])
    vcvt_f32_s32(s31,s31)
    """+vbiquadAsm("dither 1",31,30,18,19,20,21,22,23,24)+"""
    
    vadd(s0,s0,s30) #add dither
    """+vfma(0,25,26)+""" #vfma(s0,s25,s26) #add error 
    
    vadd(s0,s0,s3) #add offset

    #bound
    vcmp(s0,s1)
    vmrs(APSR_nzcv, FPSCR)
    itee(lt)
    """+vmov_reg(0,1)+""" #vmov(s0,s1)

    vcmp(s0,s2)
    vmrs(APSR_nzcv, FPSCR)
    it(gt)
    """+vmov_reg(0,2)+""" #vmov(s0,s2)
    
    #quantization section
    vcvt_s32_f32(s31, s0)
    vmov(r7,s31)

    #error prop
    vcvt_f32_s32(s31, s31)
    vsub(s26,s0,s31)
    
    strh(r7,[r0,0])
    add(r0,2)
    sub(r2,1)
    bne(Loop)

    #write back to the float arr the states of the biquads
    vstr(s9,[r3,32])
    vstr(s10,[r3,36])
    vstr(s16,[r3,60])
    vstr(s17,[r3,64])
    vstr(s23,[r3,88])
    vstr(s24,[r3,92])
    vstr(s26,[r3,100]) #error
""")

