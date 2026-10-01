"""iss_cache.py - Cache et retry automatique"""
import json
import time
from pathlib import Path
from functools import wraps

CACHE_FILE = Path.home() / ".mapci_bot_cache.json"
_CACHE = {}
_CACHE_LOADED = False


def _load():
    global _CACHE, _CACHE_LOADED
    if _CACHE_LOADED:
        return
    if CACHE_FILE.exists():
        try:
            _CACHE.update(json.loads(CACHE_FILE.read_text()))
        except Exception:
            pass
    _CACHE_LOADED = True


def _save():
    try:
        CACHE_FILE.write_text(json.dumps(_CACHE, indent=2))
    except Exception:
        pass


def cached(ttl=60):
    """Décorateur : cache le résultat d'une fonction pendant TTL secondes."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _load()
            key = f"{func.__name__}:{args}:{tuple(sorted(kwargs.items()))}"
            now = time.time()
            if key in _CACHE:
                entry = _CACHE[key]
                if now - entry["t"] < ttl:
                    return entry["v"]
            result = func(*args, **kwargs)
            _CACHE[key] = {"t": now, "v": result}
            _save()
            return result
        return wrapper
    return decorator


def retry(max_attempts=3, delay=2):
    """Décorateur : retry en cas d'échec."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for i in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if i < max_attempts - 1:
                        time.sleep(delay * (i + 1))
            raise last_exc
        return wrapper
    return decorator


def clear():
    global _CACHE
    _CACHE = {}
    _save()


if __name__ == "__main__":
    @cached(ttl=5)
    def slow_add(a, b):
        print(f"  (calcul {a}+{b})")
        return a + b

    print(slow_add(1, 2))
    print(slow_add(1, 2))  # cached
    print(slow_add(2, 3))
