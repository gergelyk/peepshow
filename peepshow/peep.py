
def peep(*args):
    """Examine local data.
    peep()   # examine all variables in the scope (locals cover globals)
    peep(x)  # examine x (name will be determined only if possible)
    """

    from peepshow.core import peep as core
    from peepshow.utils import python as utils
    from peepshow.core.trans import GloLoc, Given

    if len(args) > 1:
        raise TypeError("Too many arguments.")

    env = utils.caller_gloloc()

    if args:
        expr = utils.arg_names()[0]
        target = Given(args[0], expr)
    else:
        target = GloLoc(env.initial)

    last_target = core.peep(target, env)


def peep_(*args):
    """Examine local data.
    peep_()     # examine all variables in the scope (locals cover globals)
    peep_('x')  # examine x (name will be known as it is explicitely given)
    """

    from peepshow.core import peep as core
    from peepshow.utils import python as utils
    from peepshow.core.trans import GloLoc, Given

    if len(args) > 1:
        raise TypeError("Too many arguments.")

    expr = args[0]
    env = utils.caller_gloloc()

    if args:
        if not isinstance(expr, str):
            raise TypeError("Expression must be a string or None.")

        try:
            target = eval(expr, {}, env.initial)
        except:
            raise SyntaxError('Invalid expression.')

        target = Given(target, expr)
    else:
        target = GloLoc(env.initial)

    last_target = core.peep(target, env)
