#!/usr/bin/env python3
"""
# TASKS:-
0. Writing strings to Redis
1. Reading from Redis and recovering original type
2. Incrementing values
3. Storing lists
4. Retrieving lists
"""


from functools import wraps
from typing import Union, Callable, Optional
import redis
from uuid import uuid4


def count_calls(method: Callable) -> Callable:
    """
    A decorator that counts the number of times a function is called.
    """
    key = method.__qualname__

    @wraps(method)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return method(*args, **kwargs)

    wrapper.calls = 0
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    A decorator that stores the history of inputs and outputs for a function.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """"wrap decorated function"""
        inputKey = "{}:inputs".format(method.__qualname__)
        outputKey = "{}:outputs".format(method.__qualname__)
        input = str(args)
        self._redis.rpush(inputKey, input)
        output = str(method(self, *args, **kwargs))
        self._redis.rpush(outputKey, output)
        return output
    return wrapper


class Cache:
    """
    A class for caching and tracking method calls.
    """

    def __init__(self):
        """
        Initialize the Cache object with a Redis client
        instance and flush the database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the input data in Redis and return a randomly generated key.
        """
        random_key = str(uuid4())
        self._redis.set(random_key, data)
        return random_key

    def get(self, key: str, fn: Optional[Callable] = None) ->\
            Union[bytes, str, int, float]:
        """
        Retrieve data from Redis with an optional data conversion function.
        """
        value = self._redis.get(key)
        if fn:
            value = fn(value)
        return value

    def get_str(self, key: str) -> str:
        """
        Retrieve data from Redis and decode it as a UTF-8 string.
        """
        return self.get(key, fn=lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """
        Retrieve data from Redis and convert it to an integer.
        """
        return self.get(key, fn=lambda x: int(x.decode('utf-8')))


def replay(cache, method: Callable):
    """
    Display the history of calls of a particular function.
    """
    function_name = method.__qualname__
    inputKey = "{}:inputs".format(function_name)
    outputKey = "{}:outputs".format(function_name)

    inputs = cache._redis.lrange(inputKey, 0, -1)
    outputs = cache._redis.lrange(outputKey, 0, -1)
    print("{} was called {} times:".format(function_name, len(inputs)))
    for inp, outp in zip(inputs, outputs):
        print("{}(*{}) -> {}".format(function_name, inp.decode('utf-8'),
                                     outp.decode('utf-8')))
