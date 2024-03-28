import random

from web3 import Web3
from web3.eth import AsyncEth
from web3.types import TxParams

from min_library.models.bridges.bridge_data import TokenBridgeInfo
from min_library.models.contracts.contracts import TokenContractData
from min_library.models.networks.networks import Networks
from min_library.models.others.constants import LogStatus
from min_library.models.others.token_amount import TokenAmount
from min_library.models.swap.swap_info import SwapInfo
from min_library.models.swap.swap_query import SwapQuery
from min_library.models.transactions.tx_args import TxArgs
from min_library.utils.helpers import sleep
from tasks.swap_task import SwapTask
from tasks.coredao.coredao_data import CoredaoData


class CoreDaoBridge(SwapTask):
    TO_CORE_NETWORKS = [
        Networks.Arbitrum,
        Networks.Avalanche,
        Networks.BSC,
        Networks.Polygon,
    ]

    async def bridge(
        self,
        swap_info: SwapInfo
    ) -> str:
        account_network = self.client.account_manager.network.name
        swap_info.slippage = 0

        check_message = self.validate_swap_inputs(
            first_arg=account_network,
            second_arg=swap_info.to_network.name,
            param_type='networks'
        )
        if check_message:
            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.ERROR, message=check_message
            )

            return False
        
        try:
            src_bridge_data = CoredaoData.get_token_bridge_info(
                network_name=account_network,
                token_symbol=swap_info.from_token
            )

            swap_query = await self.compute_source_token_amount(
                swap_info=swap_info
            )
            swap_query.min_to_amount = TokenAmount(
                amount=swap_query.amount_from.Wei * (1 - swap_info.slippage / 100),
                decimals=swap_query.from_token.decimals,
                wei=True
            ) # check here

            prepared_tx_params = await self._prepare_params(
                src_bridge_data, swap_query, swap_info
            )

            if not prepared_tx_params['value']:
                message = f'Can not get value for ({account_network.upper()})'

                self.client.account_manager.custom_logger.log_message(
                    status=LogStatus.ERROR, message=message
                )

                return False

            native_balance = await self.client.contract.get_balance()
            value = TokenAmount(
                amount=prepared_tx_params['value'],
                decimals=self.client.account_manager.network.decimals,
                wei=True
            )

            if native_balance.Wei < value.Wei:
                message = (
                    f'Too low balance: balance - {round(native_balance.Ether, 2)};'
                    f' fee - {round(value.Ether, 2)}'
                )

                self.client.account_manager.custom_logger.log_message(
                    status=LogStatus.ERROR, message=message
                )

                return False

            swap_info = self.set_custom_gas_price(swap_info)

            if not swap_query.from_token.is_native_token:
                hexed_tx_hash = await self.approve_interface(
                    token_contract=swap_query.from_token,
                    spender_address=prepared_tx_params['to'],
                    amount=swap_query.amount_from,
                    swap_info=swap_info,
                    tx_params=prepared_tx_params
                )

                if hexed_tx_hash:
                    self.client.account_manager.custom_logger.log_message(
                        LogStatus.APPROVED,
                        message=f"{swap_query.from_token.title} {swap_query.amount_from.Ether}"
                    )
                    await sleep(20, 50)
            else:
                prepared_tx_params['value'] += swap_query.amount_from.Wei

            receipt_status = 0
            
            receipt_status, log_status, log_message = await self.perform_bridge(
                swap_info, swap_query, prepared_tx_params,
                external_explorer='https://layerzeroscan.com'
            )
            self.client.account_manager.custom_logger.log_message(
                status=log_status, message=log_message
            )
            
            wait_time = await self.get_wait_time()

            return wait_time if receipt_status else False
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

    def set_custom_gas_price(self, swap_info: SwapInfo):
        match self.client.account_manager.network.name:
            case Networks.BSC.name:
                swap_info.gas_price = 1

        return swap_info

    async def get_wait_time(self) -> int:
        match self.client.account_manager.network.name:
            case Networks.Arbitrum.name:
                wait_time = (1.6 * 60, 2.3 * 60)
            case Networks.Avalanche.name:
                wait_time = (2 * 60, 2.5 * 60)
            case Networks.BSC.name:
                wait_time = (2 * 60, 2.5 * 60)
            case Networks.Core.name:
                wait_time = (2 * 60, 3 * 60)
            case Networks.Polygon.name:
                wait_time = (22 * 60, 24 * 60)

        if self.client.account_manager.network in self.TO_CORE_NETWORKS:
            w3 = self.client.contract.get_web3_with_network(
                network=self.client.account_manager.network
            )

            balance = await w3.eth.get_balance(
                account=self.client.account_manager.account.address
            )

            if not balance:
                waiting_for_native_time = (4 * 60, 6 * 60)

                self.client.account_manager.custom_logger.log_message(
                    status=LogStatus.INFO,
                    message=(
                        f'Waiting for {waiting_for_native_time} secs to get some CORE '
                        f'from {__class__.__name__} for any next operations'
                    )
                )
                wait_time = (
                    waiting_for_native_time
                    if waiting_for_native_time > wait_time
                    else wait_time
                )

        return random.randint(int(wait_time[0]), int(wait_time[1]))

    async def _prepare_params(
        self,
        src_bridge_data: TokenBridgeInfo,
        swap_query: SwapQuery,
        swap_info: SwapInfo,
    ) -> TxParams:
        contract = await self.client.contract.get(
            contract=src_bridge_data.bridge_contract
        )

        if self.client.account_manager.network in self.TO_CORE_NETWORKS:
            callParams = TxArgs(
                refundAddress=self.client.account_manager.account.address,
                zroPaymentAddress=TokenContractData.ZERO_ADDRESS
            )

            args = TxArgs(
                token=swap_query.from_token.address,
                amountLd=swap_query.amount_from.Wei,
                to=self.client.account_manager.account.address,
                callParams=callParams.get_tuple(),
                adapterParams='0x'
            )

            result = await contract.functions.estimateBridgeFee(
                False,
                '0x'
            ).call()

            fee = TokenAmount(
                amount=result[0],
                decimals=self.client.account_manager.network.decimals,
                wei=True
            )
            multiplier = 1.01

        elif self.client.account_manager.network == Networks.Core:
            callParams = TxArgs(
                refundAddress=self.client.account_manager.account.address,
                zroPaymentAddress=TokenContractData.ZERO_ADDRESS
            )

            chain_id = CoredaoData.get_chain_id(
                network_name=swap_info.to_network.name
            )

            args = TxArgs(
                localToken=swap_query.from_token.address,
                remoteChainId=chain_id,
                amount=swap_query.amount_from.Wei,
                to=self.client.account_manager.account.address,
                unwrapWeth=False,
                callParams=callParams.get_tuple(),
                adapterParams='0x'
            )

            result = await contract.functions.estimateBridgeFee(
                chain_id,
                False,
                '0x'
            ).call()

            fee = TokenAmount(amount=result[0], wei=True)
            multiplier = 1.01

        fee.Wei = int(fee.Wei * multiplier)

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI(
                'bridge',
                args=args.get_tuple()
            ),
            value=fee.Wei
        )

        return tx_params
