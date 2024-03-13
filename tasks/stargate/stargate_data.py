from min_library.models.bridges.bridge_data import TokenBridgeInfo
from min_library.models.bridges.network_data import NetworkData
from min_library.models.networks.networks import Networks
from min_library.models.others.constants import TokenSymbol
from min_library.models.bridges.network_data_fetcher import NetworkDataFetcher
from tasks.stargate.stargate_contracts import StargateContracts


class StargateData(NetworkDataFetcher):
    networks_data = {
        Networks.Arbitrum.name: NetworkData(
            chain_id=110,
            bridge_dict={
                TokenSymbol.USDC_E: TokenBridgeInfo(
                    bridge_contract=StargateContracts.ARBITRUM_UNIVERSAL,
                    pool_id=1
                ),
                TokenSymbol.USDT: TokenBridgeInfo(
                    bridge_contract=StargateContracts.ARBITRUM_UNIVERSAL,
                    pool_id=2
                ),
                TokenSymbol.DAI: TokenBridgeInfo(
                    bridge_contract=StargateContracts.ARBITRUM_UNIVERSAL,
                    pool_id=3
                ),
                TokenSymbol.ETH: TokenBridgeInfo(
                    bridge_contract=StargateContracts.ARBITRUM_ETH,
                    pool_id=13
                ),
                TokenSymbol.STG: TokenBridgeInfo(
                    bridge_contract=StargateContracts.BSC_STG
                )
            }
        ),
        Networks.Avalanche.name: NetworkData(
            chain_id=106,
            bridge_dict={
                TokenSymbol.USDC: TokenBridgeInfo(
                    bridge_contract=StargateContracts.AVALANCHE_UNIVERSAL,
                    pool_id=1
                ),
                TokenSymbol.USDT: TokenBridgeInfo(
                    bridge_contract=StargateContracts.AVALANCHE_UNIVERSAL,
                    pool_id=2
                ),
                TokenSymbol.STG: TokenBridgeInfo(
                    bridge_contract=StargateContracts.AVALANCHE_STG
                ),
                TokenSymbol.USDV: TokenBridgeInfo(
                    bridge_contract=StargateContracts.AVALANCHE_USDV
                )
            }
        ),
        Networks.BSC.name: NetworkData(
            chain_id=102,
            bridge_dict={
                TokenSymbol.USDT: TokenBridgeInfo(
                    bridge_contract=StargateContracts.BSC_USDT,
                    pool_id=2
                ),
                TokenSymbol.BUSD: TokenBridgeInfo(
                    bridge_contract=StargateContracts.BSC_BUSD,
                    pool_id=5
                ),
                TokenSymbol.STG: TokenBridgeInfo(
                    bridge_contract=StargateContracts.BSC_STG
                )
            }
        ),
        Networks.Fantom.name: NetworkData(
            chain_id=112,
            bridge_dict={
                TokenSymbol.USDC: TokenBridgeInfo(
                    bridge_contract=StargateContracts.FANTOM_USDC,
                    pool_id=21
                )
            }
        ),
        Networks.Optimism.name: NetworkData(
            chain_id=111,
            bridge_dict={
                TokenSymbol.USDC_E: TokenBridgeInfo(
                    bridge_contract=StargateContracts.OPTIMISM_UNIVERSAL,
                    pool_id=1
                ),
                TokenSymbol.DAI: TokenBridgeInfo(
                    bridge_contract=StargateContracts.OPTIMISM_UNIVERSAL,
                    pool_id=3
                ),
                TokenSymbol.ETH: TokenBridgeInfo(
                    bridge_contract=StargateContracts.OPTIMISM_ETH,
                    pool_id=13
                )
            }
        ),
        Networks.Polygon.name: NetworkData(
            chain_id=109,
            bridge_dict={
                TokenSymbol.USDC_E: TokenBridgeInfo(
                    bridge_contract=StargateContracts.POLYGON_UNIVERSAL,
                    pool_id=1
                ),
                TokenSymbol.USDT: TokenBridgeInfo(
                    bridge_contract=StargateContracts.POLYGON_UNIVERSAL,
                    pool_id=2
                ),
                TokenSymbol.DAI: TokenBridgeInfo(
                    bridge_contract=StargateContracts.POLYGON_UNIVERSAL,
                    pool_id=3
                ),
                TokenSymbol.STG: TokenBridgeInfo(
                    bridge_contract=StargateContracts.POLYGON_STG
                ),
            }
        )
    }
