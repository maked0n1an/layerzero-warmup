from web3.types import TxParams
from min_library.models.contracts.contracts import TokenContractData
from min_library.models.others.constants import LogStatus
from min_library.models.others.params_types import ParamsTypes
from min_library.models.others.token_amount import TokenAmount

from min_library.models.swap.swap_info import SwapInfo
from min_library.models.transactions.tx_args import TxArgs
from min_library.utils.helpers import sleep
from tasks.swap_task import SwapTask
from tasks.coredao.coredao_data import CoredaoData


class CoreDaoBridge(SwapTask):
    async def bridge(
        self,
        swap_info: SwapInfo
    ) -> str:
        check_message = self.validate_swap_inputs(
            first_arg=self.client.account_manager.network.name,
            second_arg=swap_info.to_network,
            param_type='networks'
        )
        if check_message:
            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.ERROR, message=check_message
            )

            return False

        src_bridge_data = CoredaoData.get_token_bridge_info(
            network=self.client.account_manager.network.name,
            token_symbol=swap_info.from_token
        )
        contract = await self.client.contract.get(
            contract=src_bridge_data.bridge_contract
        )

        swap_query = await self.compute_source_token_amount(
            swap_info=swap_info
        )

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

        value = await self._get_estimateBridgeFee(contract=contract)

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI('bridge', args=args.get_tuple()),
            value=value.Wei
        )

        tx_params = self.set_all_gas_params(
            swap_info=swap_info,
            tx_params=tx_params
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
                await sleep(20, 50)
        else:
            tx_params['value'] = swap_query.amount_from.Wei

        receipt_status, log_status, log_message = await self.perform_bridge(
            swap_info, swap_query, tx_params, 
            external_explorer='https://layerzeroscan.com'
        ) 

        self.client.account_manager.custom_logger.log_message(
            status=log_status, message=log_message
        )

        return receipt_status

    async def _get_estimateBridgeFee(
        self,
        contract: ParamsTypes.Contract
    ) -> TokenAmount:
        result = await contract.functions.estimateBridgeFee(
            False,
            '0x'
        ).call()

        return TokenAmount(amount=result[0], wei=True)
