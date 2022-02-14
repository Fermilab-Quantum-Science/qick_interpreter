
import types
# from types import MethodType

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

def dummy(obj,*args,**kwargs):
    print("dummy",obj)

class dummy2:
    def __call__(self,*args,**kwargs):
        print("dummy2",self)
    def __setattr__(self,name,value):
        print("dummy2 setattr")
        setattr(self,name,value)

class Dummy:

    def __init__(self):
        self.boo = 12
        self.dumb = dummy2()

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
        print("gettattr",name)
        x = types.MethodType(dummy, self)
        setattr(self,name, self.dumb) #x)
        return self.dumb

    def g__getattribute__(self,name):
        print("gettattribute",name)
        return types.MethodType(dummy, self)


f = Dummy()
f.boo
f.glump
f.foo()
f.foo()
f.blob()
f.blob()
print(f.__dict__)


        