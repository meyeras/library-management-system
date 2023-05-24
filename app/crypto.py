from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
print("PASSWORD CONTEXT CREATED")


# Function to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Function to hash password
def get_password_hash(password):
    return pwd_context.hash(password)

