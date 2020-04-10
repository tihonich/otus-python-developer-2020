import redis
import logging
from time import time, sleep


class Store:
    def __init__(self, retry=5, cache_time=60):
        self.cache = dict()  # {'key': {'value': b"", 'timestamp': 0, 'cache_time': 0}}
        self.cache_time = cache_time
        self.retry = retry
        self.store = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=3)
        self.attempts = 0

    def do_store(self, command, *args):
        while self.attempts <= self.retry:
            try:
                value = getattr(self.store, command)(*args)
            except Exception as e:
                logging.info(f"Redis error: {e}, retry...")
                self.attempts += 1
                sleep(1)
            else:
                return value
        raise redis.exceptions.ConnectionError

    def get(self, key):
        return self.do_store('get', key)

    def set(self, key, value):
        return self.do_store('set', key, value)

    def cache_get(self, key):
        if key not in self.cache:
            return None
        value_dct = self.cache[key]
        value = value_dct['value']
        timestamp = value_dct['timestamp']
        cache_time = value_dct['cache_time']
        if time() - timestamp > cache_time:
            return None
        return value

    def cache_set(self, key, value, cache_time=None):
        cache_time = cache_time if cache_time else self.cache_time
        self.cache[key] = {
            'value': value.encode('utf8') if type(value) == str else value,
            'timestamp': time(),
            'cache_time': cache_time,
        }
        return True
