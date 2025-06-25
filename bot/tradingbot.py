from binance import Client
from binance.exceptions import BinanceAPIException
from config import Config
from logger import logger
from typing import Optional


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

            self.client.FUTURES_URL = creds['base_url']
            logger.debug(f"API endpoint: {self.client.FUTURES_URL}")

            self._validate_connection()
            logger.info("Trading bot initialized successfully")
        
        except Exception as e:
            logger.critical(f"Initialized failed: {str(e)}")
            raise
    
    def _validate_connection(self):
        """Verify API connectivity and account status"""
        try:
            response = self.client.futures_ping()
            logger.debug(f"API ping response: {response}")

            account_info = self.client.futures_account()
            logger.debug(f"Account info: {account_info}")

            balance = self.client.futures_account_balance()
            usdt_balance = next(
                (b for b in balance if b['asset'] == 'USDT'),
                None
            )

            if usdt_balance:
                logger.info(
                    f"Account balance: {usdt_balance['balance']} USDT | "
                    f"Available: {usdt_balance['availableBalance']} USDT"
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
                    exchange_info = self.client.futures_exchange_info()
                    print(f"Exchange info received: {type(exchange_info)}")
                    print(f"Keys in exchange_info: {list(exchange_info.keys())}")

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

    def place_order(self, symbol, side, order_type, quantity, **kwargs):
        """Core order placement method"""
        try:
            if not self.validate_symbol(symbol):
                return False, "Invalid symbol"
            
            if side not in ['BUY', 'SELL']:
                return False, "Invalid order side"
            
            if quantity <= 0:
                return False, "Quantity must be positive"
            
            logger.info(f"Placing {order_type} order: {side} {quantity} {symbol}")
            return True, "Order placement successful (simulated)"
        except Exception as e:
            logger.error(f"Order placement failed: {str(e)}")
            return False, str(e)
    
    def get_account_balance(self) -> dict:
        """Get current account balance with available margin"""
        try:
            balances = self.client.futures_account_balance()

            formatted = {}
            for asset in balances:
                if float(asset['balance']) > 0:
                    formatted[asset['asset']] = {
                        'balance': float(asset['balance']),
                        'available': float(asset['availableBalance']),
                        'margin': float(asset.get('crossUnPnl', 0))
                    }
            logger.info(f"Retrieved balances for {len(formatted)} assets")
            return formatted
        except BinanceAPIException as e:
            logger.error(f"Balance check failed: {e.status_code} {e.message}")
            raise RuntimeError("Failed to get balance")
    
    def get_open_orders(self, symbol: Optional[str] = None) -> list[dict]:
        """Get current open orders with detailed information"""
        try:
            params = {'symbol': symbol} if symbol else {}
            orders = self.client.futures_get_open_orders(**params)

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
                    'stopPrice': float(order.get('stopPrice', 0))
                })
            
            logger.info(f"Retrieved {len(formatted)} open orders")
            return formatted
        except BinanceAPIException as e:
            logger.error(f"Order check failed: {e.status_code} {e.message}")
            raise RuntimeError(f"Failed to get orders: {e.message}")
        except Exception as e:
            logger.error(f"Unexpected order error: {str(e)}")
            raise RuntimeError("Failed to get orders")
