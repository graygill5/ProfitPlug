import sqlite3, os, json
from pathlib import Path
from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np
from contextlib import closing
from colorama import Fore, Style

# Getting the database path and store in DIR (may want to change depending on user) 
DATA_DIR = Path.home() / "Projects/ProfitPlug/.DB"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "portfolio.db"

# get the db path
def get_db_path() -> Path:
    return DB_PATH

# ================================================================================
# stock price related functions
def last_price(symbol):
    try:
        px = yf.Ticker(symbol).history(period="1d", interval="1m")["Close"].dropna() # get the close price at the end of each minute
        if len(px) == 0:
            px = yf.Ticker(symbol).history(period="5d")["Close"].dropna() # if there is no daily data it grabs the most recent 5 days
        return float(px.iloc[-1]) if len(px) else None
    except Exception:
        return None

def hist_close(symbol, days=200):
    try:
        return yf.Ticker(symbol).history(period=f"{max(days,60)}d")["Close"].dropna() # get the close price of the last minimun 60 days
    except Exception:
        return pd.Series(dtype=float)

def rsi(series, n=14):
    if len(series) < n+1: return np.nan
    delta = series.diff() # change in price

    up = np.where(delta>0, delta, 0.0)
    down = np.where(delta<0, -delta, 0.0)

    roll_up = pd.Series(up, index=series.index).rolling(n).mean() # calculate the mean of the rise
    roll_down = pd.Series(down, index=series.index).rolling(n).mean()

    rs = roll_up / (roll_down + 1e-9) # avoid dividing by 0
    return 100 - (100/(1+rs)).iloc[-1] # get as a percentage

def sma(series, n):
    if len(series) < n: return np.nan
    return series.rolling(n).mean().iloc[-1] # get the mean of the series and then grab the last one


# ================================================================================
# database set up
DDL = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS accounts (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  cash REAL NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS positions (
  account_id INTEGER NOT NULL,
  symbol TEXT NOT NULL,
  shares INTEGER NOT NULL,
  avg_cost REAL NOT NULL,
  PRIMARY KEY (account_id, symbol),
  FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trades (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  account_id INTEGER NOT NULL,
  time TEXT NOT NULL,
  action TEXT NOT NULL,   -- BUY/SELL
  symbol TEXT NOT NULL,
  shares INTEGER NOT NULL,
  price REAL NOT NULL,
  total REAL NOT NULL,
  realized_pnl REAL,
  FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  account_id INTEGER NOT NULL,
  time TEXT NOT NULL,
  equity REAL NOT NULL,
  cash REAL NOT NULL,
  positions_json TEXT NOT NULL,
  FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);
"""

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(starting_cash=100_000.0, account_name="Main"):
    with closing(get_conn()) as conn, conn:
        for stmt in DDL.strip().split(";\n\n"):
            if stmt.strip():
                conn.executescript(stmt + ";")
        # Ensure an account exists
        cur = conn.execute("SELECT id FROM accounts WHERE name=?", (account_name,))
        row = cur.fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO accounts (name, cash, created_at) VALUES (?, ?, ?)",
                (account_name, float(starting_cash), datetime.now().isoformat())
            )
        # Return account id
        acc_id = conn.execute("SELECT id FROM accounts WHERE name=?", (account_name,)).fetchone()["id"]
        return acc_id


# ================================================================================
# account engine
class PaperAccount:
    def __init__(self, account_id: int):
        self.account_id = account_id #initialize a user with database id

    # get user cash
    def _get_cash(self, conn):
        return float(conn.execute("SELECT cash FROM accounts WHERE id=?", (self.account_id,)).fetchone()["cash"])

    # set user cash 
    def _set_cash(self, conn, cash: float):
        conn.execute("UPDATE accounts SET cash=? WHERE id=?", (float(cash), self.account_id))

    def equity(self):
        with closing(get_conn()) as conn:
            cash = self._get_cash(conn)
            pv = 0.0
            for row in conn.execute("SELECT symbol, shares FROM positions WHERE account_id=?", (self.account_id,)):
                px = last_price(row["symbol"])
                if px: pv += row["shares"] * px
            return cash + pv

    def buy(self, sym, shares):
        sym = sym.upper()
        with closing(get_conn()) as conn, conn:
            price = last_price(sym)
            if price is None:
                print("✖ Couldn't fetch price."); return
            cost = price * shares
            cash = self._get_cash(conn)
            if cost > cash + 1e-9:
                print("✖ Not enough cash."); return
            # update cash
            self._set_cash(conn, cash - cost)
            # upsert position
            row = conn.execute("SELECT shares, avg_cost FROM positions WHERE account_id=? AND symbol=?",
                               (self.account_id, sym)).fetchone()
            if row:
                new_shares = row["shares"] + shares
                new_cost = (row["shares"]*row["avg_cost"] + cost) / new_shares
                conn.execute("UPDATE positions SET shares=?, avg_cost=? WHERE account_id=? AND symbol=?",
                             (new_shares, new_cost, self.account_id, sym))
            else:
                conn.execute("INSERT INTO positions (account_id, symbol, shares, avg_cost) VALUES (?, ?, ?, ?)",
                             (self.account_id, sym, shares, price))
            # log trade
            conn.execute("""INSERT INTO trades(account_id,time,action,symbol,shares,price,total,realized_pnl)
                            VALUES(?,?,?,?,?,?,?,NULL)""",
                         (self.account_id, datetime.now().isoformat(), "BUY", sym, shares, price, cost))
        print(f"✓ Bought {shares} {sym} @ ${price:.2f}")

    def sell(self, sym, shares):
        sym = sym.upper()
        with closing(get_conn()) as conn, conn:
            pos = conn.execute("SELECT shares, avg_cost FROM positions WHERE account_id=? AND symbol=?",
                               (self.account_id, sym)).fetchone()
            if not pos or pos["shares"] < shares:
                print("✖ Not enough shares."); return
            price = last_price(sym)
            if price is None:
                print("✖ Couldn't fetch price."); return
            revenue = price * shares
            realized = (price - pos["avg_cost"]) * shares
            # update cash
            cash = self._get_cash(conn)
            self._set_cash(conn, cash + revenue)
            # update position
            new_shares = pos["shares"] - shares
            if new_shares == 0:
                conn.execute("DELETE FROM positions WHERE account_id=? AND symbol=?", (self.account_id, sym))
            else:
                conn.execute("UPDATE positions SET shares=? WHERE account_id=? AND symbol=?",
                             (new_shares, self.account_id, sym))
            # log trade
            conn.execute("""INSERT INTO trades(account_id,time,action,symbol,shares,price,total,realized_pnl)
                            VALUES(?,?,?,?,?,?,?,?)""",
                         (self.account_id, datetime.now().isoformat(), "SELL", sym, shares, price, revenue, realized))
        print(f"✓ Sold {shares} {sym} @ ${price:.2f}  (Realized P/L: ${realized:.2f})")

    def portfolio(self):
        with closing(get_conn()) as conn:
            rows = []
            for r in conn.execute("SELECT symbol, shares, avg_cost FROM positions WHERE account_id=? ORDER BY symbol",
                                  (self.account_id,)):
                px = last_price(r["symbol"])
                if px is None: continue
                mv = px * r["shares"]
                u_pnl = (px - r["avg_cost"]) * r["shares"]
                rows.append([r["symbol"], r["shares"], r["avg_cost"], px, mv, u_pnl])
            df = pd.DataFrame(rows, columns=["Symbol","Shares","Avg Cost","Price","Mkt Value","Unrealized P/L"])
            cash = self._get_cash(conn)
        eq = self.equity()
        print(f"\n--- {Fore.LIGHTBLUE_EX}Portfolio{Style.RESET_ALL} ---")
        if df.empty: print("(no positions)")
        else: print(df.to_string(index=False, float_format=lambda x: f'{x:,.2f}'))
        print(f"Cash: ${cash:,.2f}   Equity: ${eq:,.2f}")

    def history(self):
        with closing(get_conn()) as conn:
            df = pd.read_sql_query(
                "SELECT time, action, symbol, shares, price, total, realized_pnl FROM trades "
                "WHERE account_id=? ORDER BY time", conn, params=(self.account_id,))
        print("\n--- Trade History ---")
        if df.empty: print("(no trades)")
        else: print(df.to_string(index=False))

    def reset(self, starting_cash=1_000_000.0):
        with closing(get_conn()) as conn, conn:
            conn.execute("DELETE FROM positions WHERE account_id=?", (self.account_id,))
            conn.execute("DELETE FROM trades WHERE account_id=?", (self.account_id,))
            conn.execute("UPDATE accounts SET cash=? WHERE id=?", (float(starting_cash), self.account_id))
        print("↺ Reset account.")

    def snapshot_on_exit(self):
        # Save an equity snapshot for performance tracking
        with closing(get_conn()) as conn, conn:
            # capture current positions as JSON
            pos = conn.execute(
                "SELECT symbol, shares, avg_cost FROM positions WHERE account_id=?", (self.account_id,)
            ).fetchall()
            pos_json = json.dumps([dict(r) for r in pos])
            cash = self._get_cash(conn)
            equity = self.equity()  # includes live prices
            conn.execute("""INSERT INTO snapshots(account_id,time,equity,cash,positions_json)
                            VALUES(?,?,?,?,?)""",
                         (self.account_id, datetime.now().isoformat(), float(equity), float(cash), pos_json))

# ----------------- “AI” market snapshot -----------------
def analyze_market():
    symbols = ["SPY","QQQ","IWM","TLT","DXY","^VIX"]
    info = {}
    for s in symbols:
        h = hist_close(s, 200)
        if h.empty: continue
        p = float(h.iloc[-1]); s20 = sma(h,20); s50 = sma(h,50); s200 = sma(h,200); r = rsi(h,14)
        trend = ("UP" if p>s50 else "DOWN") if not np.isnan(s50) else "—"
        cross = "bullish" if s20>s50 else ("bearish" if s20<s50 else "flat")
        info[s] = {"price": p, "rsi": r, "trend": trend, "cross": cross}
    def line(sym,name):
        d = info.get(sym)
        return f"{name}: (no data)" if not d else f"{name}: {d['trend']} | 20/50 {d['cross']} | RSI {d['rsi']:.0f} | Px {d['price']:.2f}"
    risk_on = (info.get("SPY",{}).get("trend")=="UP") and (info.get("^VIX",{}).get("price",30)<18)
    print("\n=== Market Snapshot ===")
    print(line("SPY","S&P 500")); print(line("QQQ","Nasdaq 100")); print(line("IWM","Russell 2000"))
    print(line("TLT","Long Bonds")); print(line("DXY","US Dollar")); print(line("^VIX","VIX"))
    print("\n— AI Take —")
    print("• Risk looks ON: Trend up + tame VIX" if risk_on else "• Caution: Trend/VIX mixed → be selective.")

def info():
    #declare more
    return

def show():
    #declare more
    return



# ================================================================================
# Help function
HELP = f"""
Commands:
  {Fore.LIGHTGREEN_EX}buy{Style.RESET_ALL}  TICKER SHARES       -> buy  (AAPL) 5
  {Fore.LIGHTRED_EX}sell{Style.RESET_ALL} TICKER SHARES       -> sell (MSFT) 2

  {Fore.LIGHTBLUE_EX}portfolio{Style.RESET_ALL}                -> show positions, P/L, cash, equity
  {Fore.LIGHTYELLOW_EX}history{Style.RESET_ALL}                  -> show trade history

  {Fore.LIGHTMAGENTA_EX}analyze{Style.RESET_ALL}                  -> market snapshot + AI take
  {Fore.LIGHTCYAN_EX}info{Style.RESET_ALL}                     -> get information pertaining to trading & investments
  \033[38;5;208mshow\033[0m                     -> get information pertaining to trading & investments

  reset                    -> wipe state back to $1M
  help                     -> show this help
  quit                     -> save snapshot and exit
"""