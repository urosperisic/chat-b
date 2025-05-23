from passlib.context import CryptContext

# Create a password context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to hash a password
def hash_password(password: str):
    return pwd_context.hash(password)

if __name__ == "__main__":
    password = "a"


    hashed_password = hash_password(password)
    print(f"Original password: {password}")
    print(f"Hashed password: {hashed_password}")

from uuid import uuid4

novi_uuid = uuid4()

print(str(novi_uuid))