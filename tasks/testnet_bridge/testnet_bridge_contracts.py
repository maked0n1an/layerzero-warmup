from min_library.models.contracts.raw_contract import RawContract
from min_library.utils.helpers import read_json


class TestnetBridgeContracts:
    TESTNET_BRIDGE_ABI = read_json(
        path=('data', 'abis', 'layerzero', 'testnet_bridge', 'abi.json')
    )
    
    ARBITRUM_GETH_LZ = RawContract(
        title='LayerZero: GETH Token (Arbitrum GETH_LZ)',
        address='0xdD69DB25F6D620A7baD3023c5d32761D353D3De9',
        abi=TESTNET_BRIDGE_ABI
    )