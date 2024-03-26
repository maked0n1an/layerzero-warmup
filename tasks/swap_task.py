import asyncio
import aiohttp

from web3.types import (
    TxParams,
    TxReceipt,
    _Hash32,
)

from min_library.models.client import Client
from min_library.models.contracts.contracts import ContractsFactory
from min_library.models.others.constants import LogStatus, TokenSymbol
from min_library.models.others.params_types import ParamsTypes
from min_library.models.others.token_amount import TokenAmount
from min_library.models.swap.swap_info import SwapInfo
from min_library.models.swap.swap_query import SwapQuery


class SwapTask:
    def __init__(self, client: Client):
        self.client = client

    @staticmethod
    def parse_params(
        params: str,
        has_function: bool = True
    ) -> None:
        if has_function:
            function_signature = params[:10]
            print('function_signature:', function_signature)
            params = params[10:]

        count = 0
        while params:
            memory_address = hex(count * 32)[2:].zfill(3)
            print(f'{memory_address}: {params[:64]}')
            count += 1
            params = params[64:]

    def to_cut_hex_prefix_and_zfill(self, data: str, length: int = 64):
        """
        Convert the string to lowercase and fill it with zeros to the specified length.

        Args:
            length (int): The desired length of the string after filling.

        Returns:
            str: The modified string.
        """
        return data[2:].zfill(length)

    def set_all_gas_params(
        self,
        swap_info: SwapInfo,
        tx_params: dict | TxParams | None = None
    ) -> dict | TxParams:
        
        if not tx_params:
            tx_params = TxParams()
        
        if swap_info.gas_limit:
            tx_params = self.client.contract.set_gas_limit(
                gas_limit=swap_info.gas_limit,
                tx_params=tx_params
            )

        if swap_info.gas_price:
            tx_params = self.client.contract.set_gas_price(
                gas_price=swap_info.gas_price,
                tx_params=tx_params
            )

        if swap_info.multiplier_of_gas:
            tx_params = self.client.contract.add_multiplier_of_gas(
                multiplier=swap_info.multiplier_of_gas,
                tx_params=tx_params
            )

        return tx_params

    def validate_swap_inputs(
        self,
        first_arg: str,
        second_arg: str,
        param_type: str = 'args',
        function: str = 'swap'
    ) -> str:
        """
        Validate inputs for a swap operation.

        Args:
            first_arg (str): The first argument.
            second_arg (str): The second argument.
            param_type (str): The type of arguments (default is 'args').
            message (str): The message (default is 'swap')

        Returns:
            str: A message indicating the result of the validation.

        Example:
        ```python
        result = validate_swap_inputs('ETH', 'ETH', param_type='symbols')
        print(result)
        # Output: 'The symbols for swap() are equal: ETH == ETH'
        ```
        """
        if first_arg.upper() == second_arg.upper():
            return f'The {param_type} for {function}() are equal: {first_arg} == {second_arg}'

    async def approve_interface(
        self,
        swap_info: SwapInfo,
        token_contract: ParamsTypes.TokenContract,
        spender_address: ParamsTypes.Address,
        amount: ParamsTypes.Amount | None = None,
        tx_params: TxParams | dict | None = None,
        is_approve_infinity: bool = None
    ) -> str | bool:
        """
        Approve spending of a specific amount by a spender on behalf of the owner.

        Args:
            token_contract (ParamsTypes.TokenContract): The token contract instance.
            spender_address (ParamsTypes.Address): The address of the spender.
            amount (TokenAmount | None): The amount to approve (default is None).
            gas_price (float | None): Gas price for the transaction (default is None).
            gas_limit (int | None): Gas limit for the transaction (default is None).
            is_approve_infinity (bool): Whether to approve an infinite amount (default is True).

        Returns:
            bool: True if the approval is successful, False otherwise.

        Example:
        ```python
        approved = await approve_interface(
            token_contract=my_token_contract,
            spender_address='0x123abc...',
            amount=TokenAmount(amount=100, decimals=18),
            gas_price=20,
            gas_limit=50000,
            is_approve_infinity=False
        )
        print(approved)
        # Output: True
        ```
        """
        balance = await self.client.contract.get_balance(
            token_contract=token_contract
        )
        if balance.Wei <= 0:
            return True

        if not amount or amount.Wei > balance.Wei:
            amount = balance

        approved = await self.client.contract.get_approved_amount(
            token_contract=token_contract,
            spender_address=spender_address,
            owner=self.client.account_manager.account.address
        )

        if amount.Wei <= approved.Wei:
            return True

        tx_params = self.set_all_gas_params(
            swap_info=swap_info,
            tx_params=tx_params
        )

        tx_hash = await self.client.contract.approve(
            token_contract=token_contract,
            spender_address=spender_address,
            amount=amount,
            tx_params=tx_params,
            is_approve_infinity=is_approve_infinity
        )

        return tx_hash

    async def compute_source_token_amount(
        self,
        swap_info: SwapInfo
    ) -> SwapQuery:
        """
        Compute the source token amount for a given swap.

        Args:
            swap_info (SwapInfo): Information about the swap.

        Returns:
            SwapQuery: The query for the swap.

        Example:
        ```python
        swap_query = await compute_source_token_amount(swap_info=my_swap_info)
        print(swap_query)
        # Output: SwapQuery(from_token=..., to_token=..., amount_to=...)
        ```
        """
        from_token = ContractsFactory.get_contract(
            network_name=self.client.account_manager.network.name,
            token_symbol=swap_info.from_token
        )

        if from_token.is_native_token:
            balance = await self.client.contract.get_balance()
            decimals = balance.decimals

        else:
            balance = await self.client.contract.get_balance(from_token)
            decimals = balance.decimals

        if not swap_info.amount:
            token_amount = balance

        elif swap_info.amount:
            token_amount = TokenAmount(
                amount=swap_info.amount,
                decimals=decimals
            )

            if token_amount.Wei > balance.Wei:
                token_amount = balance

        elif swap_info.amount_by_percent:
            token_amount = TokenAmount(
                amount=balance.Wei * swap_info.amount_by_percent,
                decimals=decimals,
                wei=True
            )

        return SwapQuery(
            from_token=from_token,
            amount_from=token_amount
        )

    async def compute_min_destination_amount(
        self,
        swap_query: SwapQuery,
        min_to_amount: int,
        swap_info: SwapInfo,
        is_to_token_price_wei: bool = False
    ) -> SwapQuery:
        """
        Compute the minimum destination amount for a given swap (not works for cross-chain swaps).

        Args:
            swap_query (SwapQuery): The query for the swap.
            to_token_price (float): The price of the destination token.
            slippage (int): The slippage tolerance.

        Returns:
            SwapQuery: The updated query with the minimum destination amount.

        Example:
        ```python
        min_destination_query = await compute_min_destination_amount(
            swap_query=my_swap_query,
            to_token_price=my_token_price,
            slippage=1
        )
        print(min_destination_query)
        # Output: SwapQuery(from_token=..., to_token=..., amount_to=..., min_to_amount=...)
        ```
        """
        if not swap_query.to_token:
            swap_query.to_token = ContractsFactory.get_contract(
                network_name=self.client.account_manager.network.name,
                token_symbol=swap_info.to_token
            )

        decimals = 0
        if swap_query.to_token.is_native_token:
            decimals = self.client.account_manager.network.decimals

        else:
            decimals = await self.client.contract.get_decimals(
                token_contract=swap_query.to_token
            )

        min_amount_out = TokenAmount(
            amount=min_to_amount * (1 - swap_info.slippage / 100),
            decimals=decimals,
            wei=is_to_token_price_wei
        )

        return SwapQuery(
            from_token=swap_query.from_token,
            amount_from=swap_query.amount_from,
            to_token=swap_query.to_token,
            min_to_amount=min_amount_out
        )

    async def get_binance_ticker_price(
        self,
        first_token: str = TokenSymbol.ETH,
        second_token: str = TokenSymbol.USDT
    ) -> float | None:
        if first_token.startswith('W'):
            first_token = first_token[1:]

        if second_token.startswith('W'):
            second_token = second_token[1:]

        match first_token:
            case TokenSymbol.USDT:
                return 1
            case TokenSymbol.USDC:
                return 1
            case TokenSymbol.USDV:
                return 1
            case TokenSymbol.USDC_E:
                return 1

        async with aiohttp.ClientSession() as session:
            price = await self._get_price_from_binance(session, first_token, second_token)
            if price is None:
                price = await self._get_price_from_binance(session, first_token, second_token)
                return 1 / price

            return price

    async def get_token_info(self, token_address):
        contract = await self.client.contract.get_token_contract(token=token_address)
        print('name:', await contract.functions.name().call())
        print('symbol:', await contract.functions.symbol().call())
        print('decimals:', await contract.functions.decimals().call())

    async def perform_swap(
        self,
        swap_info: SwapInfo,
        swap_query: SwapQuery,
        tx_params: TxParams | dict,
    ) -> tuple[int, str, str]:
        """
        Perform a token swap operation.
        Args:
            swap_info (SwapInfo): Information about the swap.
            swap_query (SwapQuery): Query parameters for the swap.
            tx_params (TxParams | dict): Transaction parameters.
        Returns:
            tuple[bool, str, str]: A tuple containing:
                - A boolean indicating whether the swap was successful.
                - Status of the swap.
                - Message regarding the swap.
        """
        tx_params = self.set_all_gas_params(
            swap_info=swap_info,
            tx_params=tx_params
        )

        tx_hash, receipt = await self.perform_tx(tx_params)

        account_network = self.client.account_manager.network
        full_path = account_network.explorer + account_network.TxPath
        rounded_amount_from = round(swap_query.amount_from.Ether, 5)
        rounded_amount_to = round(swap_query.min_to_amount.Ether, 5)

        if receipt['status']:
            log_status = LogStatus.SWAPPED
            message = f'{rounded_amount_from} {swap_info.from_token}'

        else:
            log_status = LogStatus.ERROR
            message = f'Failed swap {rounded_amount_from} {swap_info.from_token}'

        message += (
            f' -> {rounded_amount_to} {swap_info.to_token}: '
            f'{full_path + tx_hash.hex()}'
        )

        return receipt['status'], log_status, message

    async def perform_bridge(
        self,
        swap_info: SwapInfo,
        swap_query: SwapQuery,
        tx_params: TxParams | dict,
        external_explorer: str = None
    ) -> tuple[int, str, str]:
        """
        Perform a bridge operation.

        Args:
            swap_info (SwapInfo): Information about the swap.
            swap_query (SwapQuery): Query parameters for the swap.
            tx_params (TxParams | dict): Transaction parameters.
            external_explorer (str, optional): External explorer URL. Defaults to None.

        Returns:
            tuple[str, str]: A tuple containing:
                - A boolean indicating whether the bridge operation was successful.
                - Log status of the bridge operation.
                - Message regarding the bridge operation.
        """
        tx_params = self.set_all_gas_params(
            swap_info=swap_info,
            tx_params=tx_params
        )

        tx_hash, receipt = await self.perform_tx(tx_params)

        account_network = self.client.account_manager.network

        if external_explorer:
            full_path = external_explorer + account_network.TxPath
        else:
            full_path = account_network.explorer + account_network.TxPath

        rounded_amount_from = round(swap_query.amount_from.Ether, 5)
        rounded_amount_to = round(swap_query.min_to_amount.Ether, 5)

        if receipt['status']:
            log_status = LogStatus.BRIDGED
            message = f'{rounded_amount_from} {swap_info.from_token}'
        else:
            log_status = LogStatus.ERROR
            message = f'Failed bridge {rounded_amount_from} {swap_info.from_token}'

        message += (
            f' from {account_network.name.upper()} -> '
            f'{rounded_amount_to} {swap_info.to_token}'
            f' in {swap_info.to_network.name.upper()}: '
            f'{full_path + tx_hash.hex()}'
        )

        return receipt['status'], log_status, message

    async def create_contract(
        self,
        swap_info: SwapInfo,
        recipient_address: str
    ) -> bool:
        try:
            query = await self.compute_source_token_amount(swap_info)            
            tx_params = self.set_all_gas_params(swap_info)

            receipt_status, tx_hash = await self.client.contract.transfer(
                token_contract=query.from_token,
                recipient_address=recipient_address,
                token_amount=query.amount_from,
                tx_params=tx_params
            )

            if receipt_status and tx_hash:
                log_status = LogStatus.SUCCESS
                message = (
                    f'Successfully sent {query.amount_from.Ether} {swap_info.from_token}'
                    f' to {recipient_address}'
                )
            elif not receipt_status and tx_hash:
                log_status = LogStatus.FAILED
                message = f'Failed to sent {query.amount_from.Ether} {swap_info.from_token}'

            account_network = self.client.account_manager.network
            message += (
                f': {account_network.explorer + account_network.TxPath + tx_hash.hex()}'
            )
        except Exception as e:
            exception = str(e)

            log_status = LogStatus.ERROR,
            message = (
                f'Error while sending {query.amount_from.Ether} '
                f'{swap_info.from_token}: {exception}'
            )
            receipt_status = 0

        self.client.account_manager.custom_logger.log_message(
            log_status, message
        )

        wait_time = 20 * receipt_status

        return wait_time

    async def _get_price_from_binance(
        self,
        session: aiohttp.ClientSession,
        first_token: str,
        second_token: str
    ) -> float | None:
        first_token, second_token = first_token.upper(), second_token.upper()
        for _ in range(5):
            try:
                response = await session.get(
                    f'https://api.binance.com/api/v3/ticker/price?symbol={first_token}{second_token}')
                if response.status != 200:
                    return None
                result_dict = await response.json()
                if 'price' in result_dict:
                    return float(result_dict['price'])
            except Exception as e:
                await asyncio.sleep(3)
        raise ValueError(
            f'Can not get {first_token}{second_token} price from Binance')

    async def perform_tx(
        self,
        tx_params: TxParams | dict
    ) -> tuple[_Hash32, TxReceipt]:
        """
        Perform a token swap operation.

        Args:
            swap_info (SwapInfo): Information about the swap.
            tx_params (TxParams | dict): Transaction parameters.

        Returns:
            tuple[_Hash32, TxReceipt].
            - A tuple containing:
                - The hash of the transaction.
                - The receipt of the transaction.
        """
        tx = await self.client.contract.transaction.sign_and_send(
            tx_params=tx_params
        )
        receipt = await tx.wait_for_tx_receipt(
            web3=self.client.account_manager.w3
        )

        return tx.hash, receipt
