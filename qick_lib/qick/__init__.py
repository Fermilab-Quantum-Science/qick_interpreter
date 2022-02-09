import os
#import qick

def bitfile_path():
    src = os.path.join(os.path.dirname(qick.__file__), 'qick.bit')
    return src

from .qick import QickSoc
from .qick_asm import QickProgram,freq2reg,freq2reg_adc,reg2freq,reg2freq_adc, adcfreq, cycles2us, us2cycles, deg2reg, reg2deg
from .averager_program import AveragerProgram, RAveragerProgram

