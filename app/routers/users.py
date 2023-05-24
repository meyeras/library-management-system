from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas import UserCreate, UserUpdateRequest, UserUpdateResponse, UserSchema
from app.models import User
from app.database import get_db
from app.crypto import get_password_hash
from typing import List


from app.auth import get_current_user, is_admin
router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    print("Enter in register API")
    # Check if the email is already taken
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if the username is already taken
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Hash the password before storing it in the database
    hashed_password = get_password_hash(user.password)
    # Create a new user in the database
    new_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


@router.get("/", response_model=List[UserSchema])
def get_all_users(db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can access this API.")
    users = db.query(User).all()
    return users

@router.put("/me", response_model=UserUpdateResponse)
def update_own_user(user_update: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print("Enter in update_own_user")
    updated_user = update_user_util(user=current_user, user_update=user_update, db=db) 
    return updated_user


@router.put("/{user_id}", response_model=UserUpdateResponse)
def update_user(
    user_id: int,
    user_update: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check if the current user is an admin
    print("Current user: username{0} is_admin{1}".format(current_user.username, current_user.is_admin))
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can access this API.")

    # Retrieve the user from the database
    user = db.query(User).get(user_id)

    # If the user doesn't exist, raise an exception
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = update_user_util(user=user, user_update=user_update, db=db)
    return updated_user


def update_user_util(user_update: UserUpdateRequest, user: User, db: Session):
    # Update the user's details
    if user_update.username:
        print("User update username")
        if db.query(User).filter(User.username == user_update.username).first():
            raise HTTPException(status_code=400, detail="Username already registered")
        user.username = user_update.username
    if user_update.email:
        if db.query(User).filter(User.email == user_update.email).first():
            raise HTTPException(status_code=400, detail="Email already taken")
        user.email = user_update.email
    if user_update.password:
        # Hash the new password before updating
        password_hash = get_password_hash(user_update.password)
        user.password = password_hash

    # Save the changes to the database
    db.commit()
    db.refresh(user)
    print("User refreshed in database")
    # updated_user = UserUpdateResponse(username=user.username, password=user.password, email=user.email)
    # return updated_user
    return user
