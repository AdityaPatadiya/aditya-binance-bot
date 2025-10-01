from logger import logger


@staticmethod
def limit_order(client, symbol, side, quantity, price, time_in_force='GTC'):
    """Place a limit order"""
    try:
        order = client.order_limit(
            symbol=symbol,
            side=side.upper(),
            quantity=str(quantity),
            price=str(price),
            timeInForce = time_in_force
        )

        logger.info(f"Limit order placed successfully: {order}")
        return order
    except Exception as e:
        logger.error(f"Limit order failed: {str(e)}")
        raise
