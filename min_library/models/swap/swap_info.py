import random

from min_library.models.networks.network import Network
from min_library.models.networks.networks import Networks


class SwapInfo:
    def __init__(
        self,
        from_token: str,
        to_token: str,
        slippage: float = 0.5,
        from_network: Network = Networks.Goerli,
        to_network: Network | None = None,
        amount: float | None = None,
        amount_from: float | None = None,
        amount_to: float | None = None,
        decimals: int = 5,
        min_percent: int | None = None,
        max_percent: int | None = None,
        gas_price: float | None = None,
        gas_limit: int | None = None,
        multiplier_of_gas: float | None = None
    ) -> None:
        """
        Initialize the SwapInfo class.

        Args:
            from_token (str): The token to swap from.
            to_token (str): The token to swap to.
            slippage (float): The slippage tolerance (default is 0.5).
            from_network (str | None): The source network for the swap (default is None).
            to_network (str | None): The target network for the swap (default is None).
            amount (float | None): The amount to swap (default is None).
            amount_from (float | None): The minimum amount for random amount generation.
            amount_to (float | None): The maximum amount for random amount generation.
            decimals (int): The number of decimal places for random amount generation (default is 5).
            min_percent (int | None): The minimum percentage for random amount generation.
            max_percent (int | None): The maximum percentage for random amount generation.
            multiplier_of_gas (int | None): A multiplier for gas calculation (default is None).
            gas_price (float | None): Gas price for the transaction (default is None).
            gas_limit (int | None): Gas limit for the transaction (default is None).

        """
        self.from_token = from_token
        self.to_token = to_token
        self.from_network = from_network
        self.to_network = to_network
        self.amount = amount
        self.slippage = slippage
        self.amount_by_percent = 0
        self.gas_price = gas_price
        self.gas_limit = gas_limit
        self.multiplier_of_gas = multiplier_of_gas
        if amount_from and amount_to:
            self.amount = self._get_random_amount(
                amount_from, amount_to, decimals=decimals)
        if min_percent and max_percent:
            self.amount_by_percent = self._get_random_amount_by_percent(
                min_percent, max_percent, decimals=decimals
            )

    def _get_random_amount(self, amount_from: float, amount_to: float, decimals: int):
        random_amount = round(random.uniform(amount_from, amount_to), decimals)
        return random_amount

    def _get_random_amount_by_percent(
        self,
        min_percent: int,
        max_percent: int,
        decimals: int
    ):
        random_percent_amount = round(
            random.uniform(min_percent, max_percent) / 100, decimals
        )
        return random_percent_amount
