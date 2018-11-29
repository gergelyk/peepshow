
def show(*args, **kwargs):
    """show(x, y, z=z) # print names & values of arguments
    names of args will be determined only if possible
    names of kwargs will be known as it is explicitely given
    """

    import miscutils.insp as insp
    from peepshow.core import show as core
    from peepshow.utils import python as utils

    if args or kwargs:
        # show specified variables
        if args:
            names = utils.arg_names()
        else:
            names = []
        names += [*kwargs.keys()]
        values = [*args] + [*kwargs.values()]
    else:
        # show all the user variables in scope of the caller
        env = utils.caller_gloloc()
        is_user_var = lambda item: not insp.isaccess(item[0]).special
        user_vars = filter(is_user_var, env.initial.items())
        names, values = zip(*user_vars)

    core.show(names, values)

def show_(*args, **kwargs):
    """show_('x', 'y', z='z') # print names & values of arguments
    values of args and kwargs are expressions to be evaluated in context of the caller
    values of args become names to be displayed
    names of kwargs become names to be displayed
    """

    import miscutils.insp as insp
    from peepshow.core import show as core
    from peepshow.utils import python as utils

    env = utils.caller_gloloc()

    if args or kwargs:
        # show specified variables
        names = [*args] + [*kwargs.keys()]
        exprs = [*args] + [*kwargs.values()]

        for expr in exprs:
            if not isinstance(expr, str):
                raise TypeError("Each expression must be a string.")

        values = [eval(expr, env.glo, env.loc) for expr in exprs]
    else:
        # show all the user variables in scope of the caller
        is_user_var = lambda item: not insp.isaccess(item[0]).special
        user_vars = filter(is_user_var, env.initial.items())
        names, values = zip(*user_vars)

    core.show(names, values)
