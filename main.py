from bot.client import init_binance_client
from bot.orders import place_order
from bot.cli import get_user_input
from rich import print


if __name__ == "__main__":
    client = init_binance_client(testnet=True)
    symbol, side, order_type, quantity, price = get_user_input()
    response = place_order(client, symbol, side, order_type, quantity, price)
    print(f"\n[green]Order Response:[/green]\n{response}")
