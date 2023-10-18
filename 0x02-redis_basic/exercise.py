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

def replay(method: Callable):
    """
    Display the history of calls of a particular function.
    """
    function_name = method.__qualname__
    input_key = "{}:inputs".format(function_name)
    output_key = "{}:outputs".format(function_name)

    inputs = cache._redis.lrange(input_key, 0, -1)
    outputs = cache._redis.lrange(output_key, 0, -1)
    print("{} was called {} times:".format(function_name, len(inputs)))
    for inp, outp in zip(inputs, outputs):
        print("{}(*{}) -> {}".format(function_name, inp.decode('utf-8'),
                                     outp.decode('utf-8')))

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

    @staticmethod
    def count_calls(method: Callable) -> Callable:
        """
        A decorator that counts the number of times a method is called.
        """
        key = method.__qualname__

        @wraps(method)
        def wrapper(self, *args, **kwargs):
            self._redis.incr(key)
            return method(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def call_history(method: Callable) -> Callable:
        """
        A decorator that stores the history of
        inputs and outputs for a method.
        """
        key = method.__qualname__

        @wraps(method)
        def wrapper(self, *args, **kwargs):
            input_str = str(args)
            self._redis.rpush(f"{key}:inputs", input_str)
            output = method(self, *args, **kwargs)
            self._redis.rpush(f"{key}:outputs", output)
            return output

        return wrapper

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
