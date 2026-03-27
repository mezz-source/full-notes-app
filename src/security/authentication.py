from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.util.responses import model_to_dict as model_to_dict_async
from src.repositories.user_repo import UserRepository

SECRET_KEY = "itsmezzintime" # make this a env variable in production
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def model_to_dict(model) -> dict:
    """Convert a SQLAlchemy model instance to a dictionary, converting datetime to ISO format."""
    result = {}
    for column in model.__table__.columns:

        value = getattr(model, column.name)
        if isinstance(value, datetime):
            value = value.isoformat()
        result[column.name] = value
    return result

async def async_create_access_token(data: dict) -> str:
    """
    Creates a new JWT Token based on SECRET_KEY, algorithm, and the input data dictionary
    
    Arguments:
        data (dict): The data to tokenize

    Returns:
        token (str): The created JWT Bearer string

    """
    # lets get them their little wrist band
    payload = data.copy()
    payload["exp"] = int((datetime.now() + timedelta(hours=1)).timestamp())
    print(payload)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(data: dict) -> str:
    """
    Creates a new JWT Token based on SECRET_KEY, algorithm, and the input data dictionary
    
    Arguments:
        data (dict): The data to tokenize

    Returns:
        token (str): The created JWT Bearer string

    """
    # lets get them their little wrist band
    payload = data.copy()
    payload["exp"] = int((datetime.now() + timedelta(hours=1)).timestamp())
    print(payload)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(username: str, password: str, db: Session) -> str | None:
    """Authenticate user and return access token if valid.
    
    Arguments:
        username (str): The user's username
        password (str): The users unhashed password
        db (Session): The current database session to reference
    
    Returns:
        token (str | None): The new JWT token if authentication succeded, otherwise returns nothing
    
    """
    print("Warning:", "stub alert! assumes you're ID 1")
    repo = UserRepository(db)
    user = {"id": 1} # REPLACE WITH repo.verify_credentials(username, password) when implemented
    # user = repo.verify_credentials(username, password)
    if user:
        return create_access_token(data={"sub": str(1)})
    return None

async def get_user_dict(user_id: int, db: Session) -> dict | None:
    """Get user dictionary by user ID.
    
    Arguments:
        user_id (int): The ID of the user to retrieve
        db (Session): The current database session to reference
    
    Returns:
        user_dict (dict | None): The user dictionary if found, otherwise returns nothing
    
    """
    repo = UserRepository(db)
    user = await repo.get(user_id)
    if user:
        return await model_to_dict_async(user)
    return None

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Returns the user ID included in the JWT Token.

    Arguments:
        token (str): The JWT Token to check
        db (Session): The database session to reference

    Returns:
        user (dict): The user dictionary of the current user based on the token's user ID

    Raises:
        HTTPException: Invalid token as a result form JWTErrors, or generic exceptions
    """
    try:
        # unpack their blabber mouth
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        print("Decoded token payload:", payload)
        print("user ID from token:", user_id)
        # this token is clearly forgetting something
        if user_id is None:
            print("Token payload missing 'sub' field:", payload)
            raise HTTPException(status_code=401, detail="Invalid token")

        user = await get_user_dict(int(user_id), db)
        if user is None:
            raise HTTPException(status_code=401, detail="Stale authorization token - user no longer exists")

        return user

    except JWTError as jwt_exc:
        print("JWT Error during token decoding:", str(jwt_exc))
        raise HTTPException(status_code=401, detail="Invalid token") from jwt_exc

    except Exception as exc:
        print("Unexpected error:", str(exc))
        raise HTTPException(status_code=401, detail="Invalid token") from exc