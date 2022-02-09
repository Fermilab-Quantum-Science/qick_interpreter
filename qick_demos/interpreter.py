import numpy as np
import pandas as pd
from qick import qick_asm
from qick import parser
import sys

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

class State:
    def __init__(self,program="01_phase_calibration.asm"):
        self.clock=0
        self.offset=0
        self.pc=0
        self.queue = Queue()
        self.instructions = []
        self.timed_instructions = []
        self.stack = [[] for _ in range(8)]
        self.register_file = np.zeros((8,32)) 
        self.ext_port=[]
        self.data_mem = np.empty(2**16)
        self.output_ch = [[] for _ in range(8)] # channels, stack, memory, registers, etc.
        qp = qick_asm.QickProgram()
        self.program = program
        p = parser.parse_prog(self.program)
        self.codes = { v['bin']:(k,v['type']) for k,v in qp.instructions.items() }
        self.disp = { 'I':self.decode_I, 'J1':self.decode_J, 'R':self.decode_R, 'J2':self.decode_J }
        for i,inst in enumerate(p.values()):
            #print(inst)
            word = int(inst,2)
            opcode = (word>>56)&0xff
            name = self.codes[opcode][0]
            typ = self.codes[opcode][1]
            #print(opcode,name,typ,word)
            self.instructions.append([i,opcode,name,typ,self.disp[typ](word)])
            if name == 'set':
                #print(self.disp[typ](word))
                pass
        for inst in self.instructions:
            print(inst)
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

    def __call__(self):
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
        
        if self.state.pc == None:
            return 
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
        self.state.register_file[info['page']][info[r]] = val

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
        self.state.queue.push(self.state.offset+info['imm'], TimedAction(['seti',data], self.state))

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
        self.state.data_mem[info['imm']] = self.reg_read(info,'ra')
        

    def regwi(self,info):
        print(info['imm'])
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
        print("Done")
        

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
        self.state.queue.push(int(self.state.offset + self.reg_read(info,'rc')), TimedAction(['set', data], self.state))

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
        self.reg_write(info,'ra',self.reg_read(info,'rb'))

    def memw(self,info):
        self.reg_write(info,'rb',self.reg_read(info,'ra'))


class Sim:
    def __init__(self,p):
        self.state=State(p)
        self.log = []
        #(len(self.state.instructions))
        #print(self.state.instructions)

    # assumes time in the action is an absolute time to execute instruction
    def run(self):
        seq = []
        i = 0
        print(self.state.register_file[3])
        while self.state.queue:
            #print(self.state.queue)
            val = self.state.queue.pop()
            if val==None: break
            time,action = val
            self.state.clock = time
            #print(time)
            #if self.state.pc !=None:
            action_name = action.get_action()
            #print(action_name)
            #print(self.state.pc)
            self.log.append([self.state.clock,action_name,self.state.output_ch,action.get_page(),action.get_output_ch()])
            action()
            #seq.append((time,action.last_instr[1]))
            i += 1
        #print(i)
        #for i in range(16,22):
        #    print(self.state.register_file[3][i])
        print(self.state.register_file[3])
        pd.DataFrame(self.log,columns=['Time','Instruction','Output Channel','Page','Channel No']).to_csv(self.state.program[:-4]+"_dataframe.csv")

Sim(sys.argv[1]).run()
