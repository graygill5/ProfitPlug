from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_planning():
    return {
        "title": "Planning",
        "steps": [
            "Define goals (3, 12, 36 months)",
            "Set a monthly budget",
            "Automate savings/investing"
        ]
    }
