from min_library.models.others.common import Singleton


class TokenSymbol(metaclass=Singleton):
    ETH = 'ETH'

    ARB = 'ARB'
    AVAX = 'AVAX'
    BNB = 'BNB'
    BUSD = 'BUSD'
    CELO = 'CELO'
    CORE = 'CORE'
    DAI = 'DAI'
    FRAX = 'FRAX'
    FTM = 'FTM'
    GETH = 'GETH'
    GETH_LZ = 'GETH_LZ'
    GLMR = 'GLMR'
    HECO = 'HECO'
    KAVA = 'KAVA'
    MATIC = 'MATIC'
    STG = 'STG'
    USDT = 'USDT'
    USDC = 'USDC'
    USDC_E = 'USDC_E'
    USDV = 'USDV'
    WBTC = 'WBTC'
    WCORE = 'WCORE'
    WETH = 'WETH'
    XDAI = 'xDAI'
    
class LogStatus:
    DELAY = 'DELAY'
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'
    
    APPROVED = 'APPROVED'
    MINTED = 'MINTED'
    BRIDGED = 'BRIDGED'
    SWAPPED = 'SWAPPED'
