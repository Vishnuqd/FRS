from sqlalchemy import Column, Integer, Text, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))

    saved_recipes = relationship("SavedRecipe", back_populates="user")

class BMIRecord(Base):
    __tablename__ = "bmi_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    height = Column(Float)
    weight = Column(Float)
    bmi = Column(Float)
    category = Column(String(50))

class SavedRecipe(Base):
    __tablename__ = "saved_recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    image = Column(String)
    used_ingredients = Column(Text)
    missed_ingredients = Column(Text)
    likes = Column(Integer)
    spoonacular_id = Column(Integer, unique=True, index=True)  # The Spoonacular recipe ID
    
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="saved_recipes")