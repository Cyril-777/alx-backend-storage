#!/usr/bin/env python3
"""
A function that uses the requests module to obtain the HTML content
of a particular URL and return it
"""

import redis
import requests
from functools import wraps


class CacheWeb:
    """
    A class for caching and tracking method calls.
    """

    def __init__(self):
        """ Initialize the Cache object"""
        self._redis = redis.Redis()

    def url_access_count(self, method):
        """
        A decorator for the get_page function.
        """
        @wraps(method)
        def wrapper(url):
            key = f"cached:{url}"
            cached_value = self._redis.get(key)
            if cached_value:
                return cached_value.decode("utf-8")

            key_count = f"count:{url}"
            html_content = method(url)

            self._redis.incr(key_count)
            self._redis.set(key, html_content, ex=10)
            self._redis.expire(key, 10)
            return html_content

        return wrapper

    @url_access_count
    def get_page(self, url: str) -> str:
        """
        Obtain the HTML content, track the number of accesses,
        and cache the result with a 10-second expiration.
        """
        results = requests.get(url)
        return results.text


if __name__ == "__main__":
    cache_web = CacheWeb()
    cache_web.get_page('http://slowwly.robertomurray.co.uk')
