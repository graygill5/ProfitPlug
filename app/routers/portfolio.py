from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_portfolio():
    # fake portfolio until we wire real data
    return {
        "title": "Your Portfolio",
        "holdings": [
            {"symbol": "AAPL", "shares": 10, "price": 225.12},
            {"symbol": "TSLA", "shares": 2, "price": 238.67}
        ]
    }
