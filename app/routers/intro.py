from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_intro():
    return {
        "title": "Intro to Finances",
        "sections": [
            {
                "id": "credit-cards",
                "title": "Credit Cards 101",
                "items": [
                    {
                        "headline": "How credit cards work",
                        "blurb": "You borrow money up to a limit and pay it back monthly. Pay the full statement balance to avoid interest."
                    },
                    {
                        "headline": "APR & interest",
                        "blurb": "APR is the yearly interest rate if you carry a balance. 20% APR ≈ ~1.67% per month."
                    },
                    {
                        "headline": "Statement vs. current balance",
                        "blurb": "Statement balance is what you owe for last cycle. Current balance includes new charges after the statement."
                    },
                    {
                        "headline": "Utilization",
                        "blurb": "Keep credit usage under ~10–30% of your limit for better scores. E.g., $300 of $3,000 = 10%."
                    },
                    {
                        "headline": "Rewards",
                        "blurb": "Points/cashback are nice, but interest wipes them out. Never carry a balance for points."
                    },
                    {
                        "headline": "Fees",
                        "blurb": "Watch for annual fees, late fees, foreign transaction fees. Many cards waive annual fees in year 1."
                    }
                ]
            },
            {
                "id": "stock-market-basics",
                "title": "Stock Market Basics",
                "items": [
                    {
                        "headline": "What stocks are",
                        "blurb": "A stock is partial ownership of a company. Price reflects expectations of future profits and risk."
                    },
                    {
                        "headline": "Indexes",
                        "blurb": "S&P 500, Dow, and Nasdaq are baskets of companies. They help you track the market’s overall direction."
                    },
                    {
                        "headline": "ETFs vs. single stocks",
                        "blurb": "ETFs are bundles (diversified, lower risk). Single stocks can swing more—higher risk, higher potential."
                    },
                    {
                        "headline": "Dividends",
                        "blurb": "Some companies pay cash to shareholders. Reinvesting dividends compounds growth over time."
                    },
                    {
                        "headline": "Time in market > timing",
                        "blurb": "Consistent investing and a long horizon usually beats trying to guess short-term moves."
                    }
                ]
            },
            {
                "id": "buzzwords",
                "title": "Buzzword Decoder",
                "items": [
                    {"term": "Bull/Bear Market", "blurb": "Bull = rising prices/optimism. Bear = falling prices/pessimism."},
                    {"term": "Market Cap", "blurb": "Company size = share price × shares outstanding."},
                    {"term": "P/E Ratio", "blurb": "Price divided by earnings per share. Rough sense of how ‘expensive’ a stock is."},
                    {"term": "Yield", "blurb": "Annual dividend ÷ stock price. A 3% yield pays $3 per year on $100 stock."},
                    {"term": "Volatility", "blurb": "How much price wiggles around. More volatility = bigger swings."},
                    {"term": "Liquidity", "blurb": "How easy it is to buy/sell without moving the price much."},
                    {"term": "Diversification", "blurb": "Don’t put all eggs in one basket—spread risk across assets."},
                    {"term": "Expense Ratio", "blurb": "Annual fee for ETFs/mutual funds. Lower is generally better."},
                    {"term": "Limit vs. Market Order", "blurb": "Market = buy now at prevailing price. Limit = set the max/min price you’ll accept."},
                    {"term": "Recession/Inflation", "blurb": "Recession = shrinking economy. Inflation = rising prices; erodes purchasing power."}
                ]
            }
        ]
    }