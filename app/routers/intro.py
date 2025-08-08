from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_intro():
    return {
        "title": "Intro to Finances",
        "content": "Welcome! We’ll cover budgeting, saving, debt, and basic investing."
    }