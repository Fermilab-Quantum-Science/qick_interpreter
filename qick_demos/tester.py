
# PYTHONPATH=../qick_lib/ python interpreter.py 00a.asm
import sys
import os

import desc

#try:
#    plt.x()
#except NameError as q:
#    print("yuck!",q.args)

qpath=os.path.abspath(".")
sys.path.append(qpath+"/qick_lib")
sys.path.append(qpath+"/../qick_lib")
print(sys.path)

import qick

import importlib
name="00_Send_receive_pulse"

try:
    mod = importlib.import_module(name)
    print(mod.__file__)
except NameError as q:
    print("Bad name found:",name)

