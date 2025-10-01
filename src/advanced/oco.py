from logger import logger

@staticmethod
def oco_order(client, symbol, side, quantity, price, stop_price, stop_limit_price):
    """Place an OCO (One-Cancels-Other) order"""
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        current_price = float(ticker['price'])

        if side.upper() == 'BUY':
            if price >= current_price:
                raise ValueError("For BUY OCO, stop price should be BELOW current price for buying dips")
            
            if stop_price <= current_price:
                raise ValueError("For BUY OCO, stop price should be ABOVE current price for protection")
            
        else:
            if price <= current_price:
                raise ValueError("For SELL OCO, limit price should be ABOVE currnent price for profit taking")
            
            if stop_price >= current_price:
                raise ValueError("For SELL OCO, stop price should be BELOW current price for protection")

        oco_place = client.order_oco(
            symbol=symbol,
            side=side.upper(),
            quantity=str(quantity),
            price=str(price),
            stopPrice=str(stop_price),
            stopLimitPrice=str(stop_limit_price),
            stopLimitTimeForce='GTC'
        )

        logger.info(f"OCO order placed successfully: {oco_order}")
        return oco_order
    
    except Exception as e:
        logger.error(f"OCO order failed: {str(e)}")
        raise
