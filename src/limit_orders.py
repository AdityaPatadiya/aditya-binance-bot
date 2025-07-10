from logger import logger


@staticmethod
def limit_order(client, symbol, side, quantity, price, time_in_force='GTC'):
    """Place a limit order"""
    try:
        params = {
            "symbol": symbol,
            "side": side,
            "type": 'LIMIT',
            "timeInForce": time_in_force,
            "quantity": str(quantity),
            "price": str(price)
        }
        if 'testnet.binancefuture.com' not in client.FUTURES_URL:
            params['timeInForce'] = time_in_force
        return client.futures_create_order(**params)
    except Exception as e:
        logger.error(f"Limit order failed: {str(e)}")
        raise
