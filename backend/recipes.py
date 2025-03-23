from typing import List
import requests
from fastapi import APIRouter, Depends, Query, HTTPException
import json
from backend.auth import get_current_user
import os
from backend import models, schemas
from backend.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()
API_KEY = "150c8b661b24475da5db3cc68d245d1e"
SPOONACULAR_API_URL = "https://api.spoonacular.com/recipes/findByIngredients"

def get_recipes_by_ingredients(ingredients: str, api_key: str):
    """
    Fetch recipes from Spoonacular API based on ingredients.
    :param ingredients: Comma-separated list of ingredients.
    :param api_key: API key for Spoonacular API.
    :return: List of recipes.
    """
    try:
        # Make the API request
        response = requests.get(
            SPOONACULAR_API_URL,
            params={
                "ingredients": ingredients,
                "number": 5,  # Limit to 5 results (can adjust based on your needs)
                "apiKey": api_key,
                "limitLicense": True,  # Ensures recipes have a proper license
                "ranking": 1,  # Ranking for relevance
                "ignorePantry": False  # Ignore pantry items (optional)
            },
             verify=False 
        )
        
        # Check for 403 Forbidden error and raise an exception
        if response.status_code == 403:
            raise HTTPException(status_code=403, detail="Forbidden: Invalid or missing API key for Spoonacular.")
        
        # Raise for other bad status codes
        response.raise_for_status()

        # Return the response as JSON if successful
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        # Handle specific HTTP errors
        raise HTTPException(status_code=response.status_code, detail=f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as e:
        # General exception for any request errors (e.g., network errors)
        raise HTTPException(status_code=500, detail=f"Error fetching recipes: {e}")

# Endpoint to get recipes based on ingredients
@router.get("/by_ingredients")
def get_recipes(user: dict = Depends(get_current_user), ingredients: str = Query(..., description="Comma-separated ingredients list")):
    # Fetch recipes based on the user's ingredients
    recipes = get_recipes_by_ingredients(ingredients, API_KEY)

    # Handle the case if no recipes are found
    if not recipes:
        raise HTTPException(status_code=404, detail="No recipes found.")
    
    return {"recipes": recipes}

@router.get("/recipes")
def get_recipes(bmi: float = Query(..., description="User's BMI value"), user: dict = Depends(get_current_user)):
    # Get recipes from the local JSON file based on BMI category
    dir_path = os.path.dirname(__file__)  # This is "C:\projects\food\backend"
    file_path = os.path.join(dir_path, "static", "recipes.json")
    
    try:
        with open(file_path, "r") as file:
            recipes = json.load(file)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="recipes.json file not found.")
    
    # Decide which category to recommend based on BMI
    if bmi < 18.5:
        category = "gain_weight"
    elif 18.5 <= bmi < 25:
        category = "balanced"
    elif 25 <= bmi < 30:
        category = "lose_weight"
    else:  # bmi >= 30
        category = "low_cal"

    # Filter recipes by that category
    filtered_recipes = [r for r in recipes if r["category"] == category]

    # Handle the case where no recipes match
    if not filtered_recipes:
        raise HTTPException(status_code=404, detail="No recipes found for your BMI category.")

    # Handle current_user as a dictionary
    user_email = user.get("email") if isinstance(user, dict) else user.email
    
    return {
        "user_email": user_email,
        "bmi": bmi,
        "recommended_category": category,
        "recipes": filtered_recipes
    }

@router.post("/save_recipe", response_model=schemas.SavedRecipe)
def save_recipe(recipe: schemas.SavedRecipeCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Handle current_user as a dictionary
    user_id = current_user.get("user_id") if isinstance(current_user, dict) else current_user.id
    
    # Save the recipe to the database
    db_recipe = models.SavedRecipe(
        title=recipe.title,
        image=recipe.image,
        used_ingredients=recipe.used_ingredients,
        missed_ingredients=recipe.missed_ingredients,
        rating=recipe.rating,    # Now storing rating, not likes
        feedback=recipe.feedback, # Optionally store initial feedback
        spoonacular_id=recipe.spoonacular_id,
        user_id=user_id
    )
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe

@router.get("/saved_recipes", response_model=List[schemas.SavedRecipe])
def get_saved_recipes(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("user_id") if isinstance(current_user, dict) else current_user.id
    saved_recipes = db.query(models.SavedRecipe).filter(models.SavedRecipe.user_id == user_id).all()
    return saved_recipes

@router.delete("/delete_recipe/{id}", status_code=204)
def delete_recipe(id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # If current_user is a dictionary, get user_id from it
    user_id = current_user.get("user_id") if isinstance(current_user, dict) else current_user.id
    print(f"Deleting recipe with id {id} for user {user_id}")  # Debugging line

    # Fetch the recipe from the database to check if it exists
    db_recipe = db.query(models.SavedRecipe).filter(models.SavedRecipe.id == id, models.SavedRecipe.user_id == user_id).first()

    print(f"Found recipe: {db_recipe}")  # Debugging line

    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Delete the recipe
    db.delete(db_recipe)
    db.commit()
    return {"message": "Recipe deleted successfully"}

@router.put("/update_feedback/{recipe_id}", response_model=schemas.SavedRecipe)
def update_feedback(recipe_id: int, update: schemas.UpdateFeedback, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id") if isinstance(current_user, dict) else current_user.id
    recipe = db.query(models.SavedRecipe).filter(models.SavedRecipe.id == recipe_id, models.SavedRecipe.user_id == user_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    recipe.feedback = update.feedback
    db.commit()
    db.refresh(recipe)
    return recipe


# Optional: Endpoint to update rating via star clicks
@router.put("/update_rating/{recipe_id}", response_model=schemas.SavedRecipe)
def update_rating(recipe_id: int, update: schemas.UpdateRating, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id") if isinstance(current_user, dict) else current_user.id
    recipe = db.query(models.SavedRecipe).filter(models.SavedRecipe.id == recipe_id, models.SavedRecipe.user_id == user_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    recipe.rating = update.rating
    db.commit()
    db.refresh(recipe)
    return recipe