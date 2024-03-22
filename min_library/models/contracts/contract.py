from web3 import Web3
from web3.contract import Contract, AsyncContract
from web3.types import TxParams
from eth_typing import ChecksumAddress

from min_library.models.account.account_manager import AccountManager
from min_library.models.others.dataclasses import CommonValues, DefaultAbis
from min_library.models.others.params_types import ParamsTypes
from min_library.models.others.token_amount import TokenAmount
from min_library.models.transactions.transaction import Transaction
from min_library.models.transactions.tx import Tx
from min_library.models.transactions.tx_args import TxArgs
from min_library.utils.helpers import make_request


class Contract:
    def __init__(self, account_manager: AccountManager):
        self.account_manager = account_manager
        self.transaction = Transaction(account_manager)

    @staticmethod
    async def get_signature(hex_signature: str) -> list | None:
        """
        Find all matching signatures in the database of https://www.4byte.directory/.

        :param str hex_signature: a signature hash.
        :return list | None: matches found.
        """
        try:
            url = f'https://www.4byte.directory/api/v1/signatures/?hex_signature={hex_signature}'
            response = await make_request(method="GET", url=url)
            results = response['results']
            return [m['text_signature'] for m in sorted(results, key=lambda result: result['created_at'])]
        except:
            return

    @staticmethod
    async def get_contract_attributes(
        contract: ParamsTypes.TokenContract | ParamsTypes.Contract
            | ParamsTypes.Address
    ) -> tuple[ChecksumAddress, list | None]:
        """
        Get the checksummed contract address and ABI.

        Args:
            contract (ParamsTypes.TokenContract | ParamsTypes.Contract | ParamsTypes.Address):
                The contract address or instance.

        Returns:
            tuple[ChecksumAddress, list | None]: The checksummed contract address and ABI.

        """
        abi = None
        address = None
        if type(contract) in ParamsTypes.Address.__args__:
            address = contract
        else:
            address, abi = contract.address, contract.abi

        return Web3.to_checksum_address(address), abi

    async def approve(
        self,
        token_contract: ParamsTypes.TokenContract | ParamsTypes.Contract
            | ParamsTypes.Address,
        spender_address: ParamsTypes.Address,
        amount: ParamsTypes.Amount | None = None,
        tx_params: TxParams | dict | None = None,
        is_approve_infinity: bool = False
    ) -> str | bool:
        """
        Approve a spender to spend a certain amount of tokens on behalf of the user.

        Args:
            token_contract (TokenContract | NativeTokenContract | RawContract | AsyncContract | Contract | str | Address | ChecksumAddress | ENS):
                The token contract, contract instance, or address.
            spender_address (str | Address | ChecksumAddress | ENS): The address of the spender.
            amount (float | int | TokenAmount | None): The amount of tokens to approve (default is None).
            tx_params (TxParams | dict | None): Transaction parameters (default is None).
            is_approve_infinity (bool): If True, approves an infinite amount (default is False).

        Returns:
            Tx: The transaction params object.
        """
        if type(token_contract) in ParamsTypes.Address.__args__:
            token_address, _ = await self.get_contract_attributes(contract=token_contract)
            token_contract = await self.get_token_contract(
                token=token_address
            )

        decimals = await self.get_decimals(token_contract=token_contract)
        token_contract = await self.get_token_contract(token=token_contract)
        spender_address = Web3.to_checksum_address(spender_address)

        if not amount:
            if is_approve_infinity:
                amount = CommonValues.InfinityInt

            else:
                amount = await self.get_balance(token_contract=token_contract)

        elif isinstance(amount, (int, float)):
            token_amount = TokenAmount(amount=amount, decimals=decimals).Wei

        else:
            token_amount = amount.Wei

        data = token_contract.encodeABI(
            'approve',
            args=TxArgs(
                spender=spender_address,
                amount=token_amount
            ).get_tuple())

        if tx_params:
            new_tx_params = {}
            if 'gas' in tx_params:
                new_tx_params['gas'] = tx_params['gas']
            if 'gasPrice' in tx_params:
                new_tx_params['gasPrice'] = tx_params['gasPrice']
            if 'multiplier' in tx_params:
                new_tx_params['multiplier'] = tx_params['multiplier']
            if 'maxPriorityFeePerGas' in tx_params:
                new_tx_params['maxPriorityFeePerGas'] = (
                    tx_params['maxPriorityFeePerGas']
                )

        new_tx_params.update({
            'to': token_contract.address,
            'data': data
        })
        
        tx = await self.transaction.sign_and_send(tx_params=new_tx_params)
        receipt = await tx.wait_for_tx_receipt(
            web3=self.account_manager.w3,
            timeout=240
        )
        
        return tx.hash.hex() if receipt['status'] else False

    async def get(
        self,
        contract: ParamsTypes.Contract,
        abi: list | str | None = None
    ) -> AsyncContract | Contract:
        """
        Get a contract instance.

        Args:
            contract (ParamsTypes.Contract): the contract address or instance.
            abi (list | str | None, optional): the contract ABI

        Returns:
            AsyncContract | Contract: the contract instance.
        """

        contract_address, contract_abi = await self.get_contract_attributes(
            contract=contract
        )

        if not abi and not contract_abi:
            # todo: сделаем подгрузку abi из эксплорера (в том числе через proxy_address)
            raise ValueError("Can not get contract ABI")
        if not abi:
            abi = contract_abi

        contract = self.account_manager.w3.eth.contract(
            address=contract_address, abi=abi
        )

        return contract

    async def get_approved_amount(
        self,
        token_contract: ParamsTypes.Contract | ParamsTypes.Address,
        spender_address: ParamsTypes.Address,
        owner: ParamsTypes.Address | None = None
    ) -> TokenAmount:
        """
        Get the approved amount of tokens for a spender.

        Args:
            token_contract (ParamsTypes.Contract | ParamsTypes.Address): The token contract or address.
            spender_address (ParamsTypes.Address): The address of the spender.
            owner (ParamsTypes.Address | None): The address of the token owner (default is None).

        Returns:
            TokenAmount: The approved amount of tokens.
        """
        spender_address = Web3.to_checksum_address(spender_address)

        if not owner:
            owner = self.account_manager.account.address

        decimals = 0

        if type(token_contract) in ParamsTypes.Address.__args__:
            token_contract = await self.get(contract=token_contract)

        else:
            decimals = await self.get_decimals(token_contract=token_contract)
            token_contract = await self.get_token_contract(token=token_contract)

        amount = await token_contract.functions.allowance(
            owner,
            spender_address,
        ).call()

        return TokenAmount(amount, decimals, wei=True)

    async def get_balance(
        self,
        token_contract: ParamsTypes.TokenContract | ParamsTypes.Contract
            | ParamsTypes.Address | None = None,
        address: ParamsTypes.Address | None = None
    ) -> TokenAmount:
        """
        Get the balance of an Ethereum address.

        Args:
            token_contract (ParamsTypes.TokenContract | ParamsTypes.Contract | ParamsTypes.Address | None):
                The token contract, contract address, or None for ETH balance.
            address (ParamsTypes.Address | None): The Ethereum address for which to retrieve the balance.

        Returns:
            TokenAmount: An object representing the token balance, including the amount and decimals.

        Note:
            If `token_contract` is provided, it retrieves the token balance.
            If `token_contract` is None, it retrieves the ETH balance.
        """
        if not address:
            address = self.account_manager.account.address

        if token_contract:
            decimals = await self.get_decimals(token_contract=token_contract)
            contract = await self.get_token_contract(token=token_contract)

            amount = await contract.functions.balanceOf(address).call()

        else:
            amount = await self.account_manager.w3.eth.get_balance(account=address)
            decimals = self.account_manager.network.decimals

        return TokenAmount(
            amount=amount,
            decimals=decimals,
            wei=True
        )

    async def get_decimals(
        self,
        token_contract: ParamsTypes.TokenContract | ParamsTypes.Contract
    ) -> int:
        """
        Retrieve the decimals of a token contract or contract.

        Parameters:
        - `token_contract` (TokenContract | NativeTokenContract | RawContract | AsyncContract | Contract): 
            The token contract address or contract instance.

        Returns:
        - `int`: The number of decimals for the token.

        Example:
        ```python
        decimals = await client.contract.get_decimals(token_contract='0x123abc...')
        print(decimals)
        # Output: 18
        """

        if type(token_contract) in ParamsTypes.TokenContract.__args__:
            if not token_contract.decimals:
                contract = self.account_manager.w3.eth.contract(
                    address=token_contract.address,
                    abi=token_contract.abi
                )
                token_contract.decimals = await contract.functions.decimals().call()
            decimals = token_contract.decimals
        else:
            decimals = await token_contract.functions.decimals().call()

        return decimals

    def add_multiplier_of_gas(
        self,
        tx_params: TxParams | dict,
        multiplier: float | None = None
    ) -> TxParams | dict:

        tx_params['multiplier'] = multiplier
        return tx_params

    def set_gas_price(
        self,
        gas_price: ParamsTypes.GasPrice,
        tx_params: TxParams | dict,
    ) -> TxParams | dict:
        """
        Set the gas price in the transaction parameters.

        Args:
            gas_price (GWei): The gas price to set.
            tx_params (TxParams | dict): The transaction parameters.

        Returns:
            TxParams | dict: The updated transaction parameters.

        """
        if isinstance(gas_price, float | int):
            gas_price = TokenAmount(
                amount=gas_price,
                decimals=self.account_manager.network.decimals,
                set_gwei=True
            )
        tx_params['gasPrice'] = gas_price.GWei
        return tx_params

    def set_gas_limit(
        self,
        gas_limit: ParamsTypes.GasLimit,
        tx_params: dict | TxParams,
    ) -> dict | TxParams:
        """
        Set the gas limit in the transaction parameters.

        Args:
            gas_limit (int | TokenAmount): The gas limit to set.
            tx_params (dict | TxParams): The transaction parameters.

        Returns:
            dict | TxParams: The updated transaction parameters.

        """
        if isinstance(gas_limit, int):
            gas_limit = TokenAmount(
                amount=gas_limit,
                decimals=self.account_manager.network.decimals,
                wei=True
            )
        tx_params['gas'] = gas_limit.Wei
        return tx_params

    async def get_token_contract(
        self,
        token: ParamsTypes.Contract | ParamsTypes.Address
    ) -> Contract | AsyncContract:
        """
        Get a contract instance for the specified token.

        Args:
            token (RawContract | AsyncContract | Contract | str | Address | ChecksumAddress | ENS): 
            The token contract or its address.

        Returns:
            Contract | AsyncContract: The contract instance.

        Example:
        ```python
        token_contract = await client.contract.get_token_contract(token=my_token)
        print(token_contract)
        # Output: <Contract object at 0x...>
        ```
        """
        if type(token) in ParamsTypes.Address.__args__:
            address = Web3.to_checksum_address(token)
            contract = self.account_manager.w3.eth.contract(
                address=address, abi=DefaultAbis.Token
            )
        else:
            address = Web3.to_checksum_address(token.address)

            if token.abi:
                abi = token.abi

            else:
                abi = DefaultAbis.Token

            contract = self.account_manager.w3.eth.contract(
                address=address, abi=abi
            )

        return contract
