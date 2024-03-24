import random
import time

from typing import List
from web3.types import TxParams
import web3.exceptions as web3_exceptions

from min_library.models.contracts.contracts import CoreTokenContracts
from min_library.models.contracts.raw_contract import RawContract
from min_library.models.networks.networks import Networks
from min_library.models.others.constants import LogStatus, TokenSymbol
from min_library.models.others.params_types import ParamsTypes
from min_library.models.swap.swap_info import SwapInfo
from min_library.models.swap.swap_query import SwapQuery
from min_library.models.swap.tx_payload_details import TxPayloadDetails
from min_library.models.swap.tx_payload_details_fetcher import TxPayloadDetailsFetcher
from min_library.models.transactions.tx_args import TxArgs
from min_library.utils.helpers import read_json, sleep
from tasks.swap_task import SwapTask


class ShadowSwap(SwapTask):
    contracts_dict = {
        'ShadowRouter': RawContract(
            title='ShadowRouter (CORE)',
            address='0xCCED48E6fe655E5F28e8C4e56514276ba8b34C09',
            abi=read_json(
                path=('data', 'abis', 'shadow_swap', 'shadow_router_abi.json')
            )
        )
    }

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

        contract = await self.client.contract.get(
            contract=self.contracts_dict['ShadowRouter']
        )
        tx_payload_details = ShadowSwapRoutes.get_tx_payload_details(
            first_token=swap_info.from_token,
            second_token=swap_info.to_token
        )
        
        swap_query = await self._create_swap_query(
            contract=contract,
            swap_info=swap_info,
            swap_path=tx_payload_details.swap_path
        )


        params = TxArgs(
            amountOutMin=swap_query.min_to_amount.Wei,
            path=tx_payload_details.swap_path,
            to=self.client.account_manager.account.address,
            deadline=int(time.time() + 20 * 60)
        )

        list_params = params.get_list()

        if (
            swap_info.from_token != TokenSymbol.CORE
        ):
            list_params.insert(0, swap_query.amount_from.Wei)

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI(
                tx_payload_details.method_name,
                args=tuple(list_params)
            )
        )

        if not swap_query.from_token.is_native_token:
            hexed_tx_hash = await self.approve_interface(
                token_contract=swap_query.from_token,
                spender_address=contract.address,
                amount=swap_query.amount_from,
                swap_info=swap_info,
                tx_params=tx_params
            )

            if hexed_tx_hash:
                self.client.account_manager.custom_logger.log_message(
                    LogStatus.APPROVED,
                    message=f"{swap_query.from_token.title} {swap_query.amount_from.Ether}"
                )
                await sleep(8, 15)
        else:
            tx_params['value'] = swap_query.amount_from.Wei
        try:
            receipt_status, status, message = await self.perform_swap(
                swap_info, swap_query, tx_params
            )

            self.client.account_manager.custom_logger.log_message(
                status=status, message=message
            )
        except web3_exceptions.ContractCustomError as e:
            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.ERROR, message='Try to make slippage more'
            )
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

        wait_time = self.get_wait_time()

        return wait_time if receipt_status else False

    def get_wait_time(self) -> int:
        match self.client.account_manager.network.name:
            case Networks.Core.name:
                wait_time = (0.4 * 60, 1 * 60)

        return random.randint(int(wait_time[0]), int(wait_time[1]))

    async def _create_swap_query(
        self,
        contract: ParamsTypes.Contract,
        swap_info: SwapInfo,
        swap_path: List[str]
    ) -> SwapQuery:
        swap_query = await self.compute_source_token_amount(swap_info=swap_info)
        
        amounts_out = await contract.functions.getAmountsOut(
            swap_query.amount_from.Wei,
            swap_path
        ).call()

        return await self.compute_min_destination_amount(
            swap_query=swap_query,
            min_to_amount=amounts_out[1],
            swap_info=swap_info,
            is_to_token_price_wei=True
        )


class ShadowSwapRoutes(TxPayloadDetailsFetcher):
    PATHS = {
        TokenSymbol.CORE: {
            TokenSymbol.USDT: TxPayloadDetails(
                method_name='swapExactETHForTokens',
                addresses=[
                    CoreTokenContracts.WCORE.address,
                    CoreTokenContracts.USDT.address,
                ]
            ),
        },
        TokenSymbol.USDT: {
            TokenSymbol.CORE: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    CoreTokenContracts.USDT.address,
                    CoreTokenContracts.WCORE.address
                ]
            ),
        }
    }
