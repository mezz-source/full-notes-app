from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from src.repository.user_repo import UserRepo
from src.db.session import get_db

SECRET_KEY = "itsmezzintime" # make this a env variable in production
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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
    repo = UserRepo(db)
    user = repo.verify_credentials(username, password)
    if user:
        return create_access_token(data={"sub": str(user.id)})
    return None


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Returns the user ID included in the JWT Token.

    Arguments:
        token (str): The JWT Token to check
        db (Session): The database session to reference

    Returns:
        id (int): The user ID

    Raises:
        HTTPException: Invalid token as a result form JWTErrors, or generic exceptions
    """
    try:
        # unpack their blabber mouth
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        # this token is clearly forgetting something
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        # cool - is this an actual person
        repo = UserRepo(db)
        if repo.get_by_id(user_id) is None:
            raise HTTPException(status_code=401, detail="Stale authorization token - user no longer exists")

        return user_id

    except JWTError as jwt_exc:
        raise HTTPException(status_code=401, detail="Invalid token") from jwt_exc

    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc