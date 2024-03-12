from web3.types import TxParams
from min_library.models.others.params_types import ParamsTypes
from min_library.models.others.token_amount import TokenAmount

from min_library.models.swap.swap_info import SwapInfo
from min_library.models.transactions.tx_args import TxArgs
from min_library.utils.helpers import sleep
from tasks.base_task import BaseTask
from tasks.coredao.coredao_data import CoredaoData


class CoreDaoBridge(BaseTask):
    async def bridge(
        self,
        swap_info: SwapInfo
    ) -> str:
        check = self.validate_swap_inputs(
            first_arg=self.client.account_manager.network.name,
            second_arg=swap_info.to_network,
            param_type='networks'
        )
        if check:
            return check

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
            zroPaymentAddress='0x0000000000000000000000000000000000000000'
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
            to=src_bridge_data.bridge_contract.address,
            data=contract.encodeABI('bridge', args=args.get_tuple()),
            value=value.Wei
        )

        tx_params = self.set_all_gas_params(
            swap_info=swap_info,
            tx_params=tx_params
        )

        if not swap_query.from_token.is_native_token:
            await self.approve_interface(
                token_contract=swap_query.from_token,
                spender_address=src_bridge_data.bridge_contract.address,
                amount=swap_query.amount_from,
                tx_params=tx_params,
                is_approve_infinity=False
            )
            await sleep(3, 7)
        else:
            tx_params['value'] += swap_query.amount_from.Wei

        tx = await self.client.contract.transaction.sign_and_send(
            tx_params=tx_params
        )
        receipt = await tx.wait_for_tx_receipt(
            web3=self.client.account_manager.w3,
        )

        if receipt:
            return (
                f'{swap_query.amount_from.Ether} {swap_info.from_token} '
                f'was sent from {self.client.account_manager.network.name.upper()} '
                f'to {swap_info.to_network.upper()} via CoreDao: '
                f'https://layerzeroscan.com/tx/{tx.hash.hex()} '
            )

    async def _get_estimateBridgeFee(
        self,
        contract: ParamsTypes.Contract
    ) -> TokenAmount:
        result = await contract.functions.estimateBridgeFee(
            False,
            '0x'
        ).call()

        return TokenAmount(amount=result[0], wei=True)
