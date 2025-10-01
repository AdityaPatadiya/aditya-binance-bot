from binance.enums import *
from logger import logger

@staticmethod
def market_order(client, symbol, side, quantity):
    """Place a market order"""
    try:
        order = client.order_market(
            symbol=symbol,
            side = side,
            type=FUTURE_ORDER_TYPE_MARKET,
            quantity = str(quantity)
        )

        logger.info(f"Market order placed successfully: {order}")
        return order
    except Exception as e:
        logger.error(f"Market order failed: {str(e)}")
        raise
