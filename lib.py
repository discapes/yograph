import asyncio
from typing import NamedTuple
from weakref import WeakKeyDictionary

from hishel.httpx import AsyncCacheClient

#proxy = "http://localhost:8080"
proxy = None

_clients: WeakKeyDictionary[asyncio.AbstractEventLoop, AsyncCacheClient] = WeakKeyDictionary()


def _get_client() -> AsyncCacheClient:
    loop = asyncio.get_running_loop()
    client = _clients.get(loop)
    if client is None:
        client = AsyncCacheClient(proxy=proxy, verify=(not proxy), follow_redirects=True)
        _clients[loop] = client
    return client


async def get(*args, **kwargs):
    client = _get_client()
    return await client.get(*args, **kwargs, extensions={"force_cache": not proxy})


class YtlDatum(NamedTuple):
    semester: str
    subject: str
    grade: str
    value: int | float


class Subject(NamedTuple):
    name: str
    ytl_name: str
    max_points: int
