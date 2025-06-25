import sys
import logging
from typing import Callable, TypeVar
from tradingbot import TradingBot
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
        print("│ 4. Exit                                    │")
        print("└────────────────────────────────────────────┘")

    def _get_menu_choice(self) -> str:
        """Get validate menu choice"""
        while True:
            choice = input("\nEnter your choice (1-4): ").strip()
            if choice in("1", "2", "3", "4"):
                return choice
            print("Invalid input. Please enter 1-4")

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
            prompt="Order type (MARKET/LIMIT/STOP_LIMIT): ",
            validator=lambda x: x.upper() in ("MARKET", "LIMIT", "STOP_LIMIT"),
            error_msg="Invalid order type. Choose MARKET/LIMIT/STOP_LIMIT"
        ).upper()

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

        # additional parameters
        params = {}
        if order_type in ("LIMIT", "STOP_LIMIT"):
            params['price'] = float(self._get_valid_input(
                prompt = "Enter proce: ",
                validator = lambda x: x.replace('.', '', 1).isdigit() and float(x) > 0,
                error_msg = "Price must be a positive number"
            ))
        
        if order_type == "STOP_LIMIT":
            params['stop_price'] = float(self._get_valid_input(
                prompt = "Enter stop price: ",
                validator = lambda x: x.replace('.', '', 1).isdigit() and float(x) > 0,
                error_msg = "Stop price must be a positive number"
            ))
        
        print("\n┌─────────────── ORDER SUMMARY ───────────────┐")
        print(f"│ Symbol: {symbol:>30} │")
        print(f"│ Type: {order_type:>31} │")
        print(f"│ Side: {side:>32} │")
        print(f"│ Quantity: {quantity:>26} │")
        for k, v in params.items():
            print(f"│ {k.replace('_', ' ').title():<15}: {v:>18} │")
        print("└─────────────────────────────────────────────┘")

        if self._get_yes_no("Confirm order placement? (y/n): "):
            success, response = self.bot.place_order(
                symbol = symbol,
                side = side,
                order_type = order_type,
                quantity = quantity,
                **params
            )
            if success:
                order_id = response.get('orderId') if isinstance(response, dict) else None
                if order_id:
                    print(f"Order placed successfully! ID: {order_id}")
                else:
                    print("Order placed successfully!")
                logger.info(f"Order placed: {response}")
            else:
                print(f"\nOrder failed: {response}")
                logger.error(f"Order failed: {response}")

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
        """Display account balance"""
        print("\n------ACCOUNT BALANCE----------------------")
        try:
            balance = self.bot.get_account_balance()
            usdt = balance.get('USDT', {})

            print(f"\n{'Asset':<10} {'Balance':>15} {'Available':>15}")
            print("-" * 45)
            print(f"{'USDT':<10} {float(usdt.get('balance', 0)):>15.4f} {float(usdt.get('available', 0)):>15.4f}")

            logger.info(f"Balance checked: {balance}")
        except Exception as e:
            print(f"\nError fetching balance: {str(e)}")
            logger.error(f"Balance check failed: {str(e)}")
    
    def _view_open_orders(self):
        """Display open orders"""
        print("\n── OPEN ORDERS ────────────────────────────")
        try:
            orders = self.bot.get_open_orders()
            if not orders:
                print("\nNo open orders found")
                return

            print(f"\n{'ID':<15} {'Symbol':<10} {'Side':<8} {'Type':<12} {'Qty':<12} {'Price':<12}")
            print("-" * 70)
            for order in orders[:10]:  # Show first 10 orders
                print(f"{order['orderId']:<15} {order['symbol']:<10} {order['side']:<8} "
                      f"{order['type']:<12} {float(order['origQty']):<12.4f} "
                      f"{float(order.get('price', 0)):<12.4f}")

            logger.info(f"Viewed {len(orders)} open orders")
        except Exception as e:
            print(f"\n❌ Error fetching orders: {str(e)}")
            logger.error(f"Open orders check failed: {str(e)}")


if __name__ == "__main__":
    try:
        logger.info("Starting trading interface")
        interface = TradingInterface()
        interface.run()
    except Exception as e:
        logger.critical(f"Application crashed: {str(e)}")
        print(f"\nCritical error: {str(e)}")
        sys.exit(1)
