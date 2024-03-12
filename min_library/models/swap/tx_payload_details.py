from typing import List


class TxPayloadDetails:
    def __init__(
        self,
        method_name: str,
        addresses: List[str],
        function_signature: str | None = None,
        bool_list: List[bool] | None = None
    ):
        """
        Initialize the RouteInfo class.

        Args:
            method_name (str): The name of the method.
            addresses (List[str]): The list of addresses.
            function_signature (str | None): The hex signature of provided function.
            bool_list (List[bool] | None): The list of boolean values (default is None).

        """
        self.method_name = method_name
        self.swap_path = addresses
        if function_signature:
            self.function_signature = function_signature
        if bool_list:
            self.bool_list = bool_list