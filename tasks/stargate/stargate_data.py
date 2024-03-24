from min_library.models.bridges.bridge_data import TokenBridgeInfo
from min_library.models.bridges.network_data import NetworkData
from min_library.models.networks.networks import Networks
from min_library.models.others.constants import TokenSymbol
from min_library.models.bridges.network_data_fetcher import NetworkDataFetcher
from tasks.stargate.stargate_contracts import StargateContracts


class StargateData(NetworkDataFetcher):
    SPECIAL_COINS = [
        TokenSymbol.USDV
    ]
    
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
                ),
                # TokenSymbol.USDC_E + TokenSymbol.USDV: TokenBridgeInfo(
                #     bridge_contract=StargateContracts.ARBITRUM_USDV_BRIDGE_RECOLOR_NOT_WORKING,
                # ),
                TokenSymbol.USDV + TokenSymbol.USDV: TokenBridgeInfo(
                    bridge_contract=StargateContracts.ARBITRUM_USDV
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
                # TokenSymbol.USDC_E + TokenSymbol.USDV: TokenBridgeInfo(
                #     bridge_contract=StargateContracts.AVALANCHE_USDV_BRIDGE_RECOLOR_NOT_WORKING,
                # ),            
                # TokenSymbol.USDT + TokenSymbol.USDV: TokenBridgeInfo(
                #     bridge_contract=StargateContracts.AVALANCHE_USDV_BRIDGE_RECOLOR_NOT_WORKING,
                # ),
                TokenSymbol.USDV + TokenSymbol.USDV: TokenBridgeInfo(
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
                ),
                TokenSymbol.USDV + TokenSymbol.USDV: TokenBridgeInfo(
                    bridge_contract=StargateContracts.BSC_USDV
                ),
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
                ),
                TokenSymbol.USDC_E + TokenSymbol.USDV: TokenBridgeInfo(
                    bridge_contract=StargateContracts.OPTIMISM_USDV_BRIDGE_RECOLOR,
                ),
                TokenSymbol.USDV + TokenSymbol.USDV: TokenBridgeInfo(
                    bridge_contract=StargateContracts.OPTIMISM_USDV
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
                TokenSymbol.USDC_E + TokenSymbol.USDV: TokenBridgeInfo(
                    bridge_contract=StargateContracts.POLYGON_USDV_BRIDGE_RECOLOR,
                ),
                TokenSymbol.USDT + TokenSymbol.USDV: TokenBridgeInfo(
                    bridge_contract=StargateContracts.POLYGON_USDV_BRIDGE_RECOLOR,
                ),
                TokenSymbol.USDV + TokenSymbol.USDV: TokenBridgeInfo(
                    bridge_contract=StargateContracts.POLYGON_USDV
                )
            }
        )
    }
