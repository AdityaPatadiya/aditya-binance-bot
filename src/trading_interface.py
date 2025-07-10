import sys
import logging
from typing import Callable, TypeVar
from bot import TradingBot
from logger import logger

T = TypeVar('T')


class TradingInterface:
    def __init__(self) -> None:
        self.bot = TradingBot()
        logger.info("Trading interface initialized")

    def run(self):
        """Main interactive loop"""
        while True:
            try:
                self._clear_screen()
                self._display_header()
                choice = self._get_menu_choice()

                if choice == "1":
                    self._place_order_flow()
                elif choice == "2":
                    self._check_balance()
                elif choice == "3":
                    self._view_open_orders()
                elif choice == "4":
                    self._view_trade_history()
                elif choice == "5":
                    self._cancel_order_flow()
                elif choice == "6":
                    logger.info("Shutting down trading bot")
                    print("\nGoodbye!")
                    break
                else:
                    print("Invalid choice, please try again")

                input("\n Press Enter to continue...")
            except KeyboardInterrupt:
                print("\nOperation cancelled by user")
                logging.warning("User interrupted operation")
            except Exception as e:
                logger.error(f"Interface error: {str(e)}")
                print(f"\nError: {str(e)}")
                input("Press Enter to continue...")

    def _clear_screen(self):
        """Clear terminal screen"""
        print("\033[H\033[J", end="")

    def _display_header(self):
        """Display application header"""
        print("┌────────────────────────────────────────────┐")
        print("│        BINANCE FUTURES TRADING BOT         │")
        print("├────────────────────────────────────────────┤")
        print("│ 1. Place New Order                         │")
        print("│ 2. Check Account Balance                   │")
        print("│ 3. View Open Orders                        │")
        print("│ 4. View Trade History                      │")
        print("│ 5. Cancel Order                            │")
        print("│ 6. Exit                                    │")
        print("└────────────────────────────────────────────┘")

    def _get_menu_choice(self) -> str:
        """Get validate menu choice"""
        while True:
            choice = input("\nEnter your choice (1-6): ").strip()
            if choice in("1", "2", "3", "4", "5", "6"):
                return choice
            print("Invalid input. Please enter 1-6")

    def _place_order_flow(self):
        """Complete order placement workflow"""
        print("\n--- ORDER PLACEMENT--------------------------")

        symbol = None
        while True:
            try:
                raw_input = input("Enter trading pair (e.g. BTCUSDT): ").strip()
                if not raw_input:
                    print("Symbol cannot be empty")
                    continue

                symbol_candidate = raw_input.upper()
                try:
                    if self.bot.validate_symbol(symbol_candidate):
                        symbol = symbol_candidate
                        break
                    print(f"Invalid symbol. Try example: BTCUSDT, ETHUSDT, BNBUSDT")
                except RuntimeError as e:
                    print(f"Connection error: {str(e)}")
                    print("Please check your API keys and internet connection")
                except Exception as e:
                    print(f"Validating error: {str(e)}")
                    print("Please try again")
                    return
            except KeyboardInterrupt:
                print("\n Operation cancelled")
                return

        # get order type
        order_type = self._get_valid_input(
            prompt="Order type (MARKET/LIMIT/STOP_LIMIT/OCO/TWAP): ",
            validator=lambda x: x.upper() in ("MARKET", "LIMIT", "STOP_LIMIT", "OCO", "TWAP"),
            error_msg="Invalid order type. Choose MARKET/LIMIT/STOP_LIMIT/OCO/TWAP"
        ).upper()
        params = {}

        # get side
        side = self._get_valid_input(
            prompt="Side (BUY/SELL): ",
            validator=lambda x: x.upper() in ("BUY", "SELL"),
            error_msg="Invalid side. Choose BUY or SELL"
        ).upper()

        # get quantity
        quantity = float(self._get_valid_input(
            prompt="Enter quantity: ",
            validator=lambda x: x.replace('.', '', 1).isdigit() and float(x) > 0,
            error_msg="Quantity must be a positive number"
        ))

        params = {}
        current_price = None
        if order_type in ("LIMIT", "STOP_LIMIT", "OCO"):
            try:
                ticker = self.bot.client.futures_symbol_ticker(symbol=symbol)
                current_price = float(ticker['price'])
                print(f"Current market price: {current_price:.2f}")
            except Exception as e:
                print(f"Couldn't get current price: {str(e)}")

        if order_type in ("LIMIT", "STOP_LIMIT", "OCO"):
            params['price'] = float(self._get_valid_input(
                prompt="Enter limit price (actual order execution price): ",
                validator=lambda x: x.replace('.', '', 1).isdigit() and float(x) > 0,
                error_msg="Price must be a positive number"
            ))

            if order_type == "STOP_LIMIT":
                params['stop_price'] = float(self._get_valid_input(
                    prompt="Enter stop price (trigger price): ",
                    validator=lambda x: x.replace('.', '', 1).isdigit() and float(x) > 0,
                    error_msg="Stop price must be a positive number"
                ))

            if order_type in ("LIMIT", "STOP_LIMIT") and current_price is not None:
                if abs(params['price'] - current_price) > current_price * 0.2:
                    if not self._get_yes_no("Warning: Price is >20% away from market. Continue? (y/n): "):
                        print("Order cancelled")
                        return

        if order_type == 'OCO':
            try:
                ticker = self.bot.client.futures_symbol_ticker(symbol=symbol)
                current_price = float(ticker['price'])
                print(f"Current markt price: {current_price:.2f}")
            except Exception as e:
                print(f"Couldn't get current price: {str(e)}")
                return

            params['price'] = float(self._get_valid_input(
                prompt = "Enter take-profit price: ",
                validator = lambda x: x.replace('.', '', 1).isdigit() and float(x) > 0,
                error_msg = "Price must be a positive number"
            ))
            
            while True:
                params['stop_price'] = float(self._get_valid_input(
                    prompt="Enter stop price: ",
                    validator=lambda x: x.replace('.', '', 1).isdigit() and float(x) > 0,
                    error_msg = "Stop price must be a positive number"
                ))

                if side == 'BUY' and params['stop_price'] > current_price:
                    print("For BUY position, stop price must be BELOW current price")
                elif side == "SELL" and params['stop_price'] < current_price:
                    print("For SELL position, stop price must be ABOVE current price")
                else:
                    break

            params['stop_limit_price'] = float(self._get_valid_input(
                prompt = "Enter the stop-limit execution price (MUST be below stop price for BUY): " if side == 'BUY' else "Enter the stop-limit execution price (MUST be above stop price for SELL): ",
                validator = lambda x: x.replace('.', '', 1).isdigit() and float(x) > 1,
                error_msg = "Stop-limit price must be a positive number"
            ))

        if order_type == 'TWAP':
            params['duration_min'] = float(self._get_valid_input(
                prompt = "Enter duration in minutes: ",
                validator = lambda x: x.replace('.', '', 1).isdigit() and float(x) > 0,
                error_msg = "Duration must be a positive number"
            ))

            params['slices'] = int(self._get_valid_input(
                prompt = "Enter number of slices (4-20): ",
                validator = lambda x: x.isdigit() and 4 <= int(x) <= 20,
                error_msg = "Slices must be integer between 4-20"
            ))

        print("\n┌─────────────── ORDER SUMMARY ─────────────────┐")
        print(f"│ Symbol: {symbol:>30}        │")
        print(f"│ Type: {order_type:>31}      │")
        print(f"│ Side: {side:>32}            │")
        print(f"│ Quantity: {quantity:>26.4f}    │")
        
        if order_type == "TWAP":
            print(f"| {'Duration Min':<15}: {params['duration_min']:>18.2f}  |")
            print(f"| {'Slices':<15}: {params['slices']:>18}  |")
        for k, v in params.items():
            display_name = k.replace('_', ' ').title()
            if k == "price":
                display_name = "Take-Profit Price"
            elif k == "stop_price":
                display_name = "Stop Trigger Price"
            elif k == "stop_limit_price":
                display_name = "Stop Limit Price"
            print(f"| {display_name:<15}: {v:>18.2f}  |")
        print("└─────────────────────────────────────────────┘")

        if self._get_yes_no("Confirm order placement? (y/n): "):
            success, response = self.bot.place_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                **params
            )
            if success:
                if order_type == "TWAP":
                    if response is None:
                        print("\nTWAP failed: No slices executed")
                    elif isinstance(response, list):
                        logger.info(type(response))
                        logger.info(response)
                        order_ids = [str(r.get('orderId', 'N/A')) for r in response]
                        print(f"\nTWAP partially executed! {len(response)} slices completed")
                        print(f"Slice IDs: {', '.join(order_ids)}")
                    else:
                        print(f"\nUnexpected TWAP response: {response}")
                elif order_type == "OCO":
                    order_ids = [str(r.get('orderID', 'N/A')) for r in response]
                    print(f"\nOCO order placed successfully! Order IDs: {', '.join(order_ids)}")

                    print("\nOrder Details:")
                    for i, order in enumerate(response):
                        order_type_desc = "Take-Profit Limit" if i == 0 else "Stop-Loss"
                        print(f"{order_type_desc} Order: {order_ids[i]}")
                elif order_type == "MARKET" or order_type == "LIMIT" or order_type == "STOP_LIMIT":
                    logger.info("Order Placed Successfully!")
                    logger.info(f"Order ID: {response.get('orderId')}")

            else:
                order_id = response.get('orderID', 'N/A')
                print(f"\nOrder placed successfully! ID: {order_id}")

                if order_type == "MARKET" and isinstance(response, dict) and 'fills' in response:
                    print("\nExecution Details:")
                    for fill in response['fills']:
                        print(f"- Price: {fill['price']} | Qty: {fill['qty']}")

    def _get_valid_input(self, prompt: str, validator: Callable[[str], bool], error_msg: str) -> str:
        """Get validated user input with retry"""
        while True:
            try:
                user_input = input(prompt).strip()
                if validator(user_input if prompt.lower() != "enter trading pair" else user_input.upper()):
                    return user_input.upper() if "trading pair" in prompt.lower() else user_input
                print(error_msg)
            except Exception as e:
                print(f"Input error: {str(e)}")
                raise
    
    def _get_yes_no(self, prompt: str) -> bool:
        """Get yes/no confirmation"""
        while True:
            response = input(prompt).strip().lower()
            if response in ('y', 'yes'):
                return True
            if response in ('n', 'no'):
                return False
            print("Please enter 'y'or 'n'")
    
    def _check_balance(self):
        """Display account balance for all assets"""
        print("\n------ ACCOUNT BALANCE ----------------------")
        try:
            balance = self.bot.get_account_balance()

            print(f"\n{'Asset':<8} {'Balance':>12} {'Available':>12} {'Margin':>12}")
            print("-" * 50)
            for asset, data in balance.items():
                print(f"{asset:<8} {data['balance']:>12.4f} {data['available']:>12.4f} {data['margin']:>12.4f}")

            logger.info(f"Balance checked: {balance}")
        except Exception as e:
            print(f"\nError fetching balance: {str(e)}")
            logger.error(f"Balance check failed: {str(e)}")
    
    def _view_open_orders(self):
        """Display open orders with more details"""
        print("\n── OPEN ORDERS ────────────────────────────")
        try:
            orders = self.bot.get_open_orders()
            if not orders:
                print("\nNo open orders found")
                return

            print(f"\n{'ID':<12} {'Symbol':<8} {'Side':<6} {'Type':<10} {'Qty':<10} {'Price':<10} {'Stop Price':<10}")
            print("-" * 70)
            for order in orders[:10]:  # Show first 10 orders
                print(f"{order['orderId']:<12} {order['symbol']:<8} {order['side']:<6} "
                      f"{order['type']:<10} {order['origQty']:<10.4f} "
                      f"{order['price']:<10.2f} {order['stopPrice']:<10.2f}")

            logger.info(f"Viewed {len(orders)} open orders")
        except Exception as e:
            print(f"\n Error fetching orders: {str(e)}")
            logger.error(f"Open orders check failed: {str(e)}")

    def _view_trade_history(self):
        """Display recent trade history"""
        print("\n----------TRADE HISTORY----------------------")
        try:
            symbol = input("enter trading pair (e.g. BTCUSDT): ").strip().upper()
            if not symbol:
                print("Symbol cannot empty")
                return
            
            if not self.bot.validate_symbol(symbol):
                print("Invalid symbol")
                return

            trades = self.bot.get_trade_history(symbol)
            if not trades:
                print(f"\nNo trades found for {symbol}")
                return
            
            print(f"\n{'Time':<25} {'Side': <6} {'QTY': <10} {'PnL': <10}")
            print("-" * 70)
            for trade in trades:
                print(f"{trade['time']:<25} {trade['side']:<6} "
                      f"{trade['qty']:<10.4f} {trade['price']:10.2f} "
                      f"{trade['realizedPnl']:<10.4f}")
            logger.info(f"Viewed trade history for {symbol}")
        except Exception as e:
            print(f"\nError fetching trade history: {str(e)}")
            logger.error(f"Trade history failed: {str(e)}")
    
    def _cancel_order_flow(self):
        """Cancel an open order"""
        print("\n------------CANCEL ORDER----------------------")
        try:
            symbol = input("Enter trading pair (e.g. BTCUSDT): ").strip().upper()
            if not symbol:
                print("Symbol cannot be empty")
                return

            if not self.bot.validate_symbol(symbol):
                print("Invalid symbol")
                return

            order_id = input("Enter order ID to cancel: ").strip()
            if not order_id.isdigit():
                print("Invalid order ID")
                return

            if self._get_yes_no(f"Confirm cancel order {order_id} on {symbol}? (y/n): "):
                success, response = self.bot.cancel_order(symbol, int(order_id))
                if success:
                    print(f"\n Order {order_id} canceled successfully!")
                else:
                    print(f"\nCancel failed: {response}")
        except Exception as e:
            print(f"\nError canceling order: {str(e)}")
            logger.error(f"Cancel order failed: {str(e)}")


if __name__ == "__main__":
    try:
        logger.info("\n" + "-" * 100)
        logger.info("Starting trading interface")
        interface = TradingInterface()
        interface.run()
    except Exception as e:
        logger.critical(f"Application crashed: {str(e)}")
        print(f"\nCritical error: {str(e)}")
        sys.exit(1)
