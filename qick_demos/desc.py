
import types
# from types import MethodType

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
        print("dummy2",self)
    def __setattr__(self,name,value):
        print("dummy2 setattr")
        setattr(self,name,value)

# the class that is used to stand in for anything
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
        #x = types.MethodType(dummy, self)
        setattr(self,name, self.dumb) #x)
        return self.dumb

    def g__getattribute__(self,name):
        print("gettattribute",name)
        return types.MethodType(dummy, self)

# try it out
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

done = False

while done==False:
    try:
        plt = Plot()
        plt.x()
        done=True
    except NameError as q:
        print("yuck!",q.args)
        Plot = Dummy
        