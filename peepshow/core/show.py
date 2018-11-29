from peepshow.utils.python import prettify_expr, pformat

def show(names, values):
    """Show names of variables together with corresponding values."""
    for name, value in zip(names, values):
        print(f'{prettify_expr(name)} = {pformat(value)}')
