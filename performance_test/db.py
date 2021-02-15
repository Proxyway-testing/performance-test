from aiomysql.sa import create_engine, result
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Table,
    MetaData,
    DateTime,
    Integer,
    Float,
)


def _make_proxies_table(table_name: str) -> Table:
    return Table(
        table_name,
        MetaData(),
        Column("id", BigInteger, primary_key=True),
        Column("ts", DateTime),
        Column("provider", String(64), nullable=False),
        Column("ip", String(64)),
        Column("target_status", Integer),
        Column("exception_status", Integer),
        Column("response_time", Float),
    )


class Msql:
    def __init__(
        self,
        host: str,
        db: str,
        table: str,
        *,
        port: int = None,
        user: str = None,
        password: str = None,
    ) -> None:
        self._host = host
        self._port = port
        self._db = db
        self._username = user
        self._password = password
        self._engine = None
        self._table = _make_proxies_table(table)

    async def connect_to_db(self) -> None:
        self._engine = await create_engine(
            host=self._host,
            port=self._port,
            db=self._db,
            user=self._username,
            password=self._password,
        )

    async def insert_into_db(self, results: dict) -> None:
        await self._exec(self._table.insert().values(results))

    async def _exec(self, query) -> result.ResultProxy:
        async with self._engine.acquire() as conn:
            res = await conn.execute(query)
            await conn.execute("commit")
            return res

    async def close(self) -> None:
        self._engine.close()
        await self._engine.wait_closed()
        self._engine = None
