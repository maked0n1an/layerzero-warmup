from min_library.models.bridges.bridge_data import TokenBridgeInfo


class NetworkData:
    def __init__(
        self,
        chain_id: int,
        bridge_dict: dict[str, TokenBridgeInfo],
    ) -> None:
        self.chain_id = chain_id
        self.bridge_dict = bridge_dict
