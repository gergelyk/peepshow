import peepshow.core.dialect as dialect
from peepshow.utils import terminal
from peepshow.core.explorer import Explorer
from peepshow.utils.python import catch, nth
from peepshow.core.trans import TransformationMgr

class Context:
    def __init__(self, target, env):
        self.mgr = TransformationMgr(target, self)
        self._env = env
        self.explorer = Explorer(self)

    @property
    def env(self):
        predefined = {'_': self.target, 'catch': catch, 'nth': nth}
        self._env.update(predefined)
        return self._env

    @property
    def target(self):
        return self.mgr.selected.result

    @property
    def readable(self):
        return dialect.Readable().stringify(self.mgr.selected)

    def eval_(self, expr):
        return eval(expr, {}, self.env.current)

    def exec_(self, expr):
        exec(expr, {}, self.env.current)
