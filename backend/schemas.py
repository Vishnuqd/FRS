from typing import Optional
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class Token(BaseModel):
    access_token: str
    
class BMICalculate(BaseModel):
    height: float
    weight: float

class LoginResponse(BaseModel):
    access_token: str
    name: str

class UserLogin(BaseModel):  
    email: str
    password: str
    
class SavedRecipeBase(BaseModel):
    title: str
    image: str
    used_ingredients: str
    missed_ingredients: str
    rating: int  # new name instead of likes
    spoonacular_id: int
    feedback: Optional[str] = None

class SavedRecipeCreate(BaseModel):
    title: str
    image: str
    used_ingredients: Optional[str] = None  # Allow it to be None
    missed_ingredients: Optional[str] = None  # Allow it to be None
    rating: int  # new name instead of likes
    spoonacular_id: int
    feedback: Optional[str] = None


class SavedRecipe(SavedRecipeBase):
    id: int

    class Config:
        orm_mode = True

# New schema for updating feedback
class UpdateFeedback(BaseModel):
    feedback: str

# (Optional) New schema for updating rating
class UpdateRating(BaseModel):
    rating: int