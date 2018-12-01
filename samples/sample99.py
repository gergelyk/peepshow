from peepshow import show, peep
from peepshow import show_, peep_

class NS:
    class Foo:
        """ Bleh!
        """
        x = 12
        _a = 123
        __b = None

        w = [1,2,3]

        def __init__(self):
            self.y = 23
            self._c = 123
            self.__d = None

        def __bool__(self):
            return True

        def __gtx__(self):
            pass

xn = None
xl = [1,2,3]
xt = (1,2,3)
xi = (x for x in range(1000))
xd1 = {'k1':'v1', 'k2':'v2', 'k3':'v3'}
xd2 = {1: 11, 2: 22, 3: 33}
xd3 = {'k1': 11, 'k2': 22, 'k3': 33}
xs = {1,2,3}

idx = 1

txt = 'abcdefghijklmnopqrstuvwxyz'*5


def xf1(*args, **kwargs):
    #return (*args, *kwargs.values())
    return args[0]

def xf2(x: "descr") -> "ret":
    return

class xc:
    def foo(self):
        return 123

    def foo2(self):
        return 321

    def _bar(self):
        pass

    def __baz(self):
        pass

class xc2(xc):
    def __init__(self, a,b,c):
        self.aaa = 123

xo2 = xc2(0,0,0)

class xc3(str):
    pass

xo = xc()

def xg():
    while True:
        yield 123


def rai(x, y):
    if x > y:
        raise Exception('x is greater than y')
    return y-x


peep()
