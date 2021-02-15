import asyncio
import types
from importlib.machinery import SourceFileLoader

import click

from performance_test import fs, test


@click.command()
@click.option(
    "--config_path",
    type=str,
    required=True,
    default="config.py",
    help="Path to config. Default: 'config.py'.",
)
@click.option(
    "--proxies_file",
    type=str,
    required=True,
    default="proxies.txt",
    help="Path to proxies file. Default: 'proxies.txt'. Each proxy must be separated "
    "with a new line and formatted in http format.",
)
@click.option(
    "--provider_name", type=str, required=True, help="Name of the proxy provider."
)
@click.option(
    "--test_time",
    type=int,
    required=True,
    help="Test time in seconds.",
)
@click.option(
    "--requests_number",
    type=int,
    required=True,
    help="How many requests to do in 'test_time' time period.",
)
def main(
    config_path: str,
    proxies_file: str,
    test_time: int,
    requests_number: int,
    provider_name: str,
) -> None:
    loader = SourceFileLoader("config", config_path)
    config = types.ModuleType(loader.name)
    loader.exec_module(config)
    basic_config = config.BASIC_CONFIG  # type: ignore
    mysql_config = basic_config["mysql"]
    target = basic_config["target"]
    proxies = fs.file_to_list(proxies_file)
    asyncio.get_event_loop().run_until_complete(
        test.run_test(
            mysql_config=mysql_config,
            target=target,
            proxies=proxies,
            test_time=test_time,
            requests_number=requests_number,
            provider_name=provider_name,
        )
    )


if __name__ == "__main__":
    main()
