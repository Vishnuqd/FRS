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
    likes: int
    spoonacular_id: int

class SavedRecipeCreate(BaseModel):
    title: str
    image: str
    used_ingredients: Optional[str] = None  # Allow it to be None
    missed_ingredients: Optional[str] = None  # Allow it to be None
    likes: Optional[int] = 0  # Default to 0 if likes are not provided
    spoonacular_id: int


class SavedRecipe(SavedRecipeBase):
    id: int

    class Config:
        orm_mode = True