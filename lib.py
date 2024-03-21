# caching so we can develop faster and wont strain APIs
import asyncio
from typing import NamedTuple
import hishel
from httpx import AsyncClient

#proxy = "http://localhost:8080"
proxy = None

client = hishel.AsyncCacheClient(proxy=proxy, verify=(not proxy))
def get(*args, **kwargs):
    return client.get(*args, **kwargs, extensions={"force_cache": not proxy})

class YtlDatum(NamedTuple):
    semester: str
    subject: str
    grade: str
    value: int | float
    
class YleDatum(NamedTuple):
    semester: str
    subject: str
    question: str
    option: str
    answers: int | float
    
class Subject(NamedTuple):
    name: str
    ytl_name: str
    max_points: int
    link_regex: str
    yle_url: str