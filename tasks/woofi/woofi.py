from web3.types import TxParams

from min_library.models.contracts.contracts import ContractsFactory
from min_library.models.others.constants import LogStatus
from min_library.models.others.params_types import ParamsTypes
from min_library.models.swap.swap_info import SwapInfo
from min_library.models.swap.swap_query import SwapQuery
from min_library.models.transactions.tx_args import TxArgs
from min_library.utils.helpers import sleep
from tasks.swap_task import SwapTask
from tasks.woofi.woofi_contracts import WoofiContracts


class WooFi(SwapTask):
    async def swap(
        self,
        swap_info: SwapInfo
    ) -> str:
        check_message = self.validate_swap_inputs(
            first_arg=self.client.account_manager.network.name,
            second_arg=swap_info.to_network.name,
            param_type='networks'
        )
        if check_message:
            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.ERROR, message=check_message
            )

            return False

        dex_contract = WoofiContracts.get_dex_contract(
            name='WooRouterV2',
            network=self.client.account_manager.network.name
        )

        contract = await self.client.contract.get(contract=dex_contract)
        swap_query = await self.create_swap_query(contract=contract, swap_info=swap_info)

        args = TxArgs(
            fromToken=swap_query.from_token.address,
            toToken=swap_query.to_token.address,
            fromAmount=swap_query.amount_from.Wei,
            minToAmount=swap_query.min_to_amount.Wei,
            to=self.client.account_manager.account.address,
            rebateTo=self.client.account_manager.account.address
        )

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI('swap', args=args.get_tuple()),
        )

        tx_params = self.set_all_gas_params(
            swap_info=swap_info,
            tx_params=tx_params
        )

        if not swap_query.from_token.is_native_token:
            await self.approve_interface(
                token_contract=swap_query.from_token,
                spender_address=contract.address,
                amount=swap_query.amount_from,
                tx_params=tx_params
            )
            await sleep(15, 30)
        else:
            tx_params['value'] = swap_query.amount_from.Wei

        tx = await self.client.contract.transaction.sign_and_send(
            tx_params=tx_params
        )
        receipt = await tx.wait_for_tx_receipt(
            web3=self.client.account_manager.w3
        )

        if receipt:
            account_network = self.client.account_manager.network
            full_path = account_network.explorer + account_network.TxPath
            return (
                f'{swap_query.amount_from.Ether} {swap_query.from_token.title} was swapped to '
                f'{swap_query.min_to_amount.Ether} {swap_query.to_token.title} '
                f'via {dex_contract.title}: '
                f'{full_path + tx.hash.hex()}'
            )

        return (
            f'Failed swap {swap_query.amount_from.Ether} to {swap_query.to_token.title} '
            f'via {dex_contract.title}: '
            f'{full_path + tx.hash.hex()}'
        )

    async def create_swap_query(
        self,
        contract: ParamsTypes.Contract,
        swap_info: SwapInfo
    ) -> SwapQuery:

        swap_query = await self.compute_source_token_amount(swap_info=swap_info)

        to_token = ContractsFactory.get_contract(
            network_name=self.client.account_manager.network.name,
            token_symbol=swap_info.to_token
        )

        min_to_amount = await contract.functions.tryQuerySwap(
            swap_query.from_token.address,
            to_token.address,
            swap_query.amount_from.Wei
        ).call()

        return await self.compute_min_destination_amount(
            swap_query=swap_query,
            min_to_amount=min_to_amount,
            swap_info=swap_info
        )
