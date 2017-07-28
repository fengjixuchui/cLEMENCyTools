import collections

# --------------- ISA Definitions -----------------

CONDSUFFIX = {
	0b0000: 'n',
	0b0001: 'e',
	0b0010: 'l',
	0b0011: 'le',
	0b0100: 'g',
	0b0101: 'ge',
	0b0110: 'no',
	0b0111: 'o',
	0b1000: 'ns',
	0b1001: 's',
	0b1010: 'sl',
	0b1011: 'sle',
	0b1100: 'sg',
	0b1101: 'sge',
	0b1111: '', # Always
}

ISAOperand = collections.namedtuple('ISAOperand', ['name', 'start', 'width'])
# ISAInstruction = collections.namedtuple('ISAInstruction', ['size_in_bytes', 'name', 'operands', 'opcode_bits', 'opcode', 'subopcode', 'subopcode_start', 'subopcode_bits', 'update_flag'])
class ISAInstruction(object):
	pass

def ParseISADefinitionLine(ln):
    segs = ln.split(' ')
    instrlen = segs[-1]
    assert instrlen.endswith('b')

    result = ISAInstruction()
    result.name = segs[0].lower()
    result.size_in_bytes = int(instrlen[:-1])
    result.opcode = int(segs[1].split('=')[1], 16)
    result.opcode_bits = int(segs[1].split('=')[0].split('-')[1]) + 1
    result.subopcode = None
    result.update_flag = None
    result.operands = []
    for seg in segs[2:-1]:
    	br, name = seg.split('=')
    	if '-' not in br: br = br + '-' + br
    	start, end = map(int, br.split('-'))
    	width = end-start + 1
    	if name.startswith('0x'):
    		assert result.subopcode is None, ln
    		result.subopcode = int(name, 16)
    		result.subopcode_start = start
    		result.subopcode_bits = width
    	elif name == 'UF':
    		assert result.update_flag == None
    		result.update_flag = start
    		assert width == 1
    	else:
    		result.operands.append(ISAOperand(name, start, width))
    return result

#with open('isa.txt') as fp:
#    ISA_DEF = map(ParseISADefinitionLine, fp.read().strip().split('\n'))

ISA_DEF_STR = '''AD 0-6=0x0 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
ADC 0-6=0x20 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
ADCI 0-6=0x20 7-11=rA 12-16=rB 17-23=imm 24-25=0x1 26=UF 3b
ADCIM 0-6=0x22 7-11=rA 12-16=rB 17-23=imm 24-25=0x1 26=UF 3b
ADCM 0-6=0x22 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
ADF 0-6=0x1 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
ADFM 0-6=0x3 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
ADI 0-6=0x0 7-11=rA 12-16=rB 17-23=imm 24-25=0x1 26=UF 3b
ADIM 0-6=0x2 7-11=rA 12-16=rB 17-23=imm 24-25=0x1 26=UF 3b
ADM 0-6=0x2 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
AN 0-6=0x14 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
ANI 0-6=0x14 7-11=rA 12-16=rB 17-23=imm 24-25=0x1 26=UF 3b
ANM 0-6=0x16 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
B 0-5=0x30 6-9=Condition 10-26=Offset 3b
BF 0-8=0x14c 9-13=rA 14-18=rB 19-25=0x40 26=UF 3b
BFM 0-8=0x14e 9-13=rA 14-18=rB 19-25=0x40 26=UF 3b
BR 0-5=0x32 6-9=Condition 10-14=rA 15-17=0x0 2b
BRA 0-8=0x1c4 9-35=Location 4b
BRR 0-8=0x1c0 9-35=Offset 4b
C 0-5=0x35 6-9=Condition 10-26=Offset 3b
CAA 0-8=0x1cc 9-35=Location 4b
CAR 0-8=0x1c8 9-35=Offset 4b
CM 0-7=0xb8 8-12=rA 13-17=rB 2b
CMF 0-7=0xba 8-12=rA 13-17=rB 2b
CMFM 0-7=0xbe 8-12=rA 13-17=rB 2b
CMI 0-7=0xb9 8-12=rA 13-26=imm 3b
CMIM 0-7=0xbd 8-12=rA 13-26=imm 3b
CMM 0-7=0xbc 8-12=rA 13-17=rB 2b
CR 0-5=0x37 6-9=Condition 10-14=rA 15-17=0x0 2b
DBRK 0-17=0x3ffff 2b
DI 0-11=0xa05 12-16=rA 17=0x0 2b
DMT 0-6=0x34 7-11=rA 12-16=rB 17-21=rC 22-26=0x0 3b
DV 0-6=0xc 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
DVF 0-6=0xd 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
DVFM 0-6=0xf 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
DVI 0-6=0xc 7-11=rA 12-16=rB 17-23=imm 24-25=0x1 26=UF 3b
DVIM 0-6=0xe 7-11=rA 12-16=rB 17-23=imm 24-25=0x1 26=UF 3b
DVIS 0-6=0xc 7-11=rA 12-16=rB 17-23=immS 24-25=0x3 26=UF 3b
DVISM 0-6=0xe 7-11=rA 12-16=rB 17-23=immS 24-25=0x3 26=UF 3b
DVM 0-6=0xe 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
DVS 0-6=0xc 7-11=rA 12-16=rB 17-21=rC 22-25=0x2 26=UF 3b
DVSM 0-6=0xe 7-11=rA 12-16=rB 17-21=rC 22-25=0x2 26=UF 3b
EI 0-11=0xa04 12-16=rA 17=0x0 2b
FTI 0-8=0x145 9-13=rA 14-18=rB 19-26=0x0 3b
FTIM 0-8=0x147 9-13=rA 14-18=rB 19-26=0x0 3b
HT 0-17=0x280c0 2b
IR 0-17=0x28040 2b
ITF 0-8=0x144 9-13=rA 14-18=rB 19-26=0x0 3b
ITFM 0-8=0x146 9-13=rA 14-18=rB 19-26=0x0 3b
LDS 0-6=0x54 7-11=rA 12-16=rB 17-21=Reg_Count 22-23=Adj_rB 24-50=mem_off 51-53=0x0 6b
LDT 0-6=0x56 7-11=rA 12-16=rB 17-21=Reg_Count 22-23=Adj_rB 24-50=mem_off 51-53=0x0 6b
LDW 0-6=0x55 7-11=rA 12-16=rB 17-21=Reg_Count 22-23=Adj_rB 24-50=mem_off 51-53=0x0 6b
MD 0-6=0x10 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
MDF 0-6=0x11 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
MDFM 0-6=0x13 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
MDI 0-6=0x10 7-11=rA 12-16=rB 17-23=imm 24-25=0x1 26=UF 3b
MDIM 0-6=0x12 7-11=rA 12-16=rB 17-23=imm 24-25=0x1 26=UF 3b
MDIS 0-6=0x10 7-11=rA 12-16=rB 17-23=immS 24-25=0x3 26=UF 3b
MDISM 0-6=0x12 7-11=rA 12-16=rB 17-23=immS 24-25=0x3 26=UF 3b
MDM 0-6=0x12 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
MDS 0-6=0x10 7-11=rA 12-16=rB 17-21=rC 22-25=0x2 26=UF 3b
MDSM 0-6=0x12 7-11=rA 12-16=rB 17-21=rC 22-25=0x2 26=UF 3b
MH 0-4=0x11 5-9=rA 10-26=imm 3b
ML 0-4=0x12 5-9=rA 10-26=imm 3b
MS 0-4=0x13 5-9=rA 10-26=immS 3b
MU 0-6=0x8 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
MUF 0-6=0x9 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
MUFM 0-6=0xb 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
MUI 0-6=0x8 7-11=rA 12-16=rB 17-23=imm 24-25=0x1 26=UF 3b
MUIM 0-6=0xa 7-11=rA 12-16=rB 17-23=imm 24-25=0x1 26=UF 3b
MUIS 0-6=0x8 7-11=rA 12-16=rB 17-23=immS 24-25=0x3 26=UF 3b
MUISM 0-6=0xa 7-11=rA 12-16=rB 17-23=immS 24-25=0x3 26=UF 3b
MUM 0-6=0xa 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
MUS 0-6=0x8 7-11=rA 12-16=rB 17-21=rC 22-25=0x2 26=UF 3b
MUSM 0-6=0xa 7-11=rA 12-16=rB 17-21=rC 22-25=0x2 26=UF 3b
NG 0-8=0x14c 9-13=rA 14-18=rB 19-25=0x0 26=UF 3b
NGF 0-8=0x14d 9-13=rA 14-18=rB 19-25=0x0 26=UF 3b
NGFM 0-8=0x14f 9-13=rA 14-18=rB 19-25=0x0 26=UF 3b
NGM 0-8=0x14e 9-13=rA 14-18=rB 19-25=0x0 26=UF 3b
NT 0-8=0x14c 9-13=rA 14-18=rB 19-25=0x20 26=UF 3b
NTM 0-8=0x14e 9-13=rA 14-18=rB 19-25=0x20 26=UF 3b
OR 0-6=0x18 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
ORI 0-6=0x18 7-11=rA 12-16=rB 17-23=imm 24-25=0x1 26=UF 3b
ORM 0-6=0x1a 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
RE 0-17=0x28000 2b
RF 0-11=0xa0c 12-16=rA 17=0x0 2b
RL 0-6=0x30 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
RLI 0-6=0x40 7-11=rA 12-16=rB 17-23=imm 24-25=0x0 26=UF 3b
RLIM 0-6=0x42 7-11=rA 12-16=rB 17-23=imm 24-25=0x0 26=UF 3b
RLM 0-6=0x32 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
RMP 0-6=0x52 7-11=rA 12-16=rB 17-26=0x0 3b
RND 0-8=0x14c 9-13=rA 14-25=0x60 26=UF 3b
RNDM 0-8=0x14e 9-13=rA 14-25=0x60 26=UF 3b
RR 0-6=0x31 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
RRI 0-6=0x41 7-11=rA 12-16=rB 17-23=imm 24-25=0x0 26=UF 3b
RRIM 0-6=0x43 7-11=rA 12-16=rB 17-23=imm 24-25=0x0 26=UF 3b
RRM 0-6=0x33 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
SA 0-6=0x2d 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
SAI 0-6=0x3d 7-11=rA 12-16=rB 17-23=imm 24-25=0x0 26=UF 3b
SAIM 0-6=0x3f 7-11=rA 12-16=rB 17-23=imm 24-25=0x0 26=UF 3b
SAM 0-6=0x2f 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
SB 0-6=0x4 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
SBC 0-6=0x24 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
SBCI 0-6=0x24 7-11=rA 12-16=rB 17-23=imm 24-25=0x1 26=UF 3b
SBCIM 0-6=0x26 7-11=rA 12-16=rB 17-23=imm 24-25=0x1 26=UF 3b
SBCM 0-6=0x26 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
SBF 0-6=0x5 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
SBFM 0-6=0x7 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
SBI 0-6=0x4 7-11=rA 12-16=rB 17-23=imm 24-25=0x1 26=UF 3b
SBIM 0-6=0x6 7-11=rA 12-16=rB 17-23=imm 24-25=0x1 26=UF 3b
SBM 0-6=0x6 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
SES 0-11=0xa07 12-16=rA 17-21=rB 22-26=0x0 3b
SEW 0-11=0xa08 12-16=rA 17-21=rB 22-26=0x0 3b
SF 0-11=0xa0b 12-16=rA 17=0x0 2b
SL 0-6=0x28 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
SLI 0-6=0x38 7-11=rA 12-16=rB 17-23=imm 24-25=0x0 26=UF 3b
SLIM 0-6=0x3a 7-11=rA 12-16=rB 17-23=imm 24-25=0x0 26=UF 3b
SLM 0-6=0x2a 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
SMP 0-6=0x52 7-11=rA 12-16=rB 17=0x1 18-19=Memory_Flags 3b
SR 0-6=0x29 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
SRI 0-6=0x39 7-11=rA 12-16=rB 17-23=imm 24-25=0x0 26=UF 3b
SRIM 0-6=0x3b 7-11=rA 12-16=rB 17-23=imm 24-25=0x0 26=UF 3b
SRM 0-6=0x2b 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
STS 0-6=0x58 7-11=rA 12-16=rB 17-21=Reg_Count 22-23=Adj_rB 24-50=mem_off 51-53=0x0 6b
STT 0-6=0x5a 7-11=rA 12-16=rB 17-21=Reg_Count 22-23=Adj_rB 24-50=mem_off 51-53=0x0 6b
STW 0-6=0x59 7-11=rA 12-16=rB 17-21=Reg_Count 22-23=Adj_rB 24-50=mem_off 51-53=0x0 6b
WT 0-17=0x28080 2b
XR 0-6=0x1c 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
XRI 0-6=0x1c 7-11=rA 12-16=rB 17-23=imm 24-25=0x1 26=UF 3b
XRM 0-6=0x1e 7-11=rA 12-16=rB 17-21=rC 22-25=0x0 26=UF 3b
ZES 0-11=0xa09 12-16=rA 17-21=rB 22-26=0x0 3b
ZEW 0-11=0xa0a 12-16=rA 17-21=rB 22-26=0x0 3b'''

ISA_DEF = map(ParseISADefinitionLine, ISA_DEF_STR.strip().split('\n'))

ISA_DEF.sort(key=lambda x: x.opcode_bits)
# -------------------------------------------------