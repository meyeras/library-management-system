from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.models import User, Book
from app.database import get_db
from fastapi.responses import JSONResponse
from app.crypto import verify_password

security = HTTPBearer()

# Example admin user credentials (change these with your own)
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300


# Function to authenticate user and generate access token
async def  authenticate_user(username: str, password: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if user:
        print("Found user for username {0}".format(username))
    if user and verify_password(password, user.password):
        return user
    return None

# Function to create access token
def create_access_token(username: str):
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    to_encode = {"sub": username, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def remove_bearer_prefix(token: str) -> str:
    if token.startswith("Bearer "):
        return token[len("Bearer "):]
    return token

# Function to get current user based on access token
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        print("Enter get_current_user")
        token = remove_bearer_prefix(credentials.credentials)
        print("Token is:{0}".format(token))
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("GET CURRENT USER EXTRACT USERNAME FROM TOKEN:{0}",payload)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid user")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    print("Get current user succeeded!")
    return user