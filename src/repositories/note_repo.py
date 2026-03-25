from sqlalchemy.orm import Session
from src.models.note import Note as NoteModel

class NoteRepository:
    def __init__(self, db: Session):
        self.db = db
    
    async def get(self, note_id: int):
        return self.db.query(NoteModel).filter(NoteModel.id == note_id).first()

    async def query(
            self,
            offset: int = 0,
            limit: int = 100,
            note_id: int | None = None,
            author_id: int | None = None,
            title: str | None = None,
            title_contains: str | None = None,
            content_contains: str | None = None,
            tag: str | None = None,
            ):
            query = self.db.query(NoteModel)

            if note_id is not None:
                query = query.filter(NoteModel.id == note_id)
            if author_id is not None:
                query = query.filter(NoteModel.author_id == author_id)
            if title is not None:
                query = query.filter(NoteModel.title == title)
            if title_contains is not None:
                query = query.filter(NoteModel.title.contains(title_contains))
            if content_contains is not None:
                query = query.filter(NoteModel.content.contains(content_contains))
            if tag is not None:
                query = query.filter(NoteModel.flags.contains(tag))

            return query.offset(offset).limit(limit).all()

    async def delete(self, note_id: int):
        try:
            note = self.db.query(NoteModel).filter(NoteModel.id == note_id).first()
            if note:
                self.db.delete(note)
                self.db.commit()
                return True
            return False
        except Exception:
            self.db.rollback()
            raise

    async def create(self, author_id: int, title: str, content: str, flags: str):
        try:
            new_note = NoteModel(
                author_id=author_id,
                title=title,
                content=content,
                flags=flags,
            )
            self.db.add(new_note)
            self.db.commit()
            self.db.refresh(new_note)
            return new_note
        except Exception:
            self.db.rollback()
            raise

    async def modify(self, note_id: int, modifications: dict):
        try:
            note = self.db.query(NoteModel).filter(NoteModel.id == note_id).first()
            if not note:
                return None

            for key, value in modifications.items():
                setattr(note, key, value)

            self.db.commit()
            self.db.refresh(note)
            return note
        except Exception:
            self.db.rollback()
            raise
    