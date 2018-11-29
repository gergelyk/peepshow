from IPython.core.magic import register_line_magic

@register_line_magic
def peep(target):
    """Peep the target.

    Usage:
        %peep target.

    Calls peep() from peepshow library.
    """

    import peepshow
    target = target.strip()
    if target:
        return peepshow.peep_(target)
    else:
        return peepshow.peep_()

del peep
del register_line_magic
