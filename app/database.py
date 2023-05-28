from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi_utils.guid_type import setup_guids_postgresql
from .config import settings


# Construct the PostgreSQL database connection URL with the variables stored in the .env file and
POSTGRES_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOSTNAME}:{settings.DATABASE_PORT}/{settings.POSTGRES_DB}"

engine = create_engine(
    POSTGRES_URL, echo=True
)

print("The postgres url is:{0}".format(POSTGRES_URL))

# The UUIDs can only be generated if the pgcrypto extension is installed on the Postgres instance, 
# so the setup_guids_postgresql() function will tell Postgres to install the extension if it doesn’t exist.
setup_guids_postgresql(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

