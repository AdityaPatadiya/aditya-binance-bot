from rich.prompt import Prompt
from rich import print


def get_user_input():
    symbol = Prompt.ask("[cyan]Enter Symbol[/] (e.g., BTCUSDT)").upper()
    side = Prompt.ask("[cyan]Enter side[/] (BUY/SELL)").upper()
    order_type = Prompt.ask("[cyan]Order Type[/] (MARKET/LIMIT/STOP_MARKET)").upper()
    quantity = float(Prompt.ask("[cyan]Quantity[/]"))
    price = None
    if order_type == "LIMIT":
        price = float(Prompt.ask("[cyan]Limit Price[/]"))
    
    return symbol, side, order_type, quantity, price
