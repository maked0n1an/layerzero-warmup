from typing import (
    Any,
    Callable
)

from min_library.models.account.account_manager import AccountInfo
from min_library.models.client import Client
from min_library.models.logger.logger import console_logger
from min_library.models.networks.networks import Networks
from min_library.models.others.constants import LogStatus, TokenSymbol
from min_library.models.swap.swap_info import SwapInfo
from min_library.utils.helpers import delay
from tasks.pancake_swap.pancake_swap import PancakeSwap
from tasks.shadow_swap.shadow_swap import ShadowSwap
from tasks.coredao.coredao import CoreDaoBridge
from tasks.stargate.stargate import Stargate
from tasks.testnet_bridge.testnet_bridge import TestnetBridge
from user_data.settings.settings import (
    IS_SLEEP
)

ModuleType = Callable[..., Any]
ActionType = Callable[[Any, SwapInfo], Any]


async def _default_settings(
    module: ModuleType,
    action: ActionType,
    account_info: AccountInfo,
    module_info: SwapInfo,
    swap_info: SwapInfo,
) -> int:
    client = Client(
        account_id=account_info.account_id,
        private_key=account_info.private_key,
        proxy=account_info.proxy,
        network=(
            module_info.from_network
            if module_info
            else swap_info.from_network
        )
    )

    module_instance = module(client=client)

    if module_info:
        swap_info = module_info

    client.account_manager.custom_logger.log_message(
        LogStatus.INFO, f'Started {module.__name__}'
    )

    wait_time = await action(module_instance, swap_info)
    return wait_time


async def bridge_stargate(
    account_info: AccountInfo,
    module_info: SwapInfo | None = None
) -> int:
    swap_info = SwapInfo(
        from_network=Networks.BSC,
        to_network=Networks.Polygon,
        from_token=TokenSymbol.USDT,
        to_token=TokenSymbol.USDC_E,
        slippage=0.1
    )

    stargate_instance = Stargate

    return await _default_settings(
        module=stargate_instance,
        action=stargate_instance.crosschain_swap,
        account_info=account_info,
        module_info=module_info,
        swap_info=swap_info
    )


async def bridge_coredao(
    account_info: AccountInfo,
    module_info: SwapInfo | None = None
) -> int:
    swap_info = SwapInfo(
        from_network=Networks.Core,
        to_network=Networks.BSC,
        from_token=TokenSymbol.USDT,
        to_token=TokenSymbol.USDT,
    )

    coredao_instance = CoreDaoBridge

    return await _default_settings(
        module=coredao_instance,
        action=coredao_instance.bridge,
        account_info=account_info,
        module_info=module_info,
        swap_info=swap_info
    )


async def bridge_testnet_bridge(
    account_info: AccountInfo,
    module_info: SwapInfo | None = None
) -> int:
    swap_info = SwapInfo(
        from_token=TokenSymbol.USDT,
        to_token=TokenSymbol.USDT,
        to_network=Networks.Polygon,
        from_network=Networks.Goerli
    )

    testnetbridge_instance = TestnetBridge

    return await _default_settings(
        module=testnetbridge_instance,
        action=testnetbridge_instance.bridge,
        account_info=account_info,
        module_info=module_info,
        swap_info=swap_info
    )


async def swap_pancake(
    account_info: AccountInfo,
    module_info: SwapInfo | None = None
) -> int:
    swap_info = SwapInfo(
        from_token=TokenSymbol.USDT,
        to_token=TokenSymbol.USDT,
        from_network=Networks.Polygon,
        to_network=Networks.Polygon
    )

    pancakeswap_instance = PancakeSwap

    return await _default_settings(
        module=pancakeswap_instance,
        action=pancakeswap_instance.swap,
        account_info=account_info,
        module_info=module_info,
        swap_info=swap_info
    )


async def swap_shadowswap(
    account_info: AccountInfo,
    module_info: SwapInfo | None = None
) -> int:
    swap_info = SwapInfo(
        from_network=Networks.Core,
        from_token=TokenSymbol.USDT,
        to_token=TokenSymbol.CORE,
        amount_from=0.9,
        amount_to=1.0
    )

    shadowswap_instance = ShadowSwap

    return await _default_settings(
        module=shadowswap_instance,
        action=shadowswap_instance.swap,
        account_info=account_info,
        module_info=module_info,
        swap_info=swap_info
    )


async def custom_routes(account_info: AccountInfo):    
    CLASSIC_ROUTES_MODULES_USING = [    
        # [
        #     bridge_stargate,
        #     SwapInfo(
        #         from_network=Networks.Polygon,
        #         to_network=Networks.BSC,
        #         from_token=TokenSymbol.USDT,
        #         to_token=TokenSymbol.USDT,
        #         slippage=0.1
        #     )
        # ],
        # [
        #     bridge_coredao,
        #     SwapInfo(
        #         from_network=Networks.BSC,
        #         to_network=Networks.Core,
        #         from_token=TokenSymbol.USDT,
        #         to_token=TokenSymbol.USDT,
        #     )
        # ],
        # [
        #     swap_shadowswap,
        #     SwapInfo(
        #         from_network=Networks.Core,
        #         from_token=TokenSymbol.USDT,
        #         to_token=TokenSymbol.CORE,
        #         amount_from=0.95,
        #         amount_to=1.05
        #     )
        # ],
        # [
        #     bridge_coredao,
        #     SwapInfo(
        #         from_network=Networks.Core,
        #         to_network=Networks.BSC,
        #         from_token=TokenSymbol.USDT,
        #         to_token=TokenSymbol.USDT,
        #     )
        # ],          
        # [
        #     bridge_coredao,
        #     SwapInfo(
        #         from_network=Networks.BSC,
        #         to_network=Networks.Core,
        #         from_token=TokenSymbol.USDT,
        #         to_token=TokenSymbol.USDT,
        #     )
        # ],
        # [
        #     swap_shadowswap,
        #     SwapInfo(
        #         from_network=Networks.Core,
        #         from_token=TokenSymbol.USDT,
        #         to_token=TokenSymbol.CORE,
        #         amount_from=0.9,
        #         amount_to=1.0
        #     )
        # ],
        # [
        #     bridge_coredao,
        #     SwapInfo(
        #         from_network=Networks.Core,
        #         to_network=Networks.BSC,
        #         from_token=TokenSymbol.USDT,
        #         to_token=TokenSymbol.USDT,
        #     )
        # ],        
        # [
        #     bridge_stargate,
        #     SwapInfo(
        #         from_network=Networks.BSC,
        #         to_network=Networks.Polygon,
        #         from_token=TokenSymbol.USDT,
        #         to_token=TokenSymbol.USDC_E,
        #         slippage=0.1
        #     )
        # ],   
        # [
        #     bridge_stargate,
        #     SwapInfo(
        #         from_network=Networks.Polygon,
        #         to_network=Networks.Arbitrum,
        #         from_token=TokenSymbol.USDC_E,
        #         to_token=TokenSymbol.USDV,
        #     )
        # ],   
        # [
        #     bridge_stargate,
        #     SwapInfo(
        #         from_network=Networks.Arbitrum,
        #         to_network=Networks.Optimism,
        #         from_token=TokenSymbol.USDV,
        #         to_token=TokenSymbol.USDV,
        #     )
        # ],      
        # [
        #     bridge_stargate,
        #     SwapInfo(
        #         from_network=Networks.Optimism,
        #         to_network=Networks.Arbitrum,
        #         from_token=TokenSymbol.USDV,
        #         to_token=TokenSymbol.USDV,
        #     )
        # ],      
        # [
        #     bridge_stargate,
        #     SwapInfo(
        #         from_network=Networks.Arbitrum,
        #         to_network=Networks.Avalanche,
        #         from_token=TokenSymbol.USDV,
        #         to_token=TokenSymbol.USDV,
        #     )
        # ],      
        # [
        #     bridge_stargate,
        #     SwapInfo(
        #         from_network=Networks.Avalanche, # OP - ARB (not working), AVAX - BSC (not working)
        #         to_network=Networks.Optimism,
        #         from_token=TokenSymbol.USDV,
        #         to_token=TokenSymbol.USDV,
        #     )
        # ],
        # [
        #     bridge_stargate,
        #     SwapInfo(
        #         from_network=Networks.Optimism,
        #         to_network=Networks.BSC,
        #         from_token=TokenSymbol.USDV,
        #         to_token=TokenSymbol.USDV,
        #     )
        # ],
        # [
        #     bridge_stargate,
        #     SwapInfo(
        #         from_network=Networks.Optimism,
        #         to_network=Networks.Arbitrum,
        #         from_token=TokenSymbol.USDV,
        #         to_token=TokenSymbol.USDV,
        #     )
        # ],
        # [
        #     bridge_stargate,
        #     SwapInfo(
        #         from_network=Networks.Arbitrum,
        #         to_network=Networks.Optimism,
        #         from_token=TokenSymbol.USDV,
        #         to_token=TokenSymbol.USDV,
        #     )
        # ],
        # [
        #     bridge_stargate,
        #     SwapInfo(
        #         from_network=Networks.Optimism,
        #         to_network=Networks.Arbitrum,
        #         from_token=TokenSymbol.USDV,
        #         to_token=TokenSymbol.USDV,
        #     )
        # ],
        # [
        #     bridge_stargate,
        #     SwapInfo(
        #         from_network=Networks.Arbitrum,
        #         to_network=Networks.BSC,
        #         from_token=TokenSymbol.USDV,
        #         to_token=TokenSymbol.USDV,
        #     )
        # ],
        [
            bridge_stargate,
            SwapInfo(
                from_network=Networks.BSC,
                to_network=Networks.Polygon,
                from_token=TokenSymbol.USDT,
                to_token=TokenSymbol.USDT,
                slippage=0.3
            )
        ],
    ]

    async def call_route(step):
        if callable(step[0]):
            return await step[0](account_info, step[1])

    copy_route = CLASSIC_ROUTES_MODULES_USING

    for step in copy_route:
        wait_time = await call_route(step)

        if not wait_time:
            console_logger.warning(msg='Route has been broken, maybe some errors')

        if IS_SLEEP and wait_time and step != copy_route[-1]:
            await delay(
                sleep_time=wait_time,
                message='before next step'
            )
