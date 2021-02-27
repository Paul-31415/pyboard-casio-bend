#



#syntax examples:

def mini_to_int(mini):
    exp = mini[6...4]
    mant = mini[3...0]
    if exp:
        mant |= 0x10 <<= exp
    else:
        mant <<= 1
    if mini[7]:
        -= mant
    ulp = 1<<exp
    return mant,ulp
def float_to_mini(f):
    res = `best((f>>24)&0x80,f[31]<<8) #mov imm8, and with shifted reg: 3 words total vs f[31]<<8 which is 2 for bitfield and 2 for imm shift (should make this a peephole optimization?)
    mant = f[22...0]
    exp = f[30...23] - 0x7f + 3
    if <=:
        mant |= (1<<23) >>= 1-exp
        exp = 0
    elif exp > 7:
        exp = 7 #should be culled by dataflow-pruning
        res |= 0x7f
    else:
        res |= mant>>19
    return res,1
    
#stuff:
# ( ) groups operations
# { } groups operations and forms an algebraic atom (the enclosed intermediate result is calculated)


    















































# https://developer.arm.com/documentation/ddi0403/ed/
#for the stm32f405

#summary of some key points:
# thumb2 is a stream of 16-bit halfwords,
# start with 0b111[01,10,11] are double instructions (32 bit)
#
# using 0xf as a reg specifier (pc) may do special behaviour
#  (sometimes it's for pc-relative operations)
#  (use: immediate add and sub in some cases)
#  (sometimes it reads as 0)
#  (sometimes writing to it is a jump, sometimes a discard)
# 0xd (sp) funky and bad
# pc points to current instruction + 4

# 16 bit instrucctions:
# opcode??????????

#opcode =
# fedcba9876543210
# 00          - shift,add,sub,mov,comp
#   00000000    - mov
#   000         - lsl imm
#   001         - lsr imm
#   010         - asr imm
#   01100       - add
#   01101       - sub
#   01110       - add imm3
#   01111       - sub imm3
#   100         - mov
#   101         - cmp
#   110         - add imm8
#   111         - sub imm8
# 010000      - dataprocessing (boolean ops and stuff)
#       0000    - and
#       0001    - eor (xor)
#       0010    - lsl
#       0011    - lsr
#       0100    - asr
#       0101    - adc
#       0110    - sbc
#       0111    - ror (rr)
#       1000    - tst (and but only effects flags)
#       1001    - rsb (reverse sub from 0)
#       1010    - cmp
#       1011    - cmn (compare negative)
#       1100    - orr (or)
#       1101    - mul
#       1110    - bic (clear bits)
#       1111    - mvn (not)
# 010001      - special data/branch/exchg
#       00      - add 
#       0100    - UNPREDICTABLE
#       0101    - cmp
#       011     - cmp
#       10      - mov
#       110     - bx (call)
#       111     - blx (call but different)
# 01001       - load from literal (from the literal pool)
#      
# 0101        - load/store datum
#     nnn       - str, strh, strb, ldrsb, ldr, ldrh, ldrb, ldrsh
#   10n         - str imm, ldr imm
#   11n         - strb imm, ldrb imm
# 1000n         - strh imm, ldrh imm
#    1n         - str imm, ldr imm   but sp relative
# 10100       - make pc-relative addr
# 10101       - make sp-relative addr
# 1011        - misc
# 11000       - store multiple
# 11001       - load multiple
# 1101        - conditional branch
# 11100       - unconditional branch
# above:32 bit






































#misc:

#unsigned bit field extract (p424)
# 1111 0011 1100 nnnn  0im3 dddd i20w wwww
# p = imm3:imm2
# w = wwwww+1
#Rd = (Rn>>p)&((1<<w)-1)
def ubfx(dest,rd,rn,p,w):
    assert 0 <= p < 32
    assert 0 < w <= 32-p
    dest.write(0xf3c0|rn)
    imm3 = p>>2
    imm2 = p&3
    dest.write((imm3<<12)|(rd<<8)|(imm2<<6)|(w-1))
#signed version:
# 1111 0011 0100 nnnn  0im3 dddd i20w wwww
def sbfx(dest,rd,rn,p,w):
    assert 0 <= p < 32
    assert 0 < w <= 32-p
    dest.write(0xf340|rn)
    imm3 = p>>2
    imm2 = p&3
    dest.write((imm3<<12)|(rd<<8)|(imm2<<6)|(w-1))
    


    
