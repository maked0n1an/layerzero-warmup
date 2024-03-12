from min_library.models.contracts.raw_contract import TokenContract
from min_library.models.others.token_amount import TokenAmount


class SwapQuery:
    """
    A class representing a swap query.

    Attributes:
        from_token (TokenContract): The contract of the token to swap from.
        to_token (TokenContract): The contract of the token to swap to.
        amount_from (TokenAmount): The amount of the 'from' token.
        min_to_amount (TokenAmount | None): The minimum amount of the 'to' token.

    """

    def __init__(
        self,
        from_token: TokenContract,
        amount_from: TokenAmount,
        to_token: TokenContract | None = None,
        min_to_amount: TokenAmount | None = None
    ) -> None:
        """
        Initialize the SwapQuery class.

        Args:
            from_token (TokenContract): The contract of the token to swap from.
            amount_from (TokenAmount): The amount of the from token.
            to_token (TokenContract | None): The contract of the token to swap to (default is None).
            min_to_amount (TokenAmount | None): The minimum amount of the to token (default is None).

        """
        self.from_token = from_token
        self.to_token = to_token
        self.amount_from = amount_from
        self.min_to_amount = min_to_amount
