import asyncio
import time

from performance_test import db, provider, request


async def run_test(
    mysql_config: dict,
    target: str,
    proxies: list,
    test_time: int,
    requests_number: int,
    provider_name: str,
) -> None:
    db_ = db.Msql(**mysql_config)
    await db_.connect_to_db()
    provider_ = provider.Provider(title=provider_name, proxies=proxies)
    request_ = request.Http(db_=db_, provider_=provider_, target=target)
    interval = test_time / requests_number
    start = time.time()
    while True:
        asyncio.create_task(request_.request())
        if time.time() - start > test_time:
            break
        await asyncio.sleep(interval)
