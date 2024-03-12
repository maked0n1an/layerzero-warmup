from typing import Any

from min_library.models.others.common import AutoRepr


class TxArgs(AutoRepr):
    """
    An instance for named transaction arguments.
    """

    def __init__(self, **kwargs) -> None:
        """
        Initialize the class.

        Args:
            **kwargs: named arguments of a contract transaction.

        """
        self.__dict__.update(kwargs)

    def get_list(self) -> list[Any]:
        """
        Get list of transaction arguments.

        Returns:
            List[Any]: list of transaction arguments.

        """
        return list(self.__dict__.values())

    def get_tuple(self) -> tuple[str, Any]:
        """
        Get tuple of transaction arguments.

        Returns:
            Tuple[Any]: tuple of transaction arguments.

        """
        return tuple(self.__dict__.values())
