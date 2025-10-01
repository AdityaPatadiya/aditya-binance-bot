from logger import logger

@staticmethod
def stop_limit_order(client, symbol, side, quantity, price, stop_price, time_in_force='GTC'):
    """Place a stop-limit order"""
    try:
        order = client.order(
            symbol=symbol,
            side=side.upper(),
            type="STOP_LOSS_LIMIT",
            quantity=str(quantity),
            price=str(price),
            stopPrice=str(stop_price),
            timeInForce=time_in_force   
        )

        logger.info(f"Stop-limit order placed successfully: {order}")
        return order
    
    except Exception as e:
        logger.error(f"Stop-limit order failed: {str(e)}")
        raise
