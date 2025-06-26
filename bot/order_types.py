from binance.enums import *
from logger import logger
import time


class OrderTypes:
    @staticmethod
    def market_order(client, symbol, side, quantity):
        """Place a market order"""
        try:
            return client.futures_create_order(
                symbol=symbol,
                side = side,
                type=FUTURE_ORDER_TYPE_MARKET,
                quantity = str(quantity)
            )
        except Exception as e:
            logger.error(f"Market order failed: {str(e)}")
            raise

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
                    result = client.future_create_order(
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
