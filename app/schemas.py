from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ConversationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    model_type: str


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(ConversationBase):
    pass


class ConversationOut(ConversationBase):
    id: int
    created_at: datetime
    updated_at: datetime


class MessageBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    prompt_content: str
    response_content: str


class MessageOut(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime

