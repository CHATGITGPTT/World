import sys, pathlib

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from services.chatbot.rate_limit import TTLHits


def test_ttlhits_prunes_and_cleans():
    h = TTLHits(ttl_seconds=1)
    h.add("1", ts=0.0)
    h.add("1", ts=0.5)
    h.add("1", ts=1.0)
    assert h.count("1", ts=1.0) == 3
    h._prune("1", now=2.1)
    assert h.count("1", ts=2.1) == 0
    assert "1" not in h.data
