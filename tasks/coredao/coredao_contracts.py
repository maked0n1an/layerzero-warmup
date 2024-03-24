from min_library.models.contracts.raw_contract import RawContract
from min_library.utils.helpers import read_json


class CoreDaoBridgeContracts:
    BSC = RawContract(
        title='OriginalTokenBridge (BSC)',
        address='0x52e75D318cFB31f9A2EdFa2DFee26B161255B233',
        abi=read_json(
            path=('data', 'abis', 'layerzero', 'coredao', 'bsc_bridge_abi.json')
        )
    )

    CORE = RawContract(
        title='WrappedTokenBridge (CORE)',
        address='0xA4218e1F39DA4AaDaC971066458Db56e901bcbdE',
        abi=read_json(
            path=('data', 'abis', 'layerzero', 'coredao', 'core_bridge_abi.json')
        )
    )
