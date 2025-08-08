from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# import our tab routers
from app.routers import intro, market, portfolio, planning

app = FastAPI(title="ProfitPlug API", version="0.1.0")

# CORS (dev-friendly)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount each tab under its own prefix
app.include_router(intro.router,     prefix="/api/intro",     tags=["Intro to Finances"])
app.include_router(market.router,    prefix="/api/market",    tags=["Market Updates"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(planning.router,  prefix="/api/planning",  tags=["Planning"])

@app.get("/")
def root():
    return {"ok": True, "service": "ProfitPlug API"}