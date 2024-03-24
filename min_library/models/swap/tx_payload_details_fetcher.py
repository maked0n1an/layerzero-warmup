import min_library.models.others.exceptions as exceptions
from min_library.models.swap.tx_payload_details import TxPayloadDetails


class TxPayloadDetailsFetcher:
    PATHS: dict[str, dict[str: TxPayloadDetails]] = {}

    @classmethod
    def get_tx_payload_details(
        cls,
        first_token: str,
        second_token: str
    ) -> TxPayloadDetails:
        first_token = first_token.upper()
        second_token = second_token.upper()

        if first_token not in cls.PATHS:
            raise exceptions.TxPayloadDetailsNotAdded(
                f"The '{first_token}' token has not been "
                f"added to {cls.__name__} PATHS dict"
            )

        available_token_routes = cls.PATHS[first_token]

        if second_token not in available_token_routes:
            raise exceptions.TxPayloadDetailsNotAdded(
                f"The '{second_token}' as second token has not been "
                f"added to {cls.__name__} {first_token} PATHS dict"
            )

        return available_token_routes[second_token]
