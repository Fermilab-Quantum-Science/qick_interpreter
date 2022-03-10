
import numpy as np
import pandas as pd
import sys
import types

from qick import qick_asm
from qick import parser
from qick.qick_asm import QickProgram

class Queue(list):
    def push(self,time,action):
        # put the action into the correction place in the list
        # 
        return super().append( (time,action) )

    def pop(self):
        # need to catch the exception thrown when pop on empty 
        return super().pop(0) if len(self)>0 else None



class Action:
    def __init__(self, time, func):
        self.t=time
        self.f=func

    def __call__(self):
        self.func()

def mybin(mc):
    return format(mc, '#066b')

class State:
    def __init__(self,program="01_phase_calibration.asm"):

        self.program = program
        #print(type(program))
        p=None
        use_me=None

        if isinstance(program,str):
            print("using string version")
            p = parser.parse_prog(self.program)
            #print(f"Debug str: p[18] = {type(p[18])}, {p[18]}, {int(p[18],2)}")
            use_me = p.values()
        elif isinstance(program,QickProgram):
            print("using qick program version")
            p = program.compile(debug=False)
            #print(f"Debug pro: p[18] = {p[18]}, {bin(p[18])}")
            use_me = [mybin(i) for i in p]

        self.use_me = use_me
        nchans = 8
        nregs = 32
        memsize = 2**16

        self.clock=0
        self.offset=0
        self.pc=0
        self.queue = Queue()
        self.instructions = []
        self.timed_instructions = []
        self.stack = [[] for _ in range(nchans)]
        self.register_file = np.zeros((nchans,nregs),dtype=np.int32) 
        self.ext_port=[]
        # JBK - there may need to be one mem block per channel
        self.data_mem = np.zeros(memsize,dtype=np.int32)
        self.output_ch = [[] for _ in range(nchans)] # channels, stack, memory, registers, etc.

        # these look like class-level data
        qp = qick_asm.QickProgram()
        self.codes = { v['bin']:(k,v['type']) for k,v in qp.instructions.items() }
        self.disp = { 'I':self.decode_I, 'J1':self.decode_J, 'R':self.decode_R, 'J2':self.decode_J }

        # new logged items
        self.reg_state = []
        self.mem_changes = []
        self.inst_log = []

        # JBK - fixed the next loop so it works with the list of machine instructions
        for i,inst in enumerate(use_me):
            word = int(inst,2)
            opcode = (word>>56)&0xff
            name = self.codes[opcode][0]
            typ = self.codes[opcode][1]
            #print(inst,type(inst))
            #print(opcode,name,typ,word)
            self.instructions.append([i,opcode,name,typ,self.disp[typ](word)])
            
            #if name == 'set':
            #   print(self.disp[typ](word))

        #for inst in self.instructions:
        #    print(inst)
        InstrAction(self)()

    def get_current_instr(self):
        return self.instructions[self.pc][2]

    def decode_I(self,word):
        page = ((word>>53)&0b111)
        ch   = ((word>>50)&0b111)
        oper = ((word>>46)&0b1111)
        ra   = ((word>>41)&0b11111)
        rb   = ((word>>36)&0b11111)
        rc   = ((word>>31)&0b11111)
        #junk = ((word>>16)&0b1111111111111111)
        imm  = ((word>>0)&0b11111111111111111111111111111111)

        return {'page':page,'ch':ch,'oper':oper,'ra':ra,'rb':rb,'rc':rc,'imm':imm}

    def decode_J(self,word):
        page = ((word>>53)&0b111)
        oper = ((word>>46)&0b1111)
        ra   = ((word>>41)&0b11111)
        rb   = ((word>>36)&0b11111)
        rc   = ((word>>31)&0b11111)
        adr  = ((word>>0)&0b1111111111111111) 
        return {'page':page,'oper':oper,'ra':ra,'rb':rb,'rc':rc,'addr':adr}

    def decode_end(self,word):
        return 0

    def decode_R(self,word):
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

class TimedAction:
    def __init__(self, instr, state):
        self.oper=instr[0]
        self.data = instr[1]
        self.state=state
        self.last_instr = instr
        self.instr = instr[2]

    def __call__(self):
        state = self.state        
        instr = self.instr
        # print("inst = ",instr)
        instr_args = instr
        instr_name = self.oper
        state.inst_log.append((state.clock, state.pc, instr_args['page'], 
            instr_args.get('ch',None), instr_name, instr))

        if self.oper == 'seti':
            self.seti_now(self.data)
        elif self.oper == 'set':
            self.set_now(self.data)

    def get_action(self):
        return self.oper

    def get_page(self):
        return self.data[-1]

    def get_output_ch(self):
        return self.data[-2]

    def seti_now(self,data):
        page = data.pop()
        ch = data.pop()
        #print(page)
        self.state.output_ch[ch] = [self.state.register_file[page][data[0]]]
    
    def set_now(self,data):
        page = data.pop()
        #print('appending')
        ch = data.pop()
        out_data = [self.state.register_file[page][r] for r in data]
        #print(out_data)
        self.state.output_ch[ch] = out_data
 
class InstrAction:
    def __init__(self, state):
        # since the state holds the program counter, you really don't need the instruction held here
        self.state=state
        self.last_instr = None
        self.math_fcns = {8 : np.add, 9 : np.subtract, 10 : np.multiply}
        self.comparison_fcns = {0 : np.greater, 1 : np.greater_equal, 2 : np.less, 3 : np.less_equal, 4 : np.equal, 5 : np.not_equal}
        self.bitw_fcns = {0 : np.logical_and, 1 : np.logical_or, 2 : np.logical_xor, 4 : np.left_shift, 5 : np.right_shift}
        self.functions = {'pushi':(self.pushi,2), 'popi':(self.popi,2), 'mathi':(self.mathi,2), 'seti':(self.seti,2), 'synci':(self.synci,2), 'waiti':(self.waiti,2),
            'bitwi':(self.bitwi,2), 'memri':(self.memri,2), 'memwi':(self.memwi,2), 'regwi':(self.regwi,2), 'loopnz':(self.loopnz,2), 'condj':(self.condj,2),
            'end':(self.end,2), 'math':(self.math,2), 'set':(self.set,2), 'sync':(self.sync,2), 'read':(self.read,2), 'wait':(self.wait,2), 'bitw':(self.bitw,2),
            'memr':(self.memr,2), 'memw':(self.memw,2)}

    def __call__(self):
        # I don't have your code, this is your code that runs a given instruction
        # Assumes that you will need the state to execute the instruction (memory, ports, channels, registers)
        # unsolved here: if the instruction is 'set' or similar timed instruction, care must be taken to 
        #   build a TimedAction for the queue and add it with the proper time

        # JBK - why would this happen?
        if self.state.pc == None:
            return 

        state = self.state        
        instr = state.instructions[state.pc]
        instr_args = instr[4]
        instr_name = instr[2]
        state.inst_log.append((state.clock, state.pc, instr_args['page'], 
            instr_args.get('ch',-1), instr_name, instr_args))

        instr = self.state.instructions[self.state.pc]
        self.last_instr = instr
        self.functions[instr[2]][0](instr[4])
        pc=self.state.pc
                
        self.state.pc+=1
        if self.state.pc < len(self.state.instructions):
            self.state.queue.push(self.cycles_for_instruction(instr), InstrAction(self.state))
            self.state.queue.sort(key=lambda y: y[0])
            #print(self.state.queue)

    def get_action(self):
        if self.state.pc != None:
            return self.state.instructions[self.state.pc][2]
        else:
            return 'end'

    def get_page(self):
        if self.state.pc != None:
            return self.state.instructions[self.state.pc][4]['page']
        else:
            return 0

    def get_output_ch(self):
        return -1

    def cycles_for_instruction(self,instr):
        self.state.clock = self.state.clock + self.functions[instr[2]][1]
        return self.state.clock

    def reg_read(self,info,r):
        return self.state.register_file[info['page']][info[r]]

    def reg_write(self,info,r,val):
        #print(info['page'])
        # JBK - this is where we can record the register transactions
        addr = info[r]
        page = info['page']
        self.state.register_file[page][addr] = val
        # JBK - fix me!
        self.state.reg_state.append([self.state.clock, self.state.pc, page,'A']+self.state.register_file[page].tolist())

    def pushi(self,info):
        self.state.stack[info['page']].append(self.reg_read(info,'ra'))
        self.reg_write(info,'rb',info['imm'])
        

    def popi(self,info):
        self.reg_write(info,'ra',self.state.stack[info['page']].pop())
        

    def mathi(self,info):
        math_val = self.math_fcns[info['oper']](self.reg_read(info,'rb'),info['imm'])
        self.reg_write(info,'ra',math_val)
        

    def seti(self,info):
        data = [info['rb']]
        data.append(info['ch'])
        data.append(info['page'])
        
        self.state.queue.push(self.state.offset+info['imm'], TimedAction(['seti',data,info], self.state))

    def synci(self,info):
        self.state.offset = self.state.offset + info['imm']

    def waiti(self,info):
        self.state.clock = self.state.clock + info['imm'] - 1
        

    def bitwi(self,info):
        imm = info['imm']
        if info['oper'] == 3:
            val = ~imm
        else:
            #print(reg_read(info,'rb'),imm)
            val = self.bitw_fcns[info['oper']](int(self.reg_read(info,'rb')),imm)
        self.reg_write(info,'ra',val)
        

    def memri(self,info):
        self.reg_write(info,'ra',self.state.data_mem[info['imm']])
        

    def memwi(self,info):
        # JBK - this needs to be recorded as a memory transaction
        page = info['page']
        addr = info['imm']
        val = self.reg_read(info,'ra')
        self.state.data_mem[addr] = val
        self.state.mem_changes.append((self.state.clock, self.state.pc, page, addr, val))

    def regwi(self,info):
        #print(info['imm'])
        self.reg_write(info,'ra',info['imm'])
        

    def loopnz(self,info):
        counter = self.reg_read(info,'ra')
        #print(counter)
        if counter != 0:
            self.reg_write(info,'ra',counter - 1)
            self.state.pc = info['addr'] - 1



    def condj(self,info):
        #print(info)
        cond = self.comparison_fcns[info['oper']](self.reg_read(info,'ra'),self.reg_read(info,'rb'))
        if cond:
            self.state.pc = info['addr'] - 1


    def end(self,info):
        #print("Done")
        pass
        

    def math(self,info):
        math_val = self.math_fcns[info['oper']](self.reg_read(info,'rb'),self.reg_read(info,'rc'))
        self.reg_write(info,'ra',math_val)

    def set(self,info):
        #print(info)
        reads = ['rb','rd','re','rf','rg']
        data = [info[r] for r in reads]
        data.append(info['ch'])
        data.append(info['page'])
        #print(data)
        self.state.queue.push(int(self.state.offset + self.reg_read(info,'rc')), TimedAction(['set', data,info], self.state))

    def sync(self,info):
        self.state.offset = self.state.offset + self.reg_read(info,'rc') - 1

    def read(self,info):
        self.reg_write(info,'ra',self.state.ext_port.pop())

    def wait(self,info):
        self.state.clock = self.state.clock + self.reg_read(info,'rc')

    def bitw(self,info):
        rb = self.reg_read(info,'rb')
        rc = self.reg_read(info,'rc')
        if info['oper'] == 3:
            val = ~rc
        else:
            val = self.bitw_fcns[info['oper']](rb,rc)
        self.reg_write(info,'ra',val)

    def memr(self,info):
        # self.reg_write(info,'ra',self.reg_read(info,'rb'))
        self.reg_write(info,self.state.data_mem[self.reg_read(info,'rb')])

    # JBK - is this one supposed to modify memory or just registers?
    def memw(self,info):
        # self.reg_write(info,'rb',self.reg_read(info,'ra'))
        page = info['page']
        addr = self.reg_read(info,'rb')
        val = self.reg_read(info,'ra')
        self.state.data_mem[addr] = val
        self.state.mem_change.append((self.state.clock, self.state.pc, page, addr, val))

def retrieve_pulses(self):
    pulses = []
    for ch in self.channels.keys():
        for name,pulse in self.channels[ch]['pulses'].items():
            #print("except pulses=",pulse)
            if pulse['style'] != 'const':
                idata = pulse['idata'].astype(np.int16)
                qdata = pulse['qdata'].astype(np.int16)
                #print("idata=",idata)
                #print("qdata=",qdata)
                pulses.append([ch,pulse['style'],pulse['addr'], idata, qdata])
            elif pulse['style'] == 'const':
                length = pulse['length']
                pulses.append([ch,pulse['style'],pulse['addr'],length])
    return pulses

# I think Sim can just be a function that takes a program and produces the
# the State object, the log, and the results.
# Sim modifies the program: it adds pulse extraction without loading
# The results should include the loaded memory blocks, the asm, and
# the simulating of the asm execution.


# assumes time in the action is an absolute time to execute instruction
def simulate_run(state, pulses=None):
    log = []
    seq = []
    i = 0
    # print(state.register_file[3])
    ninstrs = len(state.instructions)

    # initialize memory with pulses


    while state.queue:
        #print(state.queue)
        val = state.queue.pop()
        if val==None: break
        time,action = val

        state.clock = time
        #print(time, state.pc)
        #if state.pc !=None:
        action_name = action.get_action()
        #print(action_name)
        #print(state.pc)
        log.append([state.clock,action_name,state.output_ch,action.get_page(),action.get_output_ch()])
        action()
        #seq.append((time,action.last_instr[1]))
        i += 1

    #print(i)
    #for i in range(16,22):
    #    print(state.register_file[3][i])

    # JBK - the next line is part of saving output (in the old format).
    # we need a separate save function in here.   The new format needs to also be collected
    # and then saved in the new save function.

    # print(state.register_file[3])
    pd.DataFrame(log,columns=['Time','Instruction','Output Channel','Page','Channel No']).to_csv("test_dataframe.csv")

    return {'oldlog':log, 'pulses':pulses, 'instruction_log':state.inst_log,
     'mem_changes':state.mem_changes, 'reg_state':state.reg_state, 'state':state}

def simulate_from_asm(asm_file:str):
    state=State(asm_file)
    return simulate_run(state)

def simulate(p):
    p.retrieve_pulses = types.MethodType(retrieve_pulses, p)
    #code = p.compile()
    pulses = p.retrieve_pulses()
    state=State(p)
    return simulate_run(state,pulses=pulses)

import csv
import base64

def save_results(results, prefix):
    pulses = results['pulses']
    inst_log = results['instruction_log']
    mem_changes = results['mem_changes']
    reg_state = results['reg_state']

    with open(prefix+"_instruction_log.csv",'w') as f:
        w = csv.writer(f)
        w.writerow(['time','id','page','channel','oper','args'])
        w.writerows(inst_log)

    with open(prefix+"_memory_changes.csv",'w') as f:
        w = csv.writer(f)
        w.writerow(['time','id','page','addr','value'])
        w.writerows(mem_changes)

    with open(prefix+"_register_state.csv",'w') as f:
        w = csv.writer(f)
        head = ['time','id','page','state']+[f'r{i}' for i in list(range(32))]
        w.writerow(head)
        w.writerows(reg_state)

    with open(prefix+"_pulses.csv",'w') as f:
        w=csv.writer(f)
        w.writerow(['channel','type','start','length','I','Q'])
        I=None
        Q=None

        for r in pulses:
            pre=[r[0],r[1],r[2]]
            if r[1]=='const':
                leng=r[3]
                I=np.ones(leng,dtype=np.int16) * 2**16
                Q=np.zeros(leng,dtype=np.int16)
            else:
                leng=r[3].size
                I=r[3]
                Q=r[4]

            I = base64.b64encode(I.tobytes())
            Q = base64.b64encode(Q.tobytes())
            row=pre + [leng,I.decode(),Q.decode()]
            w.writerow(row)


def read_results(prefix):
    name_pulses = prefix+"_pulses.csv"
    name_reg_state = prefix+"_register_state.csv"
    name_mem_changes = prefix+"_memory_changes.csv"
    name_inst_log = prefix+"_instruction_log.csv"

    pulses = []
    with open(name_pulses,'r') as f:
        r = csv.reader(f)
        header = next(r)
        for row in r:
            Ibuf = row[4]
            Qbuf = row[5]
            leng = int(row[3])
            Ibuf = base64.b64decode(Ibuf)
            Qbuf = base64.b64decode(Qbuf)
            I = np.ndarray(shape=leng,dtype=np.int16,buffer=Ibuf)
            Q = np.ndarray(shape=leng,dtype=np.int16,buffer=Qbuf)
            if row[1] == 'const':
                pulses.append([int(row[0]),row[1],int(row[2]),leng,0])
            else:
                pulses.append([int(row[0]),row[1],int(row[2]),leng,I,Q])

    reg_state=[]
    with open(name_reg_state,'r') as f:
        r = csv.reader(f)
        header = next(r)
        for row in r:
            reg_state.append([int(i) for i in row[0:3]]+[row[3]]+[int(i) for i in row[4:]])

    mem_changes=[]
    with open(name_mem_changes,'r') as f:
        r = csv.reader(f)
        header = next(r)
        for row in r:
            mem_changes.append([int(i) for i in row])

    inst_log=[]
    with open(name_inst_log,'r') as f:
        r = csv.reader(f)
        header = next(r)
        for row in r:
            inst_log.append([int(i) for i in row[0:4]]+[row[4],row[5]])

    return {'pulses':pulses, 'reg_state':reg_state, 'instruction_log':inst_log,
        'mem_changes':mem_changes}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("You must give an asm file as an argument")
        sys.exit(-1)

    res = simulate_from_asm(sys.argv[1])
    print(res)
