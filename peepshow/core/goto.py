
class GoToLabel(Exception):
    pass

class Stop(GoToLabel):
    def __init__(self, *, exit):
        self.exit = exit

class NextCommand(GoToLabel):
    pass

