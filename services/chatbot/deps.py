from fastapi import HTTPException
from .rate_limit import hits

RATE_LIMIT = 60  # req/min/IP


def check_rate_limit(ip: str):
    if hits.add(ip) > RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too Many Requests")
