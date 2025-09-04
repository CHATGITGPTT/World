import time
from collections import defaultdict, deque


class TTLHits:
    def __init__(self, ttl_seconds: int = 60):
        self.ttl = ttl_seconds
        self.data: dict[str, deque[float]] = defaultdict(deque)

    def add(self, key: str, ts: float | None = None) -> int:
        now = ts if ts is not None else time.time()
        dq = self.data[key]
        dq.append(now)
        self._prune(key, now)
        return len(dq)

    def count(self, key: str, ts: float | None = None) -> int:
        now = ts if ts is not None else time.time()
        self._prune(key, now)
        return len(self.data.get(key, ()))

    def _prune(self, key: str, now: float):
        cutoff = now - self.ttl
        dq = self.data.get(key)
        if not dq:
            return
        while dq and dq[0] < cutoff:
            dq.popleft()
        if not dq:
            self.data.pop(key, None)


hits = TTLHits(ttl_seconds=60)
