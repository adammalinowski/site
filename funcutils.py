""" Some utilities to allow more functional style """

from functools import partial


def file_to_str(file_path):
    """ Take file path, return file content str """

    with open(file_path, 'r') as a_file:
        file_content = a_file.read()
    return file_content


def str_to_file(file_path, astr):
    """ Take str & file path, write file """

    with open(file_path, 'w') as afile:
        afile.write(astr)


def lcompose(func_list, log=False):
    """ Take multiple 1-arg funcs, return func which applies LTR

    lcompose([a, b, c])(x) == lambda x: c(b(a(x)))

    """
    def composed(arg):
        for func in func_list:
            if log: print 'doing %s with' % func.__name__, arg
            arg = func(arg)
            if log: print 'result', arg
        return arg
    return composed


def rcompose(func_list, **kwargs):
    """ Take multiple 1-arg funcs, return func which applies RTL

    rcompose([a, b, c])(x) == lambda x: a(b(c(x)))

    """
    return lcompose(reversed(func_list), **kwargs)


def pipe(arg, func_list, log=False):
    """ pipe(x, [a, b]) == b(a(x)) """
    return lcompose(func_list, log=log)(arg)


def atr(method_str, *args, **kwargs):
    """ Return a func which calls attr of an object, transforming the object

    examples:
    - atr('lower')(astring) == astring.lower()
    - atr('split', ':')(astring) == astring.split(':')

    """
    return lambda obj: getattr(obj, method_str)(*args, **kwargs)


def fmap(func):
    """ A partially applied map, awaiting the seq argument """
    return partial(map, func)


def ffilter(func):
    """ A partially applied filter, awaiting the seq argument """
    return partial(filter, func)


def pmap(func, fix_args, seq):
    """ Map a partially applied function """
    return map(partial(func, *fix_args), seq)


def args(func):
    """ Take a func, return func which applies list of args to original func """
    return lambda arg_list: func(*arg_list)
