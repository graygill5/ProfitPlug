from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_market_updates():
    # placeholder data for now
    return {
        "title": "Market Updates",
        "updates": [
            "S&P 500: +0.5%",
            "TSLA: +1.2%",
            "AAPL: -0.3%"
        ]
    }
