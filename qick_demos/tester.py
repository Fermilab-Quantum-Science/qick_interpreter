
# PYTHONPATH=../qick_lib/ python interpreter.py 00a.asm
import sys
import os

try:
    plt.x()
except NameError as q:
    print("yuck!",q.args)

def missing(s,k):
    print(k)

class Piglet(dict):
    def __missing__(self,m):
        print(m)
    def __init__(self):
        print("init")

p = Piglet()
p["thing"]

class Thing:
    def __init__(self):
        self.__dict__

sys.exit(0)

qpath=os.path.abspath(".")
sys.path.append(qpath+"/qick_lib")
sys.path.append(qpath+"/../qick_lib")
print(sys.path)

import qick

import importlib
name="00_Send_receive_pulse"
mod = importlib.import_module(name)

print(mod.__file__)
