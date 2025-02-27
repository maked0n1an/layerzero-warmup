from min_library.models.bridges.bridge_data import TokenBridgeInfo
from min_library.models.bridges.network_data import NetworkData
from min_library.models.networks.networks import Networks
from min_library.models.others.constants import TokenSymbol
from min_library.models.bridges.network_data_fetcher import NetworkDataFetcher
from tasks.coredao.coredao_contracts import CoreDaoBridgeContracts


class CoredaoData(NetworkDataFetcher):
    networks_data = {
        Networks.Arbitrum.name: NetworkData(
            chain_id=110,
            bridge_dict={
                TokenSymbol.USDT: TokenBridgeInfo(
                    bridge_contract=CoreDaoBridgeContracts.ARBITRUM
                ),
                TokenSymbol.USDC: TokenBridgeInfo(
                    bridge_contract=CoreDaoBridgeContracts.ARBITRUM
                ),
            }
        ),
        Networks.Avalanche.name: NetworkData(
            chain_id=106,
            bridge_dict={
                TokenSymbol.USDT: TokenBridgeInfo(
                    bridge_contract=CoreDaoBridgeContracts.AVALANCHE
                ),
                TokenSymbol.USDC: TokenBridgeInfo(
                    bridge_contract=CoreDaoBridgeContracts.ARBITRUM
                ),
            }
        ),
        Networks.BSC.name: NetworkData(
            chain_id=102,
            bridge_dict={
                TokenSymbol.USDT: TokenBridgeInfo(
                    bridge_contract=CoreDaoBridgeContracts.BSC
                ),
                TokenSymbol.USDC: TokenBridgeInfo(
                    bridge_contract=CoreDaoBridgeContracts.BSC
                ),
            }
        ),
        Networks.Core.name: NetworkData(
            chain_id=153,
            bridge_dict={
                TokenSymbol.USDT: TokenBridgeInfo(
                    bridge_contract=CoreDaoBridgeContracts.CORE
                ),
                TokenSymbol.USDC: TokenBridgeInfo(
                    bridge_contract=CoreDaoBridgeContracts.CORE
                ),
            }
        ),
        Networks.Polygon.name: NetworkData(
            chain_id=109,
            bridge_dict={
                TokenSymbol.USDT: TokenBridgeInfo(
                    bridge_contract=CoreDaoBridgeContracts.POLYGON
                ),
                TokenSymbol.USDC: TokenBridgeInfo(
                    bridge_contract=CoreDaoBridgeContracts.POLYGON
                ),                
            }
        ),
    }
