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
    
def count_calls(fn):
    @functools.wraps(fn)
    def wrapper(self, *args, **kwargs):
        key = fn.__qualname__
        count = self._redis.get(key)
        count = int(count) if count else 0
        count += 1
        self._redis.set(key, count)
        return fn(self, *args, **kwargs)
    return wrapper

# Decoration
Cache.store = count_calls(Cache.store)
