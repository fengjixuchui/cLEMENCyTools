#!/usr/bin/env python3
import argparse, collections, io, os, pathlib, re, sys

def error(msg, *args):
    print(msg.format(*args), file=sys.stderr)
    sys.exit(2)

def serialize_sign(l, x):
    if x >= 1 << l-1:
        error('Offset too large')
    if x < -(1 << l-1):
        error('Offset too small')
    return x if x >= 0 else (1 << l) + x

def serialize_unsigned(l, x):
    if x >= 1 << l:
        error('Offset too large')
    if x < 0:
        error('Offset too small')
    return x

CONDITION = {
    'n': 0,
    'e': 1,
    'l': 2,
    'le': 3,
    'g': 4,
    'ge': 5,
    'no': 6,
    'o': 7,
    'ns': 8,
    's': 9,
    'sl': 10,
    'sle': 11,
    'sg': 12,
    'sge': 13,
    '': 15,
}

ADJ_RB = {
    '': 0,
    'i': 1,
    'd': 2,
}

def assemble(fin, output, format):
    table = {}
    with open((pathlib.Path(__file__).resolve().parent.parent / 'isa.txt').as_posix()) as f:
        for lineno, line in enumerate(f.readlines(), 1):
            inst, *fields, _nbytes = line.rstrip('\n').split()
            entry = []
            for field in fields:
                bits, rhs = field.split('=')
                bits = list(map(int, bits.split('-')))
                if len(bits) == 1:
                    l = 1
                else:
                    l = bits[1]-bits[0]+1
                # register

                if rhs in ('Adj_rB', 'Condition', 'imm', 'Location', 'mem_off', 'Memory_Flags', 'Offset', 'Reg_Count', 'UF', 'immS'):
                    entry.append((l, rhs))
                elif rhs.startswith('r'):
                    entry.append((l, 'r'))
                elif rhs.startswith('0x'):
                    entry.append((l, int(rhs, 16)))
                else:
                    error('{}: unknown recognized rhs `{}`', lineno, rhs)
                table[inst.upper()] = entry

    addr = opt_start
    label2addr = {}
    reloc = collections.defaultdict(list)
    code = []
    code_ends = []
    for lineno, line in enumerate(fin.readlines(), 1):
        line = re.sub(r'#.*', '', line.strip())
        if not line: continue
        m = re.match(r'^(\w+):$', line)
        if m:
            label = m.group(1)
            if label in label2addr:
                error('{}: label `{}` redefined', lineno, label)
            label2addr[m.group(1)] = addr
            for (addr0, n, l, typ) in reloc[label]:
                i = n
                end = n+l
                value = addr-addr0 if typ == 'rel' else addr
                while i < end:
                    j = min(i+9-i%9, end)
                    l -= j-i
                    code[addr0+i//9] = code[addr0+i//9] & ~((1<<j-i)-1 << (9-j)%9) | (value>>l) << (9-j)%9
                    value &= (1 << l) - 1
                    i = j
            del reloc[label]
        else:
            if ' ' in line:
                inst, rest = line.split(' ', 1)
            else:
                inst, rest = line, ''
            inst = inst.upper()
            uf = False
            if inst.endswith('.'):
                uf = True
                inst = inst[:-1]
            for i in ['BR', 'B', 'CR', 'C']:
                if inst.startswith(i):
                    cc = inst[len(i):].lower()
                    if cc not in CONDITION:
                        continue
                        # error('{}: unknown condition code `{}`', lineno, cc)
                    inst = i
                    break
            for i in ['LDS', 'LDT', 'LDW', 'STS', 'STT', 'STW']:
                if inst.startswith(i):
                    adj_rb = inst[len(i):].lower()
                    inst = i
                    if adj_rb not in ADJ_RB:
                        error('{}: unknown Adj_rB suffix `{}`', lineno, adj_rb)
                    m = re.match(r'(\w+),\[(\w+)([+-][\dx]+)?,([\dx]+)\]', rest.replace(' ', ''))
                    if not m:
                        error('{}: {} invalid operands', lineno, inst)
                    ops = [m.group(1), m.group(2), m.group(4), m.group(3) or '0']
                    break
            else:
                ops = [i.strip() for i in rest.split(',')]
            if inst not in table:
                error('Unknown instruction `{}`'.format(inst))

            entry = table[inst]
            # most instructions

            #from ipdb import set_trace; set_trace()
            nth = x = n = 0
            for l, i in entry:
                if i in ('imm', 'mem_off', 'immS'):
                    nth += 1
                    if not ops:
                        error('{}: instruction `{}`: missing operand {}', lineno, inst, nth)
                    try:
                        if i == 'immS':
                            x = x << l | serialize_sign(l, int(ops.pop(0), 0))
                        else:
                            x = x << l | serialize_unsigned(l, int(ops.pop(0), 0))
                    except ValueError:
                        error('{}: invalid immediate number', lineno)
                elif i == 'Adj_rB':
                    x = x << l | ADJ_RB[adj_rb]
                elif i == 'Condition':
                    x = x << l | CONDITION[cc]
                elif i == 'Memory_Flags':
                    nth += 1
                    t = ops.pop(0)
                    try:
                        t = int(t, 0)
                    except ValueError:
                        t = t.upper()
                        if t == '':
                            t = 0
                        elif t == 'R':
                            t = 1
                        elif t == 'RW':
                            t = 2
                        elif t == 'RE':  # TODO check
                            t = 3
                    x = x << l | t
                elif i == 'Reg_Count':
                    # !!! minus 1
                    nth += 1
                    if not ops:
                        error('{}: instruction `{}`: missing operand {}', lineno, inst, nth)
                    x = x << l | int(ops.pop(0))-1
                elif i == 'r':
                    nth += 1
                    if not ops:
                        error('{}: instruction `{}`: missing operand {}', lineno, inst, nth)
                    t = ops.pop(0).upper()
                    if t == 'ST':
                        t = 29
                    elif t == 'RA':
                        t = 30
                    elif t == 'PC':
                        t = 31
                    else:
                        m = re.match(r'r(\d+)$', t, re.I)
                        if not m:
                            error('{}: register operand', lineno)
                        t = int(m.group(1))
                    x = x << l | t
                elif i == 'Location':
                    nth += 1
                    t = ops.pop(0)
                    try:
                        t = int(t, 0)
                    except ValueError:
                        if t in label2addr:
                            t = label2addr[t]
                        else:
                            reloc[t].append((addr-opt_start, n, l, 'abs'))
                            t = -1
                    x = x << l | serialize_sign(l, t)
                elif i == 'Offset':
                    nth += 1
                    t = ops.pop(0)
                    try:
                        t = int(t, 0)
                    except ValueError:
                        if t in label2addr:
                            t = label2addr[t]-addr
                        else:
                            reloc[t].append((addr-opt_start, n, l, 'rel'))
                            t = -1
                    x = x << l | serialize_sign(l, t)
                elif i == 'UF':
                    x = x << l | (1 if uf else 0)
                    uf = False
                elif isinstance(i, int):
                    x = x << l | i
                else:
                    error('{}: unknown recognized `{}`', lineno, i)
                n += l

            if uf:
                error('{}: `{}` does not have UF', lineno, inst)
            assert n % 9 == 0, 'Unaligned op, please check'
            addr += n // 9
            code_ends.append(addr)
            while n >= 9:
                code.append(x >> n-9)
                x &= (1 << n-9) - 1
                n -= 9
            label = None

    if reloc:
        error('Unknown labels {}', ' '.join(reloc.keys()))

    # middle endian
    addr = 0
    for i in code_ends:
        for j in range(addr, i-1, 3):
            code[j], code[j+1] = code[j+1], code[j]
        addr = i

    if format == '9bit':
        fout = sys.stdout if output == '-' else open(output, 'w')
        for i in code:
            fout.write('{:03x} '.format(i))
        fout.close()
    elif format == 'bin':
        fout = sys.stdout if output == '-' else open(output, 'w')
        for i in code:
            fout.write('{:09b} '.format(i))
        fout.close()
    elif format == 'octet':
        n = x = 0
        buf = bytearray()
        for i in code:
            x = x << 9 | i
            n += 9
            while n >= 8:
                buf.append(x >> n-8)
                x &= (1 << n-8) - 1
                n -= 8
        if n > 0:
            buf.append(x << 8-n)
        fout = sys.stdout if output == '-' else open(output, 'wb')
        fout.write(bytes(buf))
        fout.close()
    elif format == 'hextet':
        n = x = 0
        buf = bytearray()
        for i in code:
            buf.append(i & 255)
            buf.append(i >> 8)
        fout = sys.stdout if output == '-' else open(output, 'wb')
        fout.write(bytes(buf))
        fout.close()

def main():
    global opt_start
    ap = argparse.ArgumentParser(description='cLEMENCy assembler', formatter_class=argparse.RawDescriptionHelpFormatter, epilog='''
Examples:
./as.py -f 9bit clemency.s  # 100 120 003
./as.py -f bin clemency.s  # 100000000 100100000
./as.py -f octet clemency.s -o clemency.o
./as.py -f hextet clemency.s -o clemency.16  # used with convert-bits.py
    ''')
    ap.add_argument('-f', '--format', default='9bit', choices=('bin', 'octet', 'hextet', '9bit'), help='output format')
    ap.add_argument('-o', '--output', default='-', help='output filename')
    ap.add_argument('-s', '--start-address', type=int, default=0, help='start address')
    ap.add_argument('asm_file', help='')
    args = ap.parse_args()
    opt_start = args.start_address
    if args.asm_file == '-':
        assemble(sys.stdin, args.output, args.format)
    else:
        with open(args.asm_file, 'r') as fin:
            assemble(fin, args.output, args.format)

if __name__ == '__main__':
    main()
