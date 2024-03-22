from min_library.models.contracts.raw_contract import RawContract
from min_library.utils.helpers import read_json


class StargateContracts:
    STARGATE_ROUTER_ABI = read_json(
        path=('data', 'abis', 'layerzero', 'stargate', 'router_abi.json')
    )

    STARGATE_ROUTER_ETH_ABI = read_json(
        path=('data', 'abis', 'layerzero', 'stargate', 'router_eth_abi.json')
    )

    STARGATE_STG_ABI = read_json(
        path=('data', 'abis', 'layerzero', 'stargate', 'stg_abi.json')
    )
    
    STARGATE_BRIDGE_RECOLOR = read_json(
        path=('data', 'abis', 'layerzero', 'stargate', 'bridge_recolor.json')
    )
    STARGATE_OTUP = read_json(
        path=('data', 'abis', 'layerzero', 'stargate', 'usdv_abi.json')
    )    
    STARGATE_MESSAGING_V1_ABI = read_json(
        path=('data', 'abis', 'layerzero', 'stargate', 'msg_abi.json')
    )

    ARBITRUM_UNIVERSAL = RawContract(
        title='Stargate Finance: Router (Arbitrum USDC)',
        address='0x53bf833a5d6c4dda888f69c22c88c9f356a41614',
        abi=STARGATE_ROUTER_ABI
    )

    ARBITRUM_ETH = RawContract(
        title='Stargate Finance: Router (Arbitrum ETH)',
        address='0xbf22f0f184bCcbeA268dF387a49fF5238dD23E40',
        abi=STARGATE_ROUTER_ETH_ABI
    )

    ARBITRUM_STG = RawContract(
        title='Stargate Finance: (Arbitrum STG)',
        address='0x6694340fc020c5e6b96567843da2df01b2ce1eb6',
        abi=STARGATE_ROUTER_ETH_ABI
    )

    AVALANCHE_UNIVERSAL = RawContract(
        title='Stargate Finance: Router (Avalanche Universal)',
        address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
        abi=STARGATE_ROUTER_ABI
    )

    AVALANCHE_USDT = RawContract(
        title='Stargate Finance: Router (Avalanche USDT)',
        address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
        abi=STARGATE_ROUTER_ABI
    )
    
    AVALANCHE_STG = RawContract(
        title='Stargate Finance (Avalanche STG)',
        address='0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590',
        abi=STARGATE_STG_ABI
    )
    
    AVALANCHE_USDV_BRIDGE_RECOLOR = RawContract(
        title='BridgeRecolor (AVAX-C)',
        address='0x292dD933180412923ee47fA73bBF407B6d776B4C',
        abi=STARGATE_BRIDGE_RECOLOR
    )

    BSC_USDT = RawContract(
        title='Stargate Finance: Router (BSC USDT)',
        address='0x4a364f8c717cAAD9A442737Eb7b8A55cc6cf18D8',
        abi=STARGATE_ROUTER_ABI
    )

    BSC_BUSD = RawContract(
        title='Stargate Finance: Router (BSC BUSD)',
        address='0xB16f5A073d72cB0CF13824d65aA212a0e5c17D63',
        abi=STARGATE_ROUTER_ABI
    )

    BSC_STG = RawContract(
        title='Stargate Finance: (STG Token)',
        address='0xB0D502E938ed5f4df2E681fE6E419ff29631d62b',
        abi=STARGATE_STG_ABI
    )

    FANTOM_USDC = RawContract(
        title='Stargate Finance: Router (Fantom USDC)',
        address='0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6',
        abi=STARGATE_ROUTER_ABI
    )

    OPTIMISM_ETH = RawContract(
        title='Stargate Finance: ETH Router (Optimism)',
        address='0xB49c4e680174E331CB0A7fF3Ab58afC9738d5F8b',
        abi=STARGATE_ROUTER_ETH_ABI
    )

    OPTIMISM_UNIVERSAL = RawContract(
        title='Stargate Finance: Router (Optimism USDC)',
        address='0xb0d502e938ed5f4df2e681fe6e419ff29631d62b',
        abi=STARGATE_ROUTER_ABI
    )

    POLYGON_UNIVERSAL = RawContract(
        title='Stargate Finance: Router (Polygon Universal)',
        address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
        abi=STARGATE_ROUTER_ABI
    )
    POLYGON_STG = RawContract(
        title='Stargate Finance: STG Token',
        address='0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590',
        abi=STARGATE_STG_ABI
    )
    POLYGON_USDV_BRIDGE_RECOLOR = RawContract(
        title='BridgeRecolor (Polygon)',
        address='0xAb43a615526e3e15B63e5812f74a0A1B86E9965E',
        abi=STARGATE_BRIDGE_RECOLOR
    )
    POLYGON_USDV_TO_USDV = RawContract(
        title='OptimizedTransparentUpgradeableProxy (Polygon)',
        address='0x323665443CEf804A3b5206103304BD4872EA4253',
        abi=STARGATE_OTUP
    )
