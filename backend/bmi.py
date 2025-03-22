from fastapi import APIRouter, Depends, HTTPException
import requests
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import BMIRecord
from backend.schemas import BMICalculate
from backend import auth
from fastapi import Depends
from pydantic import BaseModel
from .auth import get_current_user
import jwt
import time

router = APIRouter()
API_KEY = "150c8b661b24475da5db3cc68d245d1e"
SPOONACULAR_API_URL = "https://api.spoonacular.com/recipes/complexSearch"
NUTRITION_API_URL = "https://api.spoonacular.com/recipes/{}/nutritionWidget.json"
@router.get("/protected-route")
def protected_route(user: dict = Depends(auth.get_current_user)):
    return {"message": "You are authenticated!", "user": user}


class BMIRequest(BaseModel):
    weight: float
    height: float

@router.post("/bmi")
def calculate_bmi(bmi_req: BMIRequest, user = Depends(get_current_user), db: Session = Depends(get_db)):
    
    weight = bmi_req.weight
    height_cm = bmi_req.height
    if height_cm <= 0:
        return {"error": "Height must be greater than 0"}

    # Convert cm to meters:
    height_m = height_cm / 100.0

    bmi_value = weight / (height_m * height_m)
    if bmi_value < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi_value < 25:
        category = "Normal weight"
    elif 25 <= bmi_value < 30:
        category = "Overweight"
    else:
        category = "Obesity"

    # Create a new BMIRecord and link it to the user
    record = BMIRecord(
        user_id=user["user_id"],
        height=height_m,
        weight=weight,
        bmi=bmi_value,
        category=category
    )

    # Save to the database
    db.add(record)
    db.commit()
    db.refresh(record)

    # Return BMI and category
    return {
        "bmi": round(bmi_value, 2),
        "category": category
    }

@router.get("/bmi_recipes")
def fetch_bmi_recipes(category: str, user = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    category_map = {
        "Underweight": "high-calorie",
        "Normal weight": "balanced",
        "Overweight": "low-calorie",
        "Obesity": "low-calorie"
    }

    query = category_map.get(category, "balanced")

    # Additional filters for more distinction
    filters = {
        "Underweight": {
            "cuisine": "Italian",  # High-calorie, nutrient-dense foods for underweight
            "excludeIngredients": "cheese",  # Example exclusion for underweight
        },
        "Normal weight": {
            "cuisine": "Mediterranean",  # Balanced foods for normal weight
            "intolerances": "gluten",  # Example intolerance for normal weight
        },
        "Overweight": {
            "cuisine": "Indian",  # Low-calorie foods for overweight
            "excludeIngredients": "sugar",  # Exclude sugar for overweight category
        },
        "Obesity": {
            "cuisine": "Mexican",  # Very low-calorie foods for obesity
            "intolerances": "dairy",  # Exclude dairy for obesity
        }
    }

    # Fetch the filter for the given category
    filter_params = filters.get(category, {})

    response = requests.get(
        "https://api.spoonacular.com/recipes/complexSearch",
        params={
            "diet": query,
            "apiKey": API_KEY,
            "timestamp": time.time(),
            **filter_params  # Add the specific filters based on the BMI category
        },
        verify=False
    )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch recipes from Spoonacular API")

    recipes = response.json().get("results", [])

    return {"recipes": recipes}

@router.get("/recipe_nutrition/{recipe_id}")
def fetch_recipe_nutrition(recipe_id: int):
    # Fetch detailed nutrition information for a recipe
    nutrition_response = requests.get(
        NUTRITION_API_URL.format(recipe_id),
        params={"apiKey": API_KEY},
        verify=False
    )

    if nutrition_response.status_code != 200:
        # If nutrition data is not available, return a default value
        return {"error": "Nutrition data not available"}

    nutrition_data = nutrition_response.json()
    
    # Return nutrition data
    return nutrition_data

@router.get("/last_bmi")
def get_last_bmi(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # Fetch the most recent BMI record for the user
    last_bmi = db.query(BMIRecord).filter(BMIRecord.user_id == user["user_id"]).order_by(BMIRecord.id.desc()).first()

    if last_bmi:
        return {
            "bmi": round(last_bmi.bmi, 2),
            "category": last_bmi.category
        }
    else:
        return {"message": "No BMI record found."}