
# PYTHONPATH=../qick_lib/ python interpreter.py 00a.asm
import sys
import os

import desc

#try:
#    plt.x()
#except NameError as q:
#    print("yuck!",q.args)

qpath=os.path.abspath(".")
sys.path.append(qpath+"/.")
sys.path.append(qpath+"/qick_lib")
sys.path.append(qpath+"/qick_demos")
sys.path.append(qpath+"/../qick_lib")
sys.path.append(qpath+"/../qick_demos")
print(sys.path)

import qick

print("DIR: ", dir())
print("TYPE: ", type(__builtins__), type(__builtin__))
import importlib
name="00Sendreceivepulse"
done=False

while not done:
    try:
        mod = importlib.import_module(name)
        done=True
        print(mod.__file__)
    except NameError as q:
        s = q.__str__().split("'")[1]
        if s == 'sys':
            print("this is not fool proof - looks like sys is needed in the imported module and it is not imported there.")
            sys.exit(-1)
        print("DIR: ",__name__,type(__builtins__))
        if type(__builtins__) == dict:
            __builtins__[s]=desc.Dummy()
        else:
            setattr(__builtins__,s,desc.Dummy())
        print("Bad name found:",s)

