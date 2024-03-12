import asyncio
import random
import sys
import time

from questionary import (
    questionary,
    Choice
)

from min_library.models.logger.logger import ConsoleLoggerSingleton
from min_library.utils.config import ACCOUNT_NAMES, PRIVATE_KEYS
from min_library.utils.helpers import delay, format_output
from settings.settings import (
    IS_ACCOUNT_NAMES,
    IS_SHUFFLE_WALLETS,
    IS_SLEEP
)
from tasks.swap_task import SwapTask


"""
    function_signature: 0xb1c76d29
    000: 0000000000000000000000009702230a8ea53601f5cd2dc00fdbc13d4df4a8c7
    020: 00000000000000000000000000000000000000000000000000000000004630c0
    040: 000000000000000000000000000000000000000000000000000000000045d6e8
    060: 0000000000000000000000000000000000000000000000000000000000000003
    080: 000000000000000000000000280f8024c2813471577fae235ebcb8103d658a64
    0a0: 00000000000000000000000000000000000000000000000000000000004630c0
    0c0: 000000000000000000000000000000000000000000000000000000000045d6e8
    0e0: 0000000000000000000000000000000000000000000000000000000000000066
    100: 00000000000000000000000000000000000000000000000000000000000001a0
    120: 000000000000000000000000000000000000000000000000003ba8b18dbfb992
    140: 0000000000000000000000000000000000000000000000000000000000000000
    160: 000000000000000000000000280f8024c2813471577fae235ebcb8103d658a64
    180: 0000000000000000000000000000000000000000000000000000000000000200
    1a0: 0000000000000000000000000000000000000000000000000000000000000022
    1c0: 0001000000000000000000000000000000000000000000000000000000000002
    1e0: 9810000000000000000000000000000000000000000000000000000000000000
    200: 0000000000000000000000000000000000000000000000000000000000000000
"""

def greetings():
    name_label = "========= zkBridge Minter Software ========="
    brand_label = "========== Author: M A K E D 0 N 1 A N =========="
    telegram = "======== https://t.me/crypto_maked0n1an ========"

    print("")
    format_output(name_label)
    format_output(brand_label)
    format_output(telegram)


def end_of_work():
    exit_label = "========= The bot has ended it's work! ========="
    format_output(exit_label)
    sys.exit()


def is_bot_setuped_to_start():
    end_bot = False

    if len(PRIVATE_KEYS) == 0:
        print("Don't imported private keys in 'private_keys.txt'!")
        return end_bot
    if len(ACCOUNT_NAMES) == 0 and IS_ACCOUNT_NAMES:
        print("Please insert names into account_names.txt")
        return end_bot
    if len(PRIVATE_KEYS) != len(ACCOUNT_NAMES) and IS_ACCOUNT_NAMES:
        print(
            "The account names' amount must be equal to private keys' amount"
        )
        return end_bot

    return True


def get_module():
    result = questionary.select(
        "Select a method to get started",
        choices=[
            Choice(
                "1) "
            ),
            Choice("2) Exit", "exit"),
        ],
        qmark="⚙️ ",
        pointer="✅ "
    ).ask()
    if result == "exit":
        exit_label = "========= Exited ========="
        format_output(exit_label)
        sys.exit()

    return result


def get_accounts():
    if IS_ACCOUNT_NAMES:
        accounts = [
            {
                "name": account_name,
                "key": key
            } for account_name, key in zip(ACCOUNT_NAMES, PRIVATE_KEYS)
        ]
    else:
        accounts = [
            {
                "name": _id,
                "key": key
            } for _id, key in enumerate(PRIVATE_KEYS, start=1)
        ]

    return accounts


async def run_module(module, wallet):
    return await module(wallet["name"], wallet["key"])


def measure_time_for_all_work(start_time: float):
    end_time = round(time.time() - start_time, 2)
    seconds = round(end_time % 60, 2)
    minutes = int(end_time // 60) if end_time > 60 else 0
    hours = int(end_time // 3600) if end_time > 3600 else 0

    logger.log(
        20,
        (
            f"Spent time: "
            f"{hours} hours {minutes} minutes {seconds} seconds"
        )
    )


async def main(module):
    accounts = get_accounts()

    if IS_SHUFFLE_WALLETS:
        random.shuffle(accounts)

    for account in accounts:
        is_result = await run_module(module, account)

        if IS_SLEEP and account != accounts[-1] and is_result:
            await delay(message='before next account')

if __name__ == '__main__':
    SwapTask.parse_params(
        params='0xb1c76d290000000000000000000000009702230a8ea53601f5cd2dc00fdbc13d4df4a8c700000000000000000000000000000000000000000000000000000000004630c0000000000000000000000000000000000000000000000000000000000045d6e80000000000000000000000000000000000000000000000000000000000000003000000000000000000000000280f8024c2813471577fae235ebcb8103d658a6400000000000000000000000000000000000000000000000000000000004630c0000000000000000000000000000000000000000000000000000000000045d6e8000000000000000000000000000000000000000000000000000000000000006600000000000000000000000000000000000000000000000000000000000001a0000000000000000000000000000000000000000000000000003ba8b18dbfb9920000000000000000000000000000000000000000000000000000000000000000000000000000000000000000280f8024c2813471577fae235ebcb8103d658a6400000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000022000100000000000000000000000000000000000000000000000000000000000298100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    )

    greetings()

    if not is_bot_setuped_to_start():
        exit_label = "========= The bot has ended it's work! ========="
        format_output(exit_label)
        sys.exit()

    module_data = get_module()

    start_time = time.time()
    logger = ConsoleLoggerSingleton.get_logger()
    logger.log(
        20, "The bot started to measure time for all work"
    )

    asyncio.run(main(module_data))

    measure_time_for_all_work(start_time)
    end_of_work()

