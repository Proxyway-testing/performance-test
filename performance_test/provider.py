import random


class Provider:
    def __init__(self, title: str, proxies: list) -> None:
        self._title = title
        self._proxies = proxies

    def get_proxy(self) -> str:
        return random.choice(self._proxies)

    def __str__(self) -> str:
        return self._title
