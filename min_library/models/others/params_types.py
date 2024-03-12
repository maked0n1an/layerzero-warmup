from web3 import types
from web3.contract import AsyncContract, Contract

from min_library.models.contracts.raw_contract import (
    NativeTokenContract,
    RawContract,
    TokenContract
)
from .token_amount import TokenAmount


class ParamsTypes:
    Contract = RawContract | AsyncContract | Contract
    TokenContract = TokenContract | NativeTokenContract
    Address = str | types.Address | types.ChecksumAddress | types.ENS
    Amount = float | int | TokenAmount
    GasPrice = float | int | TokenAmount
    GasLimit = int | TokenAmount
