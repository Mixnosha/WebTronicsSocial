import datetime
from sqlalchemy import DateTime, ForeignKey, String, Boolean, Text
from sqlalchemy.orm import declarative_base, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from auth.models import User

Base = declarative_base()

class Post(Base):
    __tablename__ = "post"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, nullable=False)
    title = mapped_column(String(50), nullable=False)
    body = mapped_column(Text, nullable=False)
    created_at = mapped_column(DateTime, default=datetime.datetime.utcnow)
    user_id = mapped_column(ForeignKey(User.id), nullable=False)

class ReactionPost(Base):
    __tablename__ = "reaction_post"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, nullable=False)
    user_id = mapped_column(ForeignKey(User.id), nullable=False)
    post_id = mapped_column(ForeignKey(Post.id), nullable=False)
    is_like = mapped_column(Boolean, nullable=False) # if True => like

