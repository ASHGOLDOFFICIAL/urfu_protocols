import pickle
import os
from collections import defaultdict
from time import time
from threading import Timer, Lock

DEFAULT_CACHE_FILE = 'dns_cache.pkl'


class DNSCache:
    def __init__(self, cleanup_interval=600, file=DEFAULT_CACHE_FILE):
        self.file = file
        self.cache = defaultdict(dict)
        self.cleanup_interval = cleanup_interval
        self._load_cache()
        self._start_gc_timer()

        self.lock = Lock()

    def get(self, qname, qtype):
        with self.lock:
            try:
                if qtype not in self.cache or qname not in self.cache[qtype]:
                    return None
                expire_time, records = self.cache[qtype][qname]
                if time() > expire_time:
                    self.cache[qtype].pop(qname, None)
                    return None
                return records
            except Exception as e:
                print(f"Cache get error: {e}")
                return None

    def put(self, qname, qtype, records, ttl):
        with self.lock:
            try:
                if not records:
                    return
                expire_time = time() + ttl
                self.cache[qtype][qname] = (expire_time, records)
            except Exception as e:
                print(f"Couldn't put: {e}")

    def save_cache(self):
        try:
            with open(self.file, 'wb') as cache_file:
                self._clear()
                pickle.dump(dict(self.cache), cache_file)
                print("Cache was saved")
        except Exception as e:
            print(f"Couldn't save cache: {e}")

    def _start_gc_timer(self):
        self.gc = Timer(self.cleanup_interval,
                        self._periodic_cleanup)
        self.gc.daemon = True
        self.gc.start()

    def _periodic_cleanup(self):
        self._clear()
        self._start_gc_timer()

    def _clear(self):
        try:
            current_time = time()
            for qtype in list(self.cache.keys()):
                self.cache[qtype] = {
                    qname: data for qname, data in self.cache[qtype].items()
                    if current_time <= data[0]
                }
        except Exception as e:
            print(f"Couldn't clear: {e}")

    def _load_cache(self):
        try:
            if os.path.exists(self.file):
                with open(self.file, 'rb') as f:
                    loaded_cache = pickle.load(f)
                    current_time = time()
                    for qtype, records in loaded_cache.items():
                        self.cache[qtype] = {
                            qname: data for qname, data in records.items()
                            if current_time <= data[0]
                        }
                print("Cache was loaded")
            else:
                print("Cache is empty")
        except Exception as e:
            print(f"Couldn't load cache: {e}")

    def __del__(self):
        self.save_cache()
        try:
            if self.gc:
                self.gc.cancel()
        except Exception as e:
            print(f"Timer cleanup error: {e}")
