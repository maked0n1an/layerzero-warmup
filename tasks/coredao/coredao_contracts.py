from min_library.models.contracts.raw_contract import RawContract
from min_library.utils.helpers import read_json


class CoreDaoBridgeContracts:
    COREDAO_BRIDGE_ABI = read_json(
        path=('data', 'abis', 'layerzero', 'coredao', 'bridge_abi.json')       
    )

    BSC = RawContract(
        title='OriginalTokenBridge (BSC)',
        address='0x52e75D318cFB31f9A2EdFa2DFee26B161255B233',
        abi=COREDAO_BRIDGE_ABI
    )