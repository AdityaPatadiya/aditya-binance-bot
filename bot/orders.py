from .logger import log_error, log_info


def place_order(client, symbol, side, order_type, quantity, price=None):
    try:
        params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": quantity
        }
        
        if order_type.upper() == "LIMIT":
            params["price"] = price
            params["timeInForce"] = "GTC"
        
        response = client.futures_create_order(**params)
        log_info(f"Order places: {response}")
        return response
    except Exception as e:
        log_error(e)
        return None
