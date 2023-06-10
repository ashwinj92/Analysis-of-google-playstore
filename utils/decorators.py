from logging import debug
from time import time


def timeit(func):
    def inner(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        end = time()

        print(f'Function: {func.__name__}, Time: {end - start}')

        return result

    return inner
