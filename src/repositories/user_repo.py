from sqlalchemy.orm import Session
from src.schemas.core.user import User as UserSchema, GetUser, ModifyUser, DeleteUser
from src.models.user import User as UserModel

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    async def get(self, user_id: int):
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()        

    async def get_by_username(self, username: str):
        return self.db.query(UserModel).filter(UserModel.username == username).first()
    
    async def get_by_email(self, email: str):
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    async def query(
            self,
            offset: int = 0,
            limit: int = 100,
            username: str | None = None,
            email: str | None = None,
            username_contains: str | None = None
            ):
            query = self.db.query(UserModel)
            
            if username is not None:
                query = query.filter(UserModel.username == username)
            if email is not None:
                query = query.filter(UserModel.email == email)
            if username_contains is not None:
                query = query.filter(UserModel.username.contains(username_contains))
            
            return query.offset(offset).limit(limit).all()

    async def delete(self, user_id: int):
        try:
            user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
            if user:
                self.db.delete(user)
                self.db.commit()
                return True
            return False
        except Exception:
            self.db.rollback()
            raise

    async def create(self, email: str, username: str, password_hash: str):
        try:
            new_user = UserModel(
                email=email,
                username=username,
                password_hash=password_hash
            )
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return new_user
        except Exception:
            self.db.rollback()
            raise
    
    async def modify(self, user_id: int, modifications: dict):
        try:
            user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
            if not user:
                return None
            
            for key, value in modifications.items():
                setattr(user, key, value)
            
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception:
            self.db.rollback()
            raise