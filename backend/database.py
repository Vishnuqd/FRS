from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# MySQL Database Connection
DATABASE_URL = "mysql+pymysql://root:@localhost:3308/food_db"

engine = create_engine(
    DATABASE_URL,
    pool_size=10,  # Increase pool size (default is 5)
    max_overflow=20,  # Increase the overflow limit (default is 10)
    pool_timeout=30,  # Timeout in seconds
    pool_recycle=3600  # Recycle connections after this many seconds
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
