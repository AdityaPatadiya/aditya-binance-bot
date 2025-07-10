from logger import logger

@staticmethod
def stop_limit_order(client, symbol, side, quantity, price, stop_price, time_in_force='GTC'):
    """Place a stop-limit order"""
    try:
        params = {
            "symbol": symbol,
            "side": side,
            "type": 'STOP',
            "quantity": str(quantity),
            "price": str(price),
            "stopPrice": str(stop_price)
        }
        if 'testnet.binancefuture.com' not in client.FUTURES_URL:
            params['timeInForce'] = time_in_force
        return client.futures_create_order(**params)
    except Exception as e:
        logger.error(f"Stop-limit order failed: {str(e)}")
        raise
