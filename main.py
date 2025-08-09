# main.py
from colorama import Fore, Style, init as colorama_init
from funcs import (
    init_db, PaperAccount, analyze_market, HELP,
    get_db_path
)

def main():
    colorama_init(autoreset=False)  # good practice on Windows
    acc_id = init_db(starting_cash=1_000_000.0, account_name="Main")
    acct = PaperAccount(acc_id)

    print(
        f"{Fore.RED}{Style.BRIGHT}ProfitPlug: {Style.RESET_ALL}"
        f"Your data is stored here -> "
        f"{Fore.BLACK}{Style.DIM}{get_db_path()}{Style.RESET_ALL}"
    )
    acct.portfolio()
    print(HELP)

    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaving & exiting...")
            acct.snapshot_on_exit()
            break
        if not raw:
            continue

        parts = raw.split()
        cmd = parts[0].lower()

        if cmd == "buy" and len(parts) == 3:
            acct.buy(parts[1], int(parts[2]))
        elif cmd == "sell" and len(parts) == 3:
            acct.sell(parts[1], int(parts[2]))
        elif cmd == "portfolio":
            acct.portfolio()
        elif cmd == "history":
            acct.history()
        elif cmd == "analyze":
            analyze_market()
        elif cmd == "reset":
            acct.reset()
        elif cmd in ("quit", "exit"):
            print("Saving & exiting...")
            acct.snapshot_on_exit()
            break
        elif cmd == "help":
            print(HELP)
        else:
            print("Unknown command. Type 'help'.")

if __name__ == "__main__":
    main()