import string
from functools import wraps

from funcutils import pipe


def logger(loglevel=0):
    """ Make a decorator with appropriate level of logging """

    def log(func):
        """ Decorator to print info about function being called """

        @wraps(func)
        def wrapper(*args, **kwargs):
            if loglevel == 0: print 'doing %s' % func.__name__
            elif loglevel == 1:
                print '\ndoing: %s with args: %s and kwargs: %s'\
                      % (func.__name__, args, kwargs)
            result = func(*args, **kwargs)
            if loglevel == 1: print '\nresult: ', result
            return result
        return wrapper
    return log


def num_to_base(anint, alphabet):
    """ Convert a positive number to a base with supplied alphabet """

    n = anint
    base = len(alphabet)
    result = []
    while True:
        quotient, remainder = divmod(n, base)
        result.append(alphabet[remainder])
        if quotient == 0:
            break
        n = quotient
    return ''.join(reversed(result))


def num_to_base36(anint):
    alphabet = string.ascii_lowercase + string.digits
    return num_to_base(anint, alphabet)


def get_cachebusting_name(astr):
    """ Make a nice short readable str (mostly) uniquely representing a str """
    return pipe(astr, [hash, abs, num_to_base36])
