from multiprocessing import Process
from CmpECoinNetwDispatcher import CmpECoinNetwDispatcher
from simple_node import CmpECoinSimpleNode
from validator import CmpECoinValidatorNode
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from CmpECoinWallet import CmpECoinWallet
from threading import Thread 
import ecdsa
import time
import sys


from time import sleep
import os
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table
from rich.console import Console, RenderGroup, ConsoleOptions, ConsoleDimensions
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text


console = Console()

def make_layout() -> Layout:
    """Define the layout."""
    layout = Layout(name="root")
    layout.split_column(
        Layout(name="upper"),
        Layout(name="lower")
    )

    return layout


class Clock:
    """Renders the time in the center of the screen."""

    def __rich__(self) -> Text:
        table = Table()
        table.add_column("Node")
        table.add_column("Wallet")
        table.add_row(f"{sys.argv[1]}", f" {coin.wallet.getCurrentBalance()}")
        return Panel(table)

try:
    PKs= ['20bf96d77dd5bfbdff30b099e9c5bbfcd49888008aee47b4e6d91ef95a1b59a6', 'b4521501b02417c2bf8036b3993c5728ca08e6adf40f2fd895fecc30083da7fd', 'b5070a4802bc7f572fcc9dfa5cb7c85c0e775e54b090272415715e4156fa7bcb']

    sk = SigningKey.from_string(bytes.fromhex(PKs[int(sys.argv[1])]), curve=ecdsa.SECP256k1)
    vk = sk.verifying_key

    PKsInNetwork = []
    for i in range(0,3):
        skk = SigningKey.from_string(bytes.fromhex(PKs[i]), curve=ecdsa.SECP256k1)
        PKsInNetwork.append(skk.verifying_key)


    wallet = CmpECoinWallet()
    wallet.privateKey = sk
    wallet.publicKey = vk
    meanTransactionInterDuration = 30
    meanTransactionAmount = 10

    coin = CmpECoinSimpleNode(wallet, meanTransactionInterDuration, meanTransactionAmount,  PKsInNetwork)

    

    
    table = Table()
    table.add_column("Node")
    table.add_column("Wallet")
    table.add_row(f"{sys.argv[1]}", f" {coin.blockChain.getBalanceOf(vk)}")
    p= Panel(table)

    """layout = make_layout()
    layout["lower"].update(Header())"""

    with Live(p, console=console,  redirect_stderr=True) as live:
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

except KeyboardInterrupt:
    print('Interrupted')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)