from binance.enums import *
import time
from logger import logger

@staticmethod
def twap_order(client, symbol, side, total_quantity, duration_min, slices=4):
    """Place a TWAP (Tine-Weighted Average Price) order"""
    try:
        results = []
        if slices < 1:
            raise ValueError("At least 1 slice required.")
        
        slice_quantity = total_quantity / slices
        interval_seconds = (duration_min * 60) / slices

        logger.info(f"Starting TWAP: {slices} slice over {duration_min} minutes")

        for i in range(slices):
            try:
                logger.info(f"Execution TWAP slice {i+1}/{slices} - Quantity: {slice_quantity:.6f}")

                result = client.order_market(
                    symbol=symbol,
                    side=side.upper(),
                    quantity=str(round(slice_quantity, 6))
                )

                results.append(result)
                logger.info(f"Slice {i+1} completed: Order ID {result.get('orderId')}")

                if i < slices -1:
                    time.sleep(interval_seconds)
                
            except Exception as slice_error:
                logger.error(f"Slice {i+1} failed: {str(slice_error)}")

                if i < slices - 1:
                    time.sleep(interval_seconds)
        
        logger.info(f"TWAP completed: {len(result)}/{slices} slices executed")
        return results

    except Exception as e:
        logger.error(f"TWAP order failed: {str(e)}")
        raise
