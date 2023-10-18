#!/usr/bin/env python3
"""
# TASKS:-
0. Writing strings to Redis
"""


import redis
import uuid
from typing import Callable
import functools


class Cache:
    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: str) -> str:
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Callable = None):
        data = self._redis.get(key)
        if data is not None and fn is not None:
            return fn(data)
        return data

    def get_str(self, key: str):
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str):
        return self.get(key, fn=int)


def call_history(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        inputKey = "{}:inputs".format(method.__qualname__)
        outputKey = "{}:outputs".format(method.__qualname__)
        self._redis.rpush(inputKey, str(args))
        result = method(self, *args, **kwargs)
        self._redis.rpush(outputKey, result)
        return result
    return wrapper


# Decoration
Cache.store = call_history(Cache.store)


def replay(method):
    inputKey = "{}:inputs".format(method.__qualname__)
    outputKey = "{}:outputs".format(method.__qualname__)

    inputs = Cache()._redis.lrange(inputKey, 0, -1)
    outputs = Cache()._redis.lrange(outputKey, 0, -1)

    print(f"{method.__qualname__} was called {len(inputs)} times:")

    for input_data, output_data in zip(inputs, outputs):
        input_str = input_data.decode("utf-8")
        print(f"{method.__qualname__}(*{input_str}) ->
              {output_data.decode('utf-8')}")


if __name__ == "__main__":
    cache = Cache()
