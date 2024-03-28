import time

from web3.types import TxParams

from min_library.models.contracts.contracts import ContractsFactory, TokenContractData
from min_library.models.contracts.raw_contract import RawContract
from min_library.models.others.constants import LogStatus
from min_library.models.swap.swap_info import SwapInfo
from min_library.models.swap.swap_query import SwapQuery
from min_library.utils.helpers import read_json, sleep
from tasks.swap_task import SwapTask


class PancakeSwap(SwapTask):
    ROUTER = RawContract(
        title='PancakeSwap: Smart Router V3',
        address='0x13f4EA83D0bd40E75C8222255bc855a974568Dd4',
        abi=read_json(
            path=('data', 'abis', 'pancake_swap', 'router_abi.json')
        )
    )
    FACTORY = RawContract(
        title='PancakeSwap: Factory V3',
        address='0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865',
        abi=read_json(
            path=('data', 'abis', 'pancake_swap', 'factory_abi.json')
        )
    )
    QUOTER = RawContract(
        title='PancakeSwap: Quoter V2',
        address='0xB048Bbc1Ee6b733FFfCFb9e9CeF7375518e25997',
        abi=read_json(
            path=('data', 'abis', 'pancake_swap', 'quoter_abi.json')
        )
    )

    async def get_pool(
        self,
        swap_query: SwapQuery
    ) -> str:
        factory = await self.client.contract.get(
            contract=self.FACTORY
        )

        pool = await factory.functions.getPool(
            swap_query.from_token.address,
            swap_query.to_token.address,
            500
        ).call()

        return pool

    async def get_quote(
        self,
        swap_query: SwapQuery
    ) -> int:
        quoter = await self.client.contract.get(
            contract=self.QUOTER
        )

        quoter_data = await quoter.functions.quoteExactInputSingle((
            swap_query.from_token.address,
            swap_query.to_token.address,
            swap_query.amount_from.Wei,
            500,
            0
        )).call()

        return quoter_data[0]

    async def swap(
        self,
        swap_info: SwapInfo
    ) -> bool:
        check_message = self.validate_swap_inputs(
            first_arg=swap_info.from_token,
            second_arg=swap_info.to_token,
            param_type='tokens'
        )
        if check_message:
            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.ERROR, message=check_message
            )

            return False
        
        
        swap_query = await self.compute_source_token_amount(swap_info=swap_info)

        swap_query.to_token = ContractsFactory.get_contract(
            network_name=self.client.account_manager.network.name,
            token_symbol=swap_info.to_token
        )

        # pool = await self.get_pool(swap_query=swap_query)
        pool = '0x589a5062e47202bB994cD354913733a14b54e8Dc'
        deadline = int(time.time() + 20 * 60)

        if pool == TokenContractData.ZERO_ADDRESS:
            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.ERROR,
                message=(
                    f'Swap path {swap_info.from_token} '
                    f'to {swap_info.to_token} not found!'
                )
            )

            return False

        swap_contract = await self.client.contract.get(
            contract=self.ROUTER
        )

        quote = await self.get_quote(
            swap_query=swap_query
        )

        tx_data = swap_contract.encodeABI(
            fn_name='exactInputSingle',
            args=[(
                swap_query.from_token.address,
                swap_query.to_token.address,
                300,
                self.client.account_manager.account.address,
                swap_query.amount_from.Wei,
                swap_query.min_to_amount.Wei,
                0
            )]
        )

        contract_data = await swap_contract.functions.multicall(
            deadline, [tx_data]
        )
        
        tx_params = TxParams(
            to=swap_contract.address,
            data=contract_data
        )

        tx_params = self.set_all_gas_params(
            swap_info=swap_info,
            tx_params=tx_params
        )
        
        if not swap_query.from_token.is_native_token:
            await self.approve_interface(
                token_contract=swap_query.from_token,
                spender_address=swap_contract.address,
                amount=swap_query.amount_from,
                tx_params=tx_params
            )
            await sleep(30, 50)
        else:
            tx_params['value'] = swap_query.amount_from.Wei

        try:
            receipt_status, log_status, log_message = await self.perform_swap(
                swap_info, swap_query, tx_params
            )

            self.client.account_manager.custom_logger.log_message(
                status=log_status, message=log_message
            )

            return receipt_status
        except Exception as e:
            error = str(e)
            if 'insufficient funds for gas + value' in error:
                self.client.account_manager.custom_logger.log_message(
                    status=LogStatus.ERROR, message='Insufficient funds for gas + value'
                )
            else:
                self.client.account_manager.custom_logger.log_message(
                    status=LogStatus.ERROR, message=error
                )
        return False
        
        
