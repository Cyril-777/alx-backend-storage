#!/usr/bin/env python3
"""
# TASKS:-
0. Writing strings to Redis
"""


import redis
import uuid
import functools


class Cache:
    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data) -> str:
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key, fn=None):
        data = self._redis.get(key)
        if data is not None and fn is not None:
            return fn(data)
        return data

    def get_str(self, key):
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key):
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

if __name__ == "__main__":
    cache = Cache()
