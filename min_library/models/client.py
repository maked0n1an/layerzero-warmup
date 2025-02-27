import asyncio
import random
from min_library.models.account.account_manager import AccountManager
from min_library.models.contracts.contract import Contract
from min_library.models.networks.network import Network
from min_library.models.networks.networks import Networks
from user_data.settings.settings import IS_CREATE_LOGS_FOR_EVERY_WALLET


class Client:
    def __init__(
        self,
        account_id: int | None = None,
        private_key: str | None = None,
        network: Network = Networks.Goerli,
        proxy: str | None = None,
        check_proxy: bool = True,
        create_log_file_per_account: bool = IS_CREATE_LOGS_FOR_EVERY_WALLET
    ) -> None:
        self.account_manager = AccountManager(
            account_id=account_id,
            private_key=private_key,
            network=network,
            proxy=proxy,
            check_proxy=check_proxy,
            create_log_file_per_account=create_log_file_per_account
        )

        self.contract = Contract(self.account_manager)
        
    async def step_delay(
        self,
        sleep_time: int,
        message: str = 'before next step'
    ) -> None:
        self.account_manager.custom_logger.log_message(
            "INFO", f"Sleeping {sleep_time} secs {message}"
        )
        await asyncio.sleep(sleep_time)
