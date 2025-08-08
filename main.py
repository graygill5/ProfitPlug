from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to ProfitPlug API"}

@app.get("/stocks/{symbol}")
def get_stock(symbol: str):
    # Placeholder for stock logic
    return {"symbol": symbol, "price": 123.45}