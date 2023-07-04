from pydantic import BaseModel, EmailStr, Field
import datetime
from uuid import UUID, uuid4


class PostModel(BaseModel):
    id: UUID | None
    title: str = Field(..., example="About WebTronics")
    body: str = Field(..., example="Webtronics is ...")
    user_id: UUID | None
    created_at: datetime.datetime | None

    class Config:
        orm_mode=True
        schema_extra = {
                "example": {
                    "title": "About WebTronics", 
                    "body": "WebTronics is ..."
                    }
                }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.id is None:
            self.id = uuid4()
        if self.created_at is None:
            self.created_at = datetime.datetime.utcnow()

class ReactionPostModel(BaseModel):
    id: UUID | None
    user_id: UUID | None 
    post_id: UUID 
    is_like: bool = True
    
    class Config:
        schema_extra = {
                "example": {
                    "post_id": uuid4(), 
                    "is_like": True 
                    }
                }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.id is None:
            self.id = uuid4()

class ReactionPostForRedisModel(BaseModel):
    id: UUID | None 
    post_id: UUID 
    is_like: bool 
    title: str 
    body: str 
    author: EmailStr




class UpdatePostModel(BaseModel):
    title: str
    body: str


class AllPostModel(BaseModel):
    id: UUID
    title: str 
    body: str 
    created_at: datetime.datetime 
    email: str | None

    class Config:
        orm_mode=True
