from web3 import Web3
from web3.eth import AsyncEth
from web3.contract import Contract, AsyncContract
from web3.types import (
    TxParams,
    _Hash32,
)
from eth_typing import ChecksumAddress

from min_library.models.account.account_manager import AccountManager
from min_library.models.contracts.raw_contract import TokenContract
from min_library.models.networks.network import Network
from min_library.models.others.dataclasses import CommonValues, DefaultAbis
from min_library.models.others.params_types import ParamsTypes
from min_library.models.others.token_amount import TokenAmount
from min_library.models.transactions.transaction import Transaction
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
            tuple[ChecksumAddress, list | None]: 
                The checksummed contract address and ABI (optional).
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
        Approve spending of a certain amount of tokens to a specified spender.

        Args:
            token_contract (ParamsTypes.TokenContract | ParamsTypes.Contract | ParamsTypes.Address): 
                The token contract or address to approve spending for.
            spender_address (ParamsTypes.Address): 
                The address of the spender.
            amount (ParamsTypes.Amount | None, optional): 
                The amount of tokens to approve. If None, approve the full balance. Defaults to None.
            tx_params (TxParams | dict | None, optional): 
                Additional transaction parameters. Defaults to None.
            is_approve_infinity (bool, optional): 
                Whether to approve an infinite amount. Defaults to False.

        Returns:
            Union[str, bool]: 
                If successful, returns the transaction hash. If not, returns False.
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

        approve_tx_params = {}
        if tx_params:
            approve_tx_params = self.get_custom_settings_for_tx_params(tx_params)

        approve_tx_params.update({
            'to': token_contract.address,
            'data': data
        })

        tx = await self.transaction.sign_and_send(approve_tx_params)
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

        """
        if type(token) in ParamsTypes.Address.__args__:
            address = Web3.to_checksum_address(token)
            abi = DefaultAbis.Token
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
        if not owner:
            owner = self.account_manager.account.address

        token_contract = await self.get_token_contract(token=token_contract)
        decimals = await self.get_decimals(token_contract=token_contract)

        amount = await token_contract.functions.allowance(
            owner,
            Web3.to_checksum_address(spender_address),
        ).call()

        return TokenAmount(amount, decimals, wei=True)

    async def get_balance(
        self,
        token_contract: ParamsTypes.TokenContract | ParamsTypes.Contract
            | ParamsTypes.Address = None,
        address: ParamsTypes.Address | None = None
    ) -> TokenAmount:
        """
        Get the balance of an EVM-compatible address.

        Args:
            token_contract (ParamsTypes.TokenContract | ParamsTypes.Contract | ParamsTypes.Address, optional):
                The token contract, contract address, or None for native balance. Defaults to None.
            address (ParamsTypes.Address, optional): 
                The Ethereum address for which to retrieve the balance. Defaults to None.

        Returns:
            TokenAmount: 
                An object representing the token balance, including the amount and decimals.

        Note:
            If `token_contract` is provided, it retrieves the token balance.
            If `token_contract` is None, it retrieves the native balance.
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
        token_contract: ParamsTypes.TokenContract | ParamsTypes.Contract,
        network: Network | None = None
    ) -> int:
        """
        Get the number of decimals for the given token contract.

        Args:
            token_contract (ParamsTypes.TokenContract | ParamsTypes.Contract): 
                The token contract instance or address.
            network (Network, optional): 
                The network on which the contract is deployed. Defaults to None.

        Returns:
            int: 
                The number of decimals for the token contract.
        """
        if not network:
            w3 = self.account_manager.w3

        else:
            w3 = Web3(
                Web3.AsyncHTTPProvider(
                    endpoint_uri=network.rpc,
                    request_kwargs={
                        'proxy': self.account_manager.proxy,
                        'headers': self.account_manager.headers
                    }
                ),
                modules={'eth': (AsyncEth,)},
                middlewares=[]
            )

        if type(token_contract) in ParamsTypes.TokenContract.__args__:
            if not token_contract.decimals:
                contract = w3.eth.contract(
                    address=token_contract.address,
                    abi=token_contract.abi
                )
                token_contract.decimals = await contract.functions.decimals().call()
            decimals = token_contract.decimals
        else:
            decimals = await token_contract.functions.decimals().call()

        return decimals

    async def transfer(
        self,
        recipient_address: str,
        token_amount: TokenAmount,
        token_contract: TokenContract | None = None,
        tx_params: TxParams | dict | None = None
    ) -> tuple[bool, _Hash32]:
        """
        Transfer tokens to a recipient address.

        Args:
            recipient_address (str): 
                The address of the recipient.
            token_amount (TokenAmount): 
                The amount of tokens to transfer.
            token_contract (TokenContract | None, optional): 
                The token contract instance. Defaults to None.
            tx_params (TxParams | dict | None, optional): 
                Additional transaction parameters. Defaults to None.

        Returns:
            tuple[bool, _Hash32]: 
                A tuple containing a boolean indicating the success status of the transfer and the transaction hash.
        """
        contract = await self.get_token_contract(token_contract)

        if token_contract.is_native_token:
            new_tx_params = TxParams(
                to=Web3.to_checksum_address(recipient_address),
                value=token_amount.Wei
            )

        else:
            new_tx_params = TxParams(
                to=contract.address,
                data=contract.encodeABI(
                    fn_name='transfer',
                    args=[
                        Web3.to_checksum_address(recipient_address),
                        token_amount.Wei
                    ]
                ),
                value=0
            )

        if tx_params:
            for key in tx_params.keys():
                new_tx_params[key] = tx_params[key]

        tx = await self.transaction.sign_and_send(new_tx_params)
        receipt = await tx.wait_for_tx_receipt(
            web3=self.account_manager.w3
        )

        return receipt['status'], tx.hash

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

    def get_custom_settings_for_tx_params(
        self,
        tx_params: dict
    ) -> dict:
        new_tx_params = {}

        values_for_custom_setup = [
            'gasPrice',
            'multiplier',
            'maxPriorityFeePerGas',
        ]

        for value in values_for_custom_setup:
            new_tx_params[value] = tx_params[value]

        return new_tx_params
