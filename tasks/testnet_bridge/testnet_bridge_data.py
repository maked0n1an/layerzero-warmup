from min_library.models.bridges.bridge_data import TokenBridgeInfo
from min_library.models.bridges.network_data import NetworkData
from min_library.models.networks.networks import Networks
from min_library.models.others.constants import TokenSymbol
from min_library.models.bridges.network_data_fetcher import NetworkDataFetcher
from tasks.testnet_bridge.testnet_bridge_contracts import TestnetBridgeContracts


class TestnetBridgeData(NetworkDataFetcher):
    networks_data = {
        Networks.Arbitrum.name: NetworkData(
            chain_id=110,
            bridge_dict={
                TokenSymbol.GETH_LZ: TokenBridgeInfo(
                    bridge_contract=TestnetBridgeContracts.ARBITRUM_GETH_LZ,
                )
            }
        )
    }
