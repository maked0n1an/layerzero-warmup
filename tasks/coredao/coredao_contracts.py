from min_library.models.contracts.raw_contract import RawContract
from min_library.utils.helpers import read_json


class CoreDaoBridgeContracts:
    TO_CORE_BRIDGE_ABI = read_json(
        path=('data', 'abis', 'layerzero', 'coredao', 'to_core_bridge_abi.json')
    )
    
    FROM_CORE_BRIDGE_ABI = read_json(
        path=('data', 'abis', 'layerzero', 'coredao', 'from_core_bridge_abi.json')
    )

    BSC = RawContract(
        title='OriginalTokenBridge (BSC)',
        address='0x52e75D318cFB31f9A2EdFa2DFee26B161255B233',
        abi=TO_CORE_BRIDGE_ABI
    )

    CORE = RawContract(
        title='WrappedTokenBridge (CORE)',
        address='0xA4218e1F39DA4AaDaC971066458Db56e901bcbdE',
        abi=FROM_CORE_BRIDGE_ABI
    )

    POLYGON = RawContract(
        title='OriginalTokenBridge (POLYGON)',
        address='0x52e75D318cFB31f9A2EdFa2DFee26B161255B233',
        abi=TO_CORE_BRIDGE_ABI
    )
    
    ARBITRUM = RawContract(
        title='OriginalTokenBridge (ARBITRUM)',
        address='0x29d096cD18C0dA7500295f082da73316d704031A',
        abi=TO_CORE_BRIDGE_ABI
    )
