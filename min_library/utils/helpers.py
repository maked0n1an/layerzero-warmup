import asyncio
import json
import os
import random
from typing import List

from aiohttp import (
    ClientSession
)

from min_library.models.logger.logger import console_logger
from user_data.settings.settings import (
    RETRY_COUNT
)
import min_library.models.others.exceptions as exceptions


def retry(func):
    async def _wrapper(*args, **kwargs):
        retries = 1

        while retries <= RETRY_COUNT:
            try:
                result = await func(*args, **kwargs)

                return result
            except Exception as e:
                await delay(60, f"One more retry: {retries}/{RETRY_COUNT}")
                retries += 1

    return _wrapper


async def delay(
    sleep_time: int,
    message: str = ""
) -> None:
    console_logger.info(f"Sleeping for {sleep_time} seconds {message}")

    await asyncio.sleep(sleep_time)


def format_output(message: str):
    print(f"{message:^80}")


def join_path(path: str | tuple | list) -> str:
    if isinstance(path, str):
        return path
    return str(os.path.join(*path))


def read_txt(path: str | tuple | list) -> List[str]:
    path = join_path(path)
    with open(path, 'r') as file:
        return [row.strip() for row in file]


def read_json(path: str | tuple | list, encoding: str | None = None) -> list | dict:
    path = join_path(path)
    return json.load(open(path, encoding=encoding))


async def sleep(sleep_from: int, sleep_to: int):
    random_value = random.randint(sleep_from, sleep_to)
    await asyncio.sleep(random_value)


async def make_request(
    method: str,
    url: str,
    headers: dict | None = None,
    **kwargs
) -> dict | None:
    async with ClientSession(headers=headers) as session:
        response = await session.request(method, url=url, **kwargs)

        status_code = response.status
        json_response = await response.json()

        if status_code <= 201:
            return json_response

        raise exceptions.HTTPException(
            response=json_response, status_code=status_code)
