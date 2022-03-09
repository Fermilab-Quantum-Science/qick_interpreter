
import types
from typing import Any
import sys
import builtins
# from types import MethodType

def make_getattr():
    #f = builtins.getattr
    def __getattr__mine(name) -> Any:
        print(f'my getattr {name}')
        #return f(name)
        return globals()[name]
    return __getattr__mine

# this is an example from the manual on what MethodType does
class MethodType:
    "Emulate PyMethod_Type in Objects/classobject.c"

    def __init__(self, func, obj):
        print("MT init")
        self.__func__ = func
        self.__self__ = obj

    def __call__(self, *args, **kwargs):
        print("MT call")
        func = self.__func__
        obj = self.__self__
        return func(obj, *args, **kwargs)

# my dummy method
def dummy(obj,*args,**kwargs):
    print("dummy",obj)

# my dummy class used as the installed method
class dummy2:
    def __call__(self,*args,**kwargs):
        print("dummy2 call",self,args,kwargs)
        return 0
    def __setattr__(self,name,value):
        print("dummy2 setattr",name)
        setattr(self,name,value)
    def __getattr__(self,name):
        print("dummy2 getattr",name)
        return 1

# the class that is used to stand in for anything
class Dummy:

    def __init__(self):
        pass
        #self.boo = 12
        self.__dumb = dummy2()
        self.__dict = dict()

    def __set_name__(self, owner, name):
        print("F setname")
        self.public_name = name
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None):
        print("F get")
        if obj is None:
            return self
        return types.MethodType(self, obj)

    def __getattr__(self,name):
        print("Dummy gettattr",name)
        #x = types.MethodType(dummy, self)
        setattr(self,name, self.__dumb) #x)
        return self.__dumb

    def g__getattribute__(self,name):
        print("gettattribute",name)
        return types.MethodType(dummy, self)

    def __getitem__(self, key):
        return self.__dict.get(key, 0)

    def __setitem__(self, key,value):
        self.__dict[key] = value

#sys.modules[__name__] = Dummy()
oldgetattr = builtins.getattr
newgetattr = make_getattr()
builtins.__getattr__=newgetattr
#builtins.getattr=newgetattr


def withit(df, *args, **kwargs):
    pass

df = 10

withit(df, a)



# try it out
if __name__ == "__main__":
    f = Dummy()
    f.boo
    f.glump
    f.foo()
    f.foo()
    f.blob()
    f.blob()
    print(f.__dict__)

    f.val = 5
    print(f.val)
    print(f.__dict__)
    q=p
