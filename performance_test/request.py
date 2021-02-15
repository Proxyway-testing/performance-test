import asyncio
import re
import time
from typing import Optional

import aiohttp
from aiohttp_socks import SocksConnector

from . import provider as prv
from . import db


TIMEOUT = 30
HEADERS = {"Accept-Encoding": "gzip,deflate", "User-Agent": ""}
ERROR_CODES = [
    "400",
    "401",
    "402",
    "403",
    "404",
    "405",
    "406",
    "407",
    "408",
    "409",
    "410",
    "411",
    "412",
    "413",
    "414",
    "415",
    "416",
    "417",
    "418",
    "421",
    "425",
    "426",
    "428",
    "429",
    "431",
    "451",
    "500",
    "501",
    "502",
    "503",
    "504",
    "505",
    "506",
    "507",
    "510",
    "511",
    "522",
]


def _parse_ip_address(body: str) -> str:
    for line in body.splitlines():
        if "ip=" in line:
            return line.split("=")[1]
    return ""


def _identify_exception_code(exc: Exception) -> int:
    if isinstance(exc, asyncio.TimeoutError):
        # Return as a custom client timeout.
        return 997
    m = re.search(r"\d{3}", str(exc))
    if m:
        code = m.group(0)
        if code in ERROR_CODES:
            # Return as valid http error status code.
            return int(code)
    if "ssl:False" in str(exc):
        # Return as a custom SSL error.
        return 995
    # Return as an unrecognised error.
    return 999


class HttpResponse:
    """Class responsible for storing HTTP response results."""

    def __init__(self, title: str) -> None:
        self.provider = title
        self.ip: Optional[str] = None
        self.target_status: Optional[int] = None
        self.exception_status: Optional[int] = None
        self.response_time: Optional[float] = None


class Http:
    """Class responsible for HTTP GET requests."""

    def __init__(
        self,
        db_: db.Msql,
        provider_: prv.Provider,
        target: str,
    ) -> None:
        self._db = db_
        self._provider = provider_
        self._target = target

    async def request(self) -> None:
        proxy = self._provider.get_proxy()
        connector = None
        if proxy.startswith("socks5://"):
            connector = SocksConnector.from_url(proxy)
            proxy = ""
        session = aiohttp.ClientSession(connector=connector)
        results = HttpResponse(str(self._provider))
        try:
            start_time = time.time()
            response = await session.get(
                self._target,
                verify_ssl=False,
                proxy=proxy,
                timeout=TIMEOUT,
                headers=HEADERS,
            )
            body = await response.text()
            results.response_time = time.time() - start_time
            body = body.strip()
            status = response.status
            results.target_status = status
            if body and status == 200:
                ip = _parse_ip_address(body)
                if ip:
                    results.ip = ip
        except Exception as exc:
            exception_code = _identify_exception_code(exc)
            results.exception_status = exception_code
        finally:
            await self._db.insert_into_db(results.__dict__)
            await session.close()
