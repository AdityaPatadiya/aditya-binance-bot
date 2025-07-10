from binance.enums import *
import time
from logger import logger

@staticmethod
def twap_order(client, symbol, side, total_quantity, duration_min, slices=4):
    """Place a TWAP (Tine-Weighted Average Price) order"""
    try:
        results = []
        if slices < 1:
            raise ValueError("At least 1 slice required")

        slice_quantity = total_quantity / slices
        interval = (duration_min * 60) / slices

        for i in range(slices):
            try:
                logger.info(f"Executing TWAP slice {i+1}/{slices}")
                result = client.futures_create_order(
                    symbol = symbol,
                    side = side,
                    type=FUTURE_ORDER_TYPE_MARKET,
                    quantity = str(round(slice_quantity, 6))
                )
                results.append(result)
            except Exception as slice_error:
                logger.error(f"Slice{i+1} failed: {str(slice_error)}")
            time.sleep(interval)
        return results
    except Exception as e:
        logger.error(f"TWAP order failed: {str(e)}")
        raise
