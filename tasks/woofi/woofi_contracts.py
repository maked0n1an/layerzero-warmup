import min_library.models.others.exceptions as exceptions
from min_library.models.contracts.raw_contract import RawContract
from min_library.models.networks.networks import Networks
from min_library.utils.helpers import read_json


class WoofiContracts:
    WOOFI_ROUTER_V2_ABI = read_json(
        path=('data', 'abis', 'woofi', 'abi.json')
    )

    contracts_dict = {
        'WooRouterV2': {
            Networks.Arbitrum.name: RawContract(
                title='WooRouterV2_Arbitrum',
                address='0x9aed3a8896a85fe9a8cac52c9b402d092b629a30',
                abi=WOOFI_ROUTER_V2_ABI
            ),
            Networks.Polygon.name: RawContract(
                title='WooRouterV2_Polygon',
                address='0x817Eb46D60762442Da3D931Ff51a30334CA39B74',
                abi=WOOFI_ROUTER_V2_ABI
            ),
            Networks.BSC.name: RawContract(
                title='WooRouterV2_BSC',
                address='0x4f4fd4290c9bb49764701803af6445c5b03e8f06',
                abi=WOOFI_ROUTER_V2_ABI
            )
        },
        'AggregationRouterV5': {
            Networks.Polygon.name: RawContract(
                title='AggregationRouterV5_Polygon',
                address='0x1111111254EEB25477B68fb85Ed929f73A960582',
                abi=read_json(
                    path=('data', 'abis', '1inch', 'router_v5.json')
                )
            )
        }
    }

    @classmethod
    def get_dex_contract(cls, name: str, network: str) -> RawContract | None:
        if name not in cls.contracts_dict:
            raise exceptions.DexNotExists(
                "This router has not been added to WooFiContracts")

        router_data = cls.contracts_dict[name]

        if network in router_data:

            return router_data[network]
