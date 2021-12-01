from qick import qick_asm
from qick import parser
import numpy as np

qp = qick_asm.QickProgram()
#p = parser.parse_prog("01_phase_calibration.asm")
p = parser.parse_prog("conditional_logic.asm")
#p = parser.parse_prog("math.asm")

# qp.instructions has all the opcode and instructions
# the binary opcode is a feature of the symbolic instruction, 
# this dictionary needs to be inverted: given a binary opcore, tell all the information about the instruction

# decode kinds of instructions
# need to finish these, extracting all of it, putting the data into a tuple or struct

def decode_I(word):
    page = ((word>>53)&0b111)
    ch   = ((word>>50)&0b111)
    oper = ((word>>46)&0b1111)
    ra   = ((word>>41)&0b11111)
    rb   = ((word>>36)&0b11111)
    rc   = ((word>>31)&0b11111)
    imm  = ((word>>0)&0b1111111111111111)


    return {'page':page,'ch':ch,'oper':oper,'ra':ra,'rb':rb,'rc':rc,'imm':imm}

def decode_J(word):
    page = ((word>>53)&0b111)
    oper = ((word>>46)&0b1111)
    ra   = ((word>>41)&0b11111)
    rb   = ((word>>36)&0b11111)
    rc   = ((word>>31)&0b11111)
    adr  = ((word>>0)&0b1111111111111111) 
    return {'page':page,'oper':oper,'ra':ra,'rb':rb,'rc':rc,'addr':adr}

def decode_end(word):
    return 0

def decode_R(word):
    page = ((word>>53)&0b111)
    ch   = ((word>>50)&0b111)
    oper = ((word>>46)&0b1111)
    ra   = ((word>>41)&0b11111)
    rb   = ((word>>36)&0b11111)
    rc   = ((word>>31)&0b11111)
    rd   = ((word>>26)&0b11111)
    re   = ((word>>21)&0b11111)
    rf   = ((word>>16)&0b11111)
    rg   = ((word>>11)&0b11111)
    rh   = ((word>>6)&0b11111) 
    return {'page':page,'ch':ch,'oper':oper,'ra':ra,'rb':rb,'rc':rc,'rd':rd,'re':re,'rf':rf,'rg':rg,'rh':rh}

math_fcns = {8 : np.add, 9 : np.subtract, 10 : np.multiply}
comparison_fcns = {0 : np.greater, 1 : np.greater_equal, 2 : np.less, 3 : np.less_equal, 4 : np.equal, 5 : np.not_equal}
bitw_fcns = {0 : np.logical_and, 1 : np.logical_or, 2 : np.logical_xor, 4 : np.left_shift, 5 : np.right_shift}

register_file = np.empty((8,32),dtype=np.uint)

stack = [[] for _ in range(8)]
ext_port = []
time_inst = []

data_mem = np.empty(2**16)
out_ch = [[] for _ in range(8)]

clk = 0

pc = 0

def reg_read(info,r):
    return register_file[info['page']][info[r]]

def reg_write(info,r,val):
    register_file[info['page']][info[r]] = val

def pushi(info):
    stack[info['page']].append(reg_read(info,'ra'))
    reg_write(info,'rb',info['imm'])
    

def popi(info):
    reg_write(info,'ra',stack[info['page']].pop())
    

def mathi(info):
    math_val = math_fcns[info['oper']](reg_read(info,'rb'),info['imm'])
    reg_write(info,'ra',math_val)
    

def seti(info):
    #data = [info['rb']]
    #data.append(info['page'])
    out_ch[info['page']] = [reg_read(info,'rb')]

"""
def seti_now(data):
    page = data.pop()
    out_ch.append([register_file[page][data[0]]])
"""


def synci(info):
    global clk
    clk = clk + info['imm'] - 1

def waiti(info):
    global clk
    clk = info['imm'] - 1
    

def bitwi(info):
    imm = info['imm']
    if info['oper'] == 3:
        val = ~imm
    else:
        #print(reg_read(info,'rb'),imm)
        val = bitw_fcns[info['oper']](int(reg_read(info,'rb')),imm)
    reg_write(info,'ra',val)
    

def memri(info):
    reg_write(info,'ra',data_mem[info['imm']])
    

def memwi(info):
    data_mem[info['imm']] = reg_read(info,'ra')
    

def regwi(info):
    reg_write(info,'ra',info['imm'])
    

def loopnz(info):
    global pc
    counter = reg_read(info,'ra')
    if counter != 0:
        reg_write(info,'ra',counter - 1)
        pc = info['addr'] - 1



def condj(info):
    global pc
    print(info)
    cond = comparison_fcns[info['oper']](reg_read(info,'ra'),reg_read(info,'rb'))
    if cond:
        pc = info['addr'] - 1


def end(info):
    global pc
    print("Done")
    pc = None

def math(info):
    math_val = math_fcns[info['oper']](reg_read(info,'rb'),reg_read(info,'rc'))
    reg_write(info,'ra',math_val)

def set(info):
    reads = ['rb','rd','re','rf','rg']
    #data = [info[r] for r in reads]
    #data.append(info['page'])
    out_ch[info['page']] = [reg_read(info,r) for r in reads]

"""
def set_now(data):
    page = data.pop()
    print('appending')
    [register_file[page][r] for r in data]
    out_ch.append([register_file[page][r] for r in data])
"""


def sync(info):
    global clk
    clk = clk + reg_read(info,'rc') - 1

def read(info):
    reg_write(info,'ra',ext_port.pop())

def wait(info):
    global clk
    clk = reg_read(info,'rc')

def bitw(info):
    rb = reg_read(info,'rb')
    rc = reg_read(info,'rc')
    if info['oper'] == 3:
        val = ~rc
    else:
        val = bitw_fcns[info['oper']](rb,rc)
    reg_write(info,'ra',val)

def memr(info):
    reg_write(info,'ra',reg_read(info,'rb'))

def memw(info):
    reg_write(info,'rb',reg_read(info,'ra'))

def schedule_time(program):
    if program[2] == 'seti':
        return program[4]['imm']
    elif program[2] == 'seti':
        return reg_read(program[4],'rc')

def sync_time(program):
    if program[2] == 'synci':
        return program[4]['imm']
    elif program[2] == 'sync':
        return reg_read(program[4],'rc')



codes = { v['bin']:(k,v['type']) for k,v in qp.instructions.items() }

disp = { 'I':decode_I, 'J1':decode_J, 'R':decode_R, 'J2':decode_J }

functions = {'pushi':(pushi,2), 'popi':(popi,2), 'mathi':(mathi,2), 'seti':(seti,2), 'synci':(synci,2), 'waiti':(waiti,2),
            'bitwi':(bitwi,2), 'memri':(memri,2), 'memwi':(memwi,2), 'regwi':(regwi,2), 'loopnz':(loopnz,2), 'condj':(condj,2),
            'end':(end,2), 'math':(math,2), 'set':(set,2), 'sync':(sync,2), 'read':(read,2), 'wait':(wait,2), 'bitw':(bitw,2),
            'memr':(memr,2), 'memw':(memw,2)}

program = []


for i,inst in enumerate(p.values()):
    #print(inst)
    word = int(inst,2)
    opcode = (word>>56)&0xff
    name = codes[opcode][0]
    typ = codes[opcode][1]
    #print(opcode,name,typ,word)
    program.append([i,opcode,name,typ,disp[typ](word)])
    #print(disp[typ](word))

print("____PARSED_PROGRAM____")
for p in program:
    print(p)
print("______________________")


out_ch_clk = []

"""
clk_schedule = 0
timed_program = []
for p in program:
    if p[2] == 'set' or p[2] == 'seti':
        time = schedule_time(p)
        if time != None:
            timed_program.append([time,p])
        else:
            timed_program.append([clk_schedule,p])
            clk_schedule = clk_schedule + functions_time[p[2]]
    elif p[2] == 'sync' or 'synci':
        time = sync_time(p)
        if time != None:
            clk_schedule = time
        else:
            clk_schedule = clk_schedule + functions_time[p[2]]
    else:
        timed_program.append([clk_schedule,p])
        clk_schedule = clk_schedule + functions_time[p[2]]

print("____TIMED_PROGRAM____")
for p in timed_program:
    print(p)
print("______________________")

timed_program.sort()
previous_time = timed_program[0]
for timed_p in timed_program[1:]:
    if previous_time[0] == timed_p[0]:
        if reg_read(previous_time[1][4],'page') == reg_read(timed_p[1][4],'page'):
            print("______TIMING_WARNING______")
            print("{} and {} take place at same time".format(previous_time[1][2],timed_p[1][2]))
    previous_time = timed_p

for p in timed_program:
    functions[p[1][2]](p[1][4])

"""

while pc < len(program):
    functions[program[pc][2]](program[pc][4])
    
    if bool(time_inst):
        print("_____TIME INSTRUCTIONS_____")
        print(time_inst)
        print("___________________________")
        time_inst.sort()
        while time_inst[0][0] <= clk:
            if time_inst[0][1] == 'set':
                set_now(time_inst[0][2])
            elif time_inst[0][1] == 'seti':
                seti_now(time_inst[0][2])
            out_ch_clk.append(clk)
            time_inst = time_inst[1:]
            if not bool(time_inst):
                break
    if pc == None:
        break
    elif program[pc][2] == 'end':
        break
    pc = pc + 1
    clk = clk + 1


hex_register = []
for register in register_file:
    hex_vals = []
    for val in register:
        hex_vals.append(f'{val:016x}')
    hex_register.append(hex_vals)

for i,hex in enumerate(hex_register):
    print("_______PAGE_{}_______".format(i))
    for j,h in enumerate(hex):
        print("{} : {}".format(j,h))
    print("____________________")
#print(register_file)
print("____OUTPUT_CHANNEL____")
for ch in enumerate(out_ch):
    print("{}".format(ch))
print("_____________________________________")
