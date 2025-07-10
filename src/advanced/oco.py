from logger import logger

@staticmethod
def oco_order(client, symbol, side, quantity, price, stop_price, stop_limit_price):
    """Place an OCO (One-Cancels-Other) order"""
    try:
        ticker = client.futures_symbol_ticker(symbol=symbol)
        current_price = float(ticker['price'])

        limit_order = client.futures_create_order(
        symbol=symbol,
        side='SELL' if side == 'BUY' else 'BUY',
        type='LIMIT',
        timeInForce='GTC',
        quantity=str(quantity),
        price=str(price)
        )

        stop_order_type = 'STOP_MARKET'

        if side == 'BUY' and stop_price > current_price:
            raise ValueError("For BUY position, stop must be BEOW current price")
        elif side == "SELL" and stop_price < current_price:
            raise ValueError("For SELL position, stop price must be ABOVE current price")

    # Place stop-loss order (using stop-market for simplicity)
        stop_order = client.futures_create_order(
        symbol=symbol,
        side='SELL' if side == 'BUY' else 'BUY',
        type=stop_order_type,
        quantity=str(quantity),
        stopPrice=str(stop_price))

        return [limit_order, stop_order]
    except Exception as e:
        logger.error(f"OCO order failed: {str(e)}")
        raise
