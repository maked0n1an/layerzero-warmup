from min_library.models.contracts.raw_contract import RawContract


class TokenBridgeInfo:
    def __init__(
        self,
        bridge_contract: RawContract,
        pool_id: int | None = None
    ) -> None:
        self.bridge_contract = bridge_contract
        self.pool_id = pool_id
