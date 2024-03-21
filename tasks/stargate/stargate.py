from typing import Tuple
from web3.types import TxParams

from min_library.models.networks.networks import Networks
from min_library.models.others.constants import LogStatus, TokenSymbol
from min_library.models.others.params_types import ParamsTypes
from min_library.models.others.token_amount import TokenAmount
from min_library.models.swap.swap_info import SwapInfo
from min_library.models.swap.swap_query import SwapQuery
from min_library.models.transactions.tx_args import TxArgs
from min_library.utils.helpers import sleep
from tasks.stargate.stargate_contracts import StargateContracts
from tasks.stargate.stargate_data import StargateData
from tasks.swap_task import SwapTask


class Stargate(SwapTask):
    async def swap(
        self,
        swap_info: SwapInfo,
        max_fee: float = 0.7,
        dst_fee: float | TokenAmount | None = None
    ) -> bool:
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

        from_network = self.client.account_manager.network.name

        src_bridge_data = StargateData.get_token_bridge_info(
            network=from_network,
            token_symbol=swap_info.from_token
        )

        contract = await self.client.contract.get(
            contract=src_bridge_data.bridge_contract
        )

        swap_query = await self.compute_source_token_amount(
            swap_info=swap_info
        )

        if dst_fee and isinstance(dst_fee, float):
            dst_network = Networks.get_network(
                network_name=swap_info.to_network
            )
            dst_fee = TokenAmount(
                amount=dst_fee,
                decimals=dst_network.decimals
            )

        data, value = await self.get_data_for_swap(
            swap_info=swap_info,
            swap_query=swap_query,
            contract=contract,
            src_pool_id=src_bridge_data.pool_id,
            dst_fee=dst_fee
        )

        if not value:
            message = f'Can not get value for ({from_network.upper()})'

            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.ERROR, message=message
            )

            return False

        native_balance = await self.client.contract.get_balance()

        if native_balance.Wei < value.Wei:
            message = f'Too low balance: balance: {native_balance.Ether}; value: {value.Ether}'

            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.ERROR, message=message
            )

            return False

        token_price = await self.get_binance_ticker_price(
            first_token=self.client.account_manager.network.coin_symbol
        )
        network_fee = float(value.Ether) * token_price

        dst_native_amount_price = 0
        if dst_fee:
            dst_token_price = await self.get_binance_ticker_price(
                first_token=dst_network.coin_symbol
            )
            dst_native_amount_price = float(dst_fee.Ether) * dst_token_price

        if network_fee - dst_native_amount_price > max_fee:
            message = (
                f'Too high fee for fee: '
                f'{network_fee - dst_native_amount_price} '
                f'({from_network.upper()})'
            )
            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.WARNING, message=message
            )

        tx_params = TxParams(
            to=contract.address,
            data=data,
            value=int(value.Wei * 1.01)
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

    async def get_data_for_swap(
        self,
        swap_info: SwapInfo,
        swap_query: SwapQuery,
        contract: ParamsTypes.Contract,
        src_pool_id: int | None,
        dst_fee: float | TokenAmount | None = None
    ) -> Tuple[str, TokenAmount]:
        dst_chain_id, dst_pool_id = StargateData.get_chain_id_and_pool_id(
            network=swap_info.to_network,
            token_symbol=swap_info.to_token
        )

        if swap_info.from_token == TokenSymbol.ETH:
            tx_args = TxArgs(
                _dstChainId=dst_chain_id,
                _refundAddress=self.client.account_manager.account.address,
                _toAddress=self.client.account_manager.account.address,
                _amountLD=swap_query.amount_from.Wei,
                _minAmountLd=int(swap_query.amount_from.Wei *
                                 (100 - swap_info.slippage) / 100),
            )

            data = contract.encodeABI('swapETH', args=tx_args.get_tuple())

        elif swap_info.from_token == TokenSymbol.USDV:
            address = self.client.account_manager.account.address
            swap_query = await self.compute_min_destination_amount(
                swap_query=swap_query,
                min_to_amount=1,
                swap_info=swap_info
            )

            tx_args = TxArgs(
                _swapParam=TxArgs(
                    _fromToken=swap_query.from_token.address,
                    _fromTokenAmount=swap_query.amount_from.Wei,
                    _minUSDVOut=swap_query.min_to_amount.Wei
                ).get_tuple(),
                _param=TxArgs(
                    to=self.to_cut_hex_prefix_and_zfill(address),
                    amountLD=swap_query.from_token.address,
                    minAmountLD=swap_query.amount_from.Wei,
                    dstEid=dst_chain_id
                ).get_tuple(),
                _msgFee=TxArgs(
                    nativeFee="",
                    lzTokenFee="",
                ).get_tuple(),
                _refundAddress=address,
                _composeMsg='0x'
            ).get_tuple()

            data = contract.encodeABI('swapRecolorSend', args=tx_args)

            value = await self._quote_send_fee(
                router_contract=contract,
                swap_query=swap_query,    
                dst_chain_id=dst_chain_id,
                adapter_params=adapter_params        
            )            

        elif swap_info.from_token == TokenSymbol.STG:
            adapter_params = '0x00010000000000000000000000000000000000000000000000000000000000014c08'

            tx_args = TxArgs(
                _dstChainId=dst_chain_id,
                _to=self.client.account_manager.account.address,
                _qty=swap_query.amount_from.Wei,
                zroPaymentAddress='0x0000000000000000000000000000000000000000',
                adapterParam=adapter_params
            )

            data = contract.encodeABI('sendTokens', args=tx_args.get_tuple())

            value = await self._estimate_send_tokens_fee(
                stg_contract=contract,
                dst_chain_id=dst_chain_id,
                adapter_params=adapter_params
            )
            return data, value

        else:
            lz_tx_params = TxArgs(
                dstGasForCall=0,
                dstNativeAmount=dst_fee.Wei if dst_fee else 0,
                dstNativeAddr=(
                    self.client.account_manager.account.address
                    if dst_fee
                    else '0x0000000000000000000000000000000000000000'
                )
            )

            tx_args = TxArgs(
                _dstChainId=dst_chain_id,
                _srcPoolId=src_pool_id,
                _dstPoolId=dst_pool_id,
                _refundAddress=self.client.account_manager.account.address,
                _amountLD=swap_query.amount_from.Wei,
                _minAmountLd=int(swap_query.amount_from.Wei *
                                 (100 - swap_info.slippage) / 100),
                _lzTxParams=lz_tx_params.get_tuple(),
                _to=self.client.account_manager.account.address,
                _payload='0x'
            )

            data = contract.encodeABI('swap', args=tx_args.get_tuple())

        value = await self._quote_layer_zero_fee(
            router_contract=contract,
            dst_chain_id=dst_chain_id,
            lz_tx_params=lz_tx_params,
            src_token_symbol=swap_info.from_token,
        )

        return data, value

    async def _estimate_send_tokens_fee(
        self,
        stg_contract: ParamsTypes.Contract,
        dst_chain_id: int,
        adapter_params: str,
    ) -> TokenAmount:
        result = await stg_contract.functions.estimateSendTokensFee(
            dst_chain_id,
            False,
            adapter_params
        ).call()

        return TokenAmount(amount=result[0], wei=True)

    async def _quote_layer_zero_fee(
        self,
        router_contract: ParamsTypes.Contract,
        dst_chain_id: int,
        lz_tx_params: TxArgs,
        src_token_symbol: str | None = None
    ) -> TokenAmount:
        if src_token_symbol and src_token_symbol.upper() == TokenSymbol.ETH:
            network = self.client.account_manager.network.name

            network_data = StargateData.get_network_data(network=network)

            router = None
            for key, value in network_data.bridge_dict.items():
                if key != TokenSymbol.ETH:
                    router = value.bridge_contract
                    break
            if not router:
                router_eth_address = (
                    await router_contract.functions.stargateRouter().call()
                )
                router = await self.client.contract.get(
                    contract=router_eth_address,
                    abi=StargateContracts.STARGATE_ROUTER_ETH_ABI
                )

        result = await router_contract.functions.quoteLayerZeroFee(
            dst_chain_id,
            1,
            self.client.account_manager.account.address,
            '0x',
            lz_tx_params.get_list()
        ).call()

        return TokenAmount(amount=result[0], wei=True)

    async def _quote_send_fee(
        self,
        router_contract: ParamsTypes.Contract,
        swap_query: SwapQuery,
        dst_chain_id: int,
        adapter_params: str,
        use_lz_token: bool = False,
    ) -> TokenAmount:
        result = await router_contract.functions.quoteSendFee(
            [
                self.to_cut_hex_prefix_and_zfill(
                    self.client.account_manager.account.address
                ),
                swap_query.amount_from.Wei,
                swap_query.min_to_amount.Wei,
                dst_chain_id
            ],
            adapter_params,
            False,
            "0x"
        ).call()

        return TokenAmount(amount=result[0], wei=True)
