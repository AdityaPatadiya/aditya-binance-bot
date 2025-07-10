from binance.enums import *
from logger import logger

@staticmethod
def market_order(client, symbol, side, quantity):
    """Place a market order"""
    try:
        return client.futures_create_order(
            symbol=symbol,
            side = side,
            type=FUTURE_ORDER_TYPE_MARKET,
            quantity = str(quantity)
        )
    except Exception as e:
        logger.error(f"Market order failed: {str(e)}")
        raise
