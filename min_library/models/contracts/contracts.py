from min_library.models.networks.networks import Networks
from min_library.models.others.constants import TokenSymbol
from min_library.models.others.common import Singleton
from min_library.models.contracts.raw_contract import (
    TokenContract,
    NativeTokenContract
)
import min_library.models.others.exceptions as exceptions
from min_library.utils.helpers import read_json


class ContractsFactory:
    @staticmethod
    def get_contract(network_name: str, token_symbol: str):
        match(network_name):
            case Networks.Ethereum.name:
                return EthereumTokenContracts.get_token(token_symbol)
            case Networks.Arbitrum.name:
                return ArbitrumTokenContracts.get_token(token_symbol)
            case Networks.Avalanche.name:
                return AvalancheTokenContracts.get_token(token_symbol)
            case Networks.BSC.name:
                return BscTokenContracts.get_token(token_symbol)
            case Networks.Core.name:
                return CoreTokenContracts.get_token(token_symbol)
            case Networks.Fantom.name:
                return FantomTokenContracts.get_token(token_symbol)
            # case Networks.Kava.name:
            #     return KavaTokenContracts.get_token(token_symbol)
            case Networks.Optimism.name:
                return OptimismTokenContracts.get_token(token_symbol)
            case Networks.Polygon.name:
                return PolygonTokenContracts.get_token(token_symbol)
            # case Networks.ZkSync.name:
            #     return ZkSyncTokenContracts.get_token(token_symbol)
            case _:
                raise ValueError("Network not supported")


class TokenContractData(metaclass=Singleton):
    NATIVE_ETH = NativeTokenContract(title=TokenSymbol.ETH)

    ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

    @classmethod
    def get_token(
        cls,
        token_symbol: str,
        project_prefix: str | None = None,
    ) -> TokenContract:
        contract_name = (
            f'{token_symbol.upper()}_{project_prefix.upper()}'
            if project_prefix
            else f'{token_symbol.upper()}'
        )

        if not hasattr(cls, contract_name):
            raise exceptions.ContractNotExists(
                f"The contract has not been added "
                f"to {cls.__class__.__name__} contracts"
            )

        return getattr(cls, contract_name)


class EthereumTokenContracts(TokenContractData):
    ETH = TokenContractData.NATIVE_ETH

class ArbitrumTokenContracts(TokenContractData):
    ETH = TokenContractData.NATIVE_ETH

    ARB = TokenContract(
        title=TokenSymbol.ARB,
        address='0x912CE59144191C1204E64559FE8253a0e49E6548',
        decimals=18
    )

    GETH = TokenContract(
        title=TokenSymbol.GETH,
        address='0xaF7355462240d5a8f3509BD890994AF1022F1948',
        decimals=18
    )

    GETH_LZ = TokenContract(
        title="GETH_LZ",
        address='0xdD69DB25F6D620A7baD3023c5d32761D353D3De9',
        decimals=18
    )

    USDC = TokenContract(
        title=TokenSymbol.USDC,
        address='0xaf88d065e77c8cC2239327C5EDb3A432268e5831',
    )

    USDT = TokenContract(
        title=TokenSymbol.USDT,
        address='0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
        decimals=6
    )

    USDV = TokenContract(
        title=TokenSymbol.USDV,
        address='0x323665443CEf804A3b5206103304BD4872EA4253',
        abi=read_json(
            path=('data', 'abis', 'layerzero', 'stargate', 'usdv_abi.json')
        )
    )

    DAI = TokenContract(
        title=TokenSymbol.DAI,
        address='0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1',
        decimals=18
    )

    USDC_E = TokenContract(
        title=TokenSymbol.USDC_E,
        address='0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8',
        decimals=6
    )

    WBTC = TokenContract(
        title=TokenSymbol.WBTC,
        address='0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f',
    )


class AvalancheTokenContracts(TokenContractData):
    AVAX = NativeTokenContract(title=TokenSymbol.AVAX)

    ETH = TokenContract(
        title=TokenSymbol.ETH,
        address='0xf20d962a6c8f70c731bd838a3a388d7d48fa6e15',
    )

    USDC = TokenContract(
        title=TokenSymbol.USDC,
        address='0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E',
        decimals=6
    )

    USDT = TokenContract(
        title=TokenSymbol.USDT,
        address='0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7',
    )

    USDV = TokenContract(
        title=TokenSymbol.USDV,
        address='0x323665443CEf804A3b5206103304BD4872EA4253',
        abi=read_json(
            path=('data', 'abis', 'layerzero', 'stargate', 'usdv_abi.json')
        )
    )

    FRAX = TokenContract(
        title=TokenSymbol.FRAX,
        address='0xD24C2Ad096400B6FBcd2ad8B24E7acBc21A1da64',
    )

    STG = TokenContract(
        title=TokenSymbol.STG,
        address='0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590'
    )


class BscTokenContracts(TokenContractData):
    BNB = NativeTokenContract(title=TokenSymbol.BNB)

    USDT = TokenContract(
        title=TokenSymbol.USDT,
        address='0x55d398326f99059fF775485246999027B3197955',
    )
    
    USDC = TokenContract(
        title=TokenSymbol.USDC,
        address='0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d',
        decimals=18
    )

    BUSD = TokenContract(
        title=TokenSymbol.BUSD,
        address='0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56',
    )

    STG = TokenContract(
        title=TokenSymbol.STG,
        address='0xb0d502e938ed5f4df2e681fe6e419ff29631d62b',
    )

    USDV = TokenContract(
        title=TokenSymbol.USDV,
        address='0x323665443CEf804A3b5206103304BD4872EA4253',
        abi=read_json(
            path=('data', 'abis', 'layerzero', 'stargate', 'usdv_abi.json')
        ),
        decimals=18,
    )

class CoreTokenContracts(TokenContractData):
    CORE = NativeTokenContract(title=TokenSymbol.CORE)
    
    USDT = TokenContract(
        title=TokenSymbol.USDT,
        address='0x900101d06a7426441ae63e9ab3b9b0f63be145f1',
        decimals=6
    )
    
    USDC = TokenContract(
        title=TokenSymbol.USDC,
        address='0xa4151B2B3e269645181dCcF2D426cE75fcbDeca9',
        decimals=6
    )
    
    WCORE = TokenContract(
        title=TokenSymbol.WCORE,
        address='0x191e94fa59739e188dce837f7f6978d84727ad01',
        decimals=18
    )

class FantomTokenContracts(TokenContractData):
    USDC = TokenContract(
        title=TokenSymbol.USDC,
        address='0x04068DA6C83AFCFA0e13ba15A6696662335D5B75',
        decimals=6
    )

    USDC_E = TokenContract(
        title=TokenSymbol.USDC,
        address='0x28a92dde19D9989F39A49905d7C9C2FAc7799bDf',
        decimals=6
    )

# class KavaTokenContracts(TokenContractFetcher):
#     STG = TokenContract(
#         title=TokenSymbol.STG,
#         address='',
#         decimals=18
#     )


class OptimismTokenContracts(TokenContractData):
    ETH = TokenContractData.NATIVE_ETH

    USDC = TokenContract(
        title=TokenSymbol.USDC,
        address='0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85',
        decimals=6
    )
    
    USDT = TokenContract(
        title=TokenSymbol.USDT,
        address='0x94b008aa00579c1307b0ef2c499ad98a8ce58e58',
        decimals=6
    )

    USDC_E = TokenContract(
        title=TokenSymbol.USDC_E,
        address='0x7F5c764cBc14f9669B88837ca1490cCa17c31607',
        decimals=6
    )

    DAI = TokenContract(
        title=TokenSymbol.DAI,
        address='0xda10009cbd5d07dd0cecc66161fc93d7c9000da1'
    )

    FRAX = TokenContract(
        title=TokenSymbol.FRAX,
        address='0x2E3D870790dC77A83DD1d18184Acc7439A53f475'
    )

    USDV = TokenContract(
        title=TokenSymbol.USDV,
        address='0x323665443CEf804A3b5206103304BD4872EA4253',
        abi=read_json(
            path=('data', 'abis', 'layerzero', 'stargate', 'usdv_abi.json')
        )
    )


class PolygonTokenContracts(TokenContractData):
    MATIC = NativeTokenContract(title=TokenSymbol.MATIC)

    USDC = TokenContract(
        title=TokenSymbol.USDC,
        address='0x3c499c542cef5e3811e1192ce70d8cc03d5c3359',
        decimals=6
    )

    USDC_E = TokenContract(
        title=TokenSymbol.USDC_E,
        address='0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
        decimals=6
    )

    USDT = TokenContract(
        title=TokenSymbol.USDT,
        address='0xc2132d05d31c914a87c6611c10748aeb04b58e8f',
        decimals=6
    )

    USDV = TokenContract(
        title=TokenSymbol.USDV,
        address='0x323665443CEf804A3b5206103304BD4872EA4253',
        abi=read_json(
            path=('data', 'abis', 'layerzero', 'stargate', 'usdv_abi.json')
        )
    )

    DAI = TokenContract(
        title=TokenSymbol.DAI,
        address='0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063'
    )

    WBTC = TokenContract(
        title=TokenSymbol.WBTC,
        address='0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6'
    )

    STG = TokenContract(
        title=TokenSymbol.STG,
        address='0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590',
        decimals=18
    )


# class ZkSyncTokenContracts(TokenContractFetcher):
#     ETH = NativeTokenContract(
#         title=TokenSymbol.ETH,
#         address=TokenContractFetcher.ZERO_ADDRESS
#     )

#     ceBUSD = TokenContract(
#         title=TokenSymbol.BUSD,
#         address='0x2039bb4116B4EFc145Ec4f0e2eA75012D6C0f181'
#     )

#     WETH = TokenContract(
#         title=TokenSymbol.WETH,
#         address='0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91',
#         abi=read_json(
#             path=('data', 'abis', 'zksync', 'weth_abi.json')
#         )
#     )

#     WBTC = TokenContract(
#         title=TokenSymbol.WBTC,
#         address='0xBBeB516fb02a01611cBBE0453Fe3c580D7281011',
#         decimals=8
#     )

#     USDC = TokenContract(
#         title=TokenSymbol.USDC,
#         address='0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4',
#         decimals=6
#     )

#     USDT = TokenContract(
#         title=TokenSymbol.USDT,
#         address='0x493257fD37EDB34451f62EDf8D2a0C418852bA4C',
#         decimals=6
#     )

#     SPACE = TokenContract(
#         title='SPACE',
#         address='0x47260090cE5e83454d5f05A0AbbB2C953835f777',
#         decimals=18
#     )
