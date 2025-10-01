from binance import Client
from binance.exceptions import BinanceAPIException
from config import Config
from logger import logger
from typing import Optional, Any, Tuple
import limit_orders
import market_orders
from advanced import stop_limit, oco, twap


class TradingBot:
    def __init__(self) -> None:
        """Initialize trading bot with API client"""
        try:
            self.config = Config()
            logger.info("Configuration loaded")

            creds = self.config.credentials
            self.client = Client(
                api_key=creds['api_key'],
                api_secret=creds['api_secret'],
                testnet=True
            )

            # self.client.FUTURES_URL = creds['base_url']
            # logger.debug(f"API endpoint: {self.client.FUTURES_URL}")

            logger.info("Trading bot initialized successfully")
            self._validate_connection()

        except Exception as e:
            logger.critical(f"Initialized failed: {str(e)}")
            raise

    def _validate_connection(self):
        """Verify API connectivity and account status"""
        try:
            response = self.client.get_account()
            logger.debug("API connection is successfully.")

            # account_info = self.client.futures_account()
            # logger.debug(f"Account info: {account_info}")


            balance = response["balances"]
            usdt_balance = next(
                (b for b in balance if b['asset'] == 'USDT'),
                None
            )

            if usdt_balance and float(usdt_balance['free']) > 0:
                logger.info(
                    f"Account balance: {usdt_balance['free']} USDT free | "
                    f"locked: {usdt_balance['locked']} USDT"
                )
            else:
                logger.warning("USDT balance not found")

            logger.info("API connection validated")

        except BinanceAPIException as api_error:
            logger.error(
                f"API error {api_error.status_code}: {api_error.message}"
            )
            raise
        except Exception as e:
            logger.error(f"Connection validation failed: {str(e)}")
            raise

    def validate_symbol(self, symbol:str):
        """Validate trading symbol format and availability"""
        try:
            if not symbol.isupper() or ' ' in symbol or not any(c.isalpha() for c in symbol):
                logger.warning(f"Invalid symbol format: {symbol}")
                return False

            if not hasattr(self, '_valid_symbols'):
                try:
                    exchange_info = self.client.get_exchange_info()

                    if 'symbols' not in exchange_info:
                        logger.error("'symbols' key missing in exchange ingo")
                        raise RuntimeError("Invalid API response format")

                    self._valid_symbols = {s['symbol'] for s in exchange_info['symbols']}
                    logger.debug(f"Loaded {len(self._valid_symbols)} valid symbols")
                except BinanceAPIException as e:
                    logger.error(f"API error loading symbols: {e.status_code} {e.message}")
                    raise RuntimeError("Unable to fetch symbol list")
                except Exception as e:
                    logger.error(f"Error loading symbols {str(e)}")
                    raise RuntimeError("Symbol list unavailable")

            if symbol in self._valid_symbols:
                return True

            logger.warning(f"Invalid symbol: {symbol}. Valid example: {", ".join(sorted(self._valid_symbols)[:3])}")
            return False
        except RuntimeError:
            raise
        except Exception as e:
            logger.error(f"Symbol validation error: {str(e)}")
            return False

    def place_order(self, symbol, side, order_type, quantity, **kwargs) -> Tuple[bool, Any]:
        """Core order placement method"""
        quantity = float(quantity)
        try:
            if not self.validate_symbol(symbol):
                return False, "Invalid symbol"

            if side not in ['BUY', 'SELL']:
                return False, "Invalid order side"

            if quantity <= 0:
                return False, "Quantity must be positive"

            logger.info(f"Placing {order_type} order: {side} {quantity} {symbol}")
            str_kwargs = {k: str(v) for k, v in kwargs.items()}

            if order_type == "MARKET":
                result = market_orders.market_order(
                    self.client, symbol, side, quantity
                )
            elif order_type == "LIMIT":
                if 'price' not in kwargs:
                    return False, "Price is required for limitorders"
                result = limit_orders.limit_order(
                    self.client, symbol, side, quantity, str_kwargs['price']
                )
            elif order_type == "STOP_LIMIT":
                if 'price' not in kwargs or 'stop_price' not in kwargs:
                    return False, "Price and stop_price are required for stop-limit orders"
                result = stop_limit.stop_limit_order(
                    self.client, symbol, side, quantity, kwargs['price'], kwargs['stop_price']
                )
            elif order_type == "OCO":
                if 'price' not in kwargs or 'stop_price' not in kwargs or 'stop_limit_price' not in kwargs:
                    return False, "Price, stop_price, and stop_limit_price are required for OCO orders"
                result = oco.oco_order(
                    self.client, symbol, side, quantity, kwargs['price'], kwargs['stop_price'], kwargs['stop_limit_price']
                )
            elif order_type == "TWAP":
                if 'duration_min' not in kwargs:
                    return False, "Missing 'duration_min' for TWAP order"
                try:
                    ticker = self.client.get_symbol_ticker(symbol=symbol)
                    price = float(ticker['price'])

                    slice_qty = quantity / kwargs.get('slices', 4)
                    required_total = slice_qty * price

                    balance = self.get_account_balance()
                    usdt_balance = balance.get('USDT', {}).get('available', 0)

                    if usdt_balance < required_total:
                        return False, (
                            f"Insufficient margin. Need ${required_total:.2f}"
                            f"for smallest slice, available ${usdt_balance:.2f}"
                        )
                except Exception as e:
                    logger.error(f"Margin check failed: {str(e)}")
                    return False, "Margin verification error"
                result = twap.twap_order(
                    self.client, symbol, side, quantity, kwargs['duration_min'], kwargs.get('slices', 4)
                )
            else:
                return False, f"unsupported order type: {order_type}"

            return True, result
        except BinanceAPIException as e:
            error = f"API Error (code {e.status_code}): {e.message}"
            logger.error(error)
            return False, error
        except Exception as e:
            logger.error(f"Order placement failed: {str(e)}")
            return False, str(e)

    def get_account_balance(self) -> dict:
        """Get current account balance with available margin"""
        try:
            account = self.client.get_account()
            balances = account['balances']

            formatted = {}
            for asset in balances:
                free = float(asset['free'])
                locked = float(asset['locked'])
                total = free + locked
                if total > 0:
                    formatted[asset['asset']] = {
                        'free': free,
                        'locked': locked,
                        'total': total
                    }
            logger.info(f"Retrieved balances for {len(formatted)} assets")
            return formatted
        except BinanceAPIException as e:
            logger.error(f"Balance check failed: {e.status_code} {e.message}")
            raise RuntimeError(f"Failed to get balance {e.message}")
        except Exception as e:
            logger.error(f"Unexpected balance error: {str(e)}")
            raise RuntimeError("Failed to get balance")

    def get_open_orders(self, symbol: Optional[str] = None) -> list[dict]:
        """Get current open orders with detailed information"""
        try:
            if symbol:
                orders = self.client.get_open_orders(symbol=symbol)
            else:
                orders = self.client.get_open_orders()

            formatted = []
            for order in orders:
                formatted.append({
                    'orderId': order['orderId'],
                    'symbol': order['symbol'],
                    'side': order['side'],
                    'type': order['type'],
                    'origQty': float(order['origQty']),
                    'price': float(order.get('price', 0)),
                    'status': order['status'],
                    'time': order['time'],
                })

            logger.info(f"Retrieved {len(formatted)} open orders")
            return formatted
        except BinanceAPIException as e:
            logger.error(f"Order check failed: {e.status_code} {e.message}")
            raise RuntimeError(f"Failed to get orders: {e.message}")
        except Exception as e:
            logger.error(f"Unexpected order error: {str(e)}")
            raise RuntimeError("Failed to get orders")

    def get_trade_history(self, symbol: str, limit: int = 10) -> list[dict]:
        """Get recent trades for a symbol"""
        try:
            trades = self.client.get_my_trades(symbol=symbol)
            trades = trades[-limit:]

            formatted = []
            for trade in trades:
                formatted.append({
                    'id': trade['id'],
                    'symbol': trade['symbol'],
                    'side': trade['isBuyer'] and 'BUY' or 'SELL',
                    'qty': float(trade['qty']),
                    'price': float(trade['price']),
                    'commission': f"{trade['commission']} {trade['commissionAsset']}",
                    'time': trade['time']
                })

            logger.info(f"Retrieved {len(formatted)} trades for {symbol}")
            return formatted
        except BinanceAPIException as e:
            logger.error(f"Trade history error: {e.status_code} {e.message}")
            raise RuntimeError(f"Failed to get trade history: {e.message}")
        except Exception as e:
            logger.error(f"Unexpected trade error: {str(e)}")
            raise RuntimeError("Failed to get trade history")

    def cancel_order(self, symbol: str, order_id: int) -> Tuple[bool, Any]:
        """Cancel an open order"""
        try:
            result = self.client.cancel_order(
                symbol=symbol,
                orderId=order_id
            )
            logger.info(f"Canceled order {order_id} on {symbol}")
            return True, result
        except BinanceAPIException as e:
            error = f"Cancel failed: {e.status_code} {e.message}"
            logger.error(error)
            return False, error
        except Exception as e:
            error = f"Cancel error: {str(e)}"
            logger.error(error)
            return False, error

    def get_max_position(self, symbol, leverage=1):
        """Calculate maximum position size based on available balance"""
        try:
            balance = self.get_account_balance()
            usdt_balance = balance.get('USDT', {}).get('free', 0)

            if not usdt_balance:
                return 0

            ticker = self.client.get_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])

            return (usdt_balance * leverage) / price
        except Exception as e:
            return 0
