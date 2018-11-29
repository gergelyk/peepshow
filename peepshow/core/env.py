from types import SimpleNamespace

class Env(SimpleNamespace):
    def __init__(self, glo, loc):
        super().__init__(glo=glo, loc=loc)
        self.initial = {**glo, **loc}
        self.current = {**self.initial}

    def update(self, items):
        self.current.update(items)
