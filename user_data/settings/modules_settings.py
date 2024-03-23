from min_library.models.account.account_manager import AccountInfo
from min_library.models.client import Client
from min_library.models.networks.networks import Networks
from min_library.models.others.constants import LogStatus, TokenSymbol
from min_library.models.swap.swap_info import SwapInfo
from tasks.pancake_swap.pancake_swap import PancakeSwap
from user_data.settings.settings import (
    IS_SLEEP
)
from tasks.coredao.coredao import CoreDaoBridge
from tasks.stargate.stargate import Stargate
from tasks.testnet_bridge.testnet_bridge import TestnetBridge


async def bridge_stargate(
    account_info: AccountInfo,
    module_info: SwapInfo | None = None
) -> int:
    swap_info = SwapInfo(
        from_token=TokenSymbol.USDT,
        to_token=TokenSymbol.USDT,
        to_network=Networks.Polygon
    )

    client = Client(
        account_id=account_info.account_id if account_info else "",
        private_key=account_info.private_key if account_info else "",
        proxy=account_info.proxy if account_info else "",
        network=module_info.from_network if module_info else Networks.BSC
    )

    stargate = Stargate(client=client)

    if module_info:
        swap_info = SwapInfo(
            from_token=module_info.from_token,
            to_token=module_info.to_token,
            to_network=module_info.to_network
        )

    client.account_manager.custom_logger.log_message(
        LogStatus.INFO, f'Started Stargate'
    )

    wait_time = await stargate.crosschain_swap(swap_info)
    return wait_time

    swap_info = SwapInfo(
        from_token=TokenSymbol.USDT,
        to_token=TokenSymbol.USDT,
        to_network=Networks.Polygon.name,
    )
    match swap_info.from_network:
        case Networks.BSC.name:
            swap_info.gas_price = 2.5
        case Networks.Opbnb.name:
            swap_info.gas_price = 0.00002
    
    client.account_manager.custom_logger.log_message(
        LogStatus.INFO, f'Started Stargate({"?"})'
    )
    return await stargate.swap(swap_info)


async def bridge_coredao(account_id, private_key) -> bool:
    client = Client(
        account_id=account_id,
        private_key=private_key,
        network="?",
    )
    coredao = CoreDaoBridge(client=client)
    swap_info = SwapInfo(
        from_token="?",
        to_token="?",
        to_network="?",
    )
    client.account_manager.custom_logger.log_message(
        LogStatus.INFO, f'Started CoredaoBridge({"?"})'
    )
    return await coredao.bridge(swap_info)


async def bridge_testnet_bridge(account_id, private_key) -> bool:
    client = Client(
        account_id=account_id,
        private_key=private_key,
        network="?",
    )
    testnet_bridge = TestnetBridge(client=client)
    swap_info = SwapInfo(
        from_token="?",
        to_token="?",
        to_network="?",
    )
    client.account_manager.custom_logger.log_message(
        LogStatus.INFO, f'Started TestnetBridge({"?"})'
    )
    return await testnet_bridge.bridge(swap_info)


async def custom_routes(account_id, private_key):
    CLASSIC_ROUTES_MODULES_USING = [
        [
            bridge_stargate,
            (Networks.Avalanche, TokenSymbol.AVAX),
            (Networks.Avalanche, TokenSymbol.USDC_E)
        ],
        [
            bridge_stargate,
            (Networks.Polygon, TokenSymbol.USDC_E),
            (Networks.BSC, TokenSymbol.USDT)
        ],
        [
            bridge_stargate,
            (Networks.BSC, TokenSymbol.USDT),
            (Networks.Core, TokenSymbol.USDT)
        ],
        [
            bridge_coredao,
            (Networks.Core, TokenSymbol.USDT),
            (Networks.BSC, TokenSymbol.USDT)
        ],
        [
            'sushiswap_swap',
            (Networks.BSC, TokenSymbol.USDT),
            (Networks.BSC, TokenSymbol.USDC)
        ],
        [
            bridge_coredao,
            (Networks.BSC, TokenSymbol.USDC),
            (Networks.Core, TokenSymbol.USDC)
        ],
        [
            bridge_coredao,
            (Networks.Core, TokenSymbol.USDC),
            (Networks.BSC, TokenSymbol.USDC)
        ],
        [
            'bridge_stargate',
            (Networks.BSC, TokenSymbol.USDT),
            (Networks.BSC, TokenSymbol.USDT)
        ],
        [
            'bridge_stargate',
            (Networks.Core, TokenSymbol.USDT),
            (Networks.BSC, TokenSymbol.USDT)
        ],
    ]

    async def call_route(route):
        if callable(route[0]):
            return await route[0](*route[1:])

    client = Client(
        account_id=account_id,
        private_key=private_key,
        proxy=None
    )

    for route in CLASSIC_ROUTES_MODULES_USING:
        is_result = await call_route(route)

        if IS_SLEEP and is_result:
            has_minted_one_time = is_result
            await client.initial_delay(
                sleep_from=SLEEP_BETWEEN_BRIDGES_ON_ONE_ACCOUNT_FROM,
                sleep_to=SLEEP_BETWEEN_BRIDGES_ON_ONE_ACCOUNT_TO,
                message='before next mint'
            )


async def _mint_one_nft_or_some_nfts(account_id, private_key, nft_name) -> bool:
    random.shuffle(MINT_NETWORKS)
    has_minted_one_time = False

    for option in MINT_NETWORKS:
        network_name = random.choice(option)
        if network_name is None:
            continue

        network_object = Networks.get_network(network_name=network_name)
        client = Client(
            account_id=account_id,
            private_key=private_key,
            network=network_object,
        )
        zkbridge = ZkBridge(client)

        network = client.account_manager.network.name
        is_result = await zkbridge.mint(
            nft_name=nft_name,
            network=network
        )

        if IS_SLEEP and network != MINT_NETWORKS[-1] and is_result:
            has_minted_one_time = is_result
            await client.initial_delay(
                sleep_from=SLEEP_BETWEEN_MINTS_ON_ONE_ACCOUNT_FROM,
                sleep_to=SLEEP_BETWEEN_MINT_ON_ONE_ACCOUNT_TO,
                message='before next mint'
            )

    return has_minted_one_time
