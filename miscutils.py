import string
import logging
from functools import wraps


actual_logger = logging.getLogger("logger")


def logger():
    """ Make a decorator with appropriate level of logging """

    def log(func):
        """ Decorator to print info about function being called """

        @wraps(func)
        def wrapper(*args, **kwargs):
            actual_logger.info('doing %s' % func.__name__)
            actual_logger.debug('with args: %s and kwargs: %s' % ( args, kwargs))
            result = func(*args, **kwargs)
            actual_logger.debug('\nresult: %s' % result)
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


def nice_date(dt):
    def suffix(day):
        if 4 <= day <= 20 or 24 <= day <= 30:
            return "th"
        else:
            return ["st", "nd", "rd"][(day % 10) - 1]
    return dt.strftime('%d{S} %B, %Y'.replace('{S}', suffix(dt.day)))
