from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from database import DBSessionDep
from entities import Conversation
from schemas import ConversationCreate, ConversationOut, ConversationUpdate, MessageOut
from repositories.conversations import ConversationRepository
from services.conversations import ConversationService


from fastapi import BackgroundTasks
from fastapi.responses import StreamingResponse
from itertools import tee

from services.llm import stream_chat_response
from entities import Message
from repositories.conversations import ConversationRepository
from database import async_session


router = APIRouter(prefix="/conversations", tags=["conversations"])


async def get_conversation(
    conversation_id: int, session: DBSessionDep
) -> Conversation:
    conversation = await ConversationRepository(session).get(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    return conversation

async def store_message(prompt_content: str, response_content: str, conversation_id: int) -> None:
    async with async_session() as session:
        msg = Message(
            conversation_id=conversation_id,
            prompt_content=prompt_content,
            response_content=response_content,
        )
        session.add(msg)
        await session.commit()

GetConversationDep = Annotated[Conversation, Depends(get_conversation)]


@router.get("")
async def list_conversations_controller(
    session: DBSessionDep, skip: int = 0, take: int = 100
) -> list[ConversationOut]:
    conversations = await ConversationRepository(session).list(skip, take)
    return [ConversationOut.model_validate(c) for c in conversations]


@router.get("/{conversation_id}")
async def get_conversation_controller(
    conversation: GetConversationDep,
) -> ConversationOut:
    return ConversationOut.model_validate(conversation)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_conversation_controller(
    conversation: ConversationCreate, session: DBSessionDep
) -> ConversationOut:
    new_conversation = await ConversationRepository(session).create(conversation)
    return ConversationOut.model_validate(new_conversation)


@router.put("/{conversation_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_conversation_controller(
    conversation: GetConversationDep,
    updated_conversation: ConversationUpdate,
    session: DBSessionDep,
) -> ConversationOut:
    updated = await ConversationRepository(session).update(
        conversation.id, updated_conversation
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ConversationOut.model_validate(updated)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation_controller(
    conversation: GetConversationDep, session: DBSessionDep
) -> None:
    await ConversationRepository(session).delete(conversation.id)


@router.get("/{conversation_id}/messages")
async def list_conversation_messages_controller(
    conversation: GetConversationDep,
    session: DBSessionDep,
) -> list[MessageOut]:
    messages = await ConversationService(session).list_messages(conversation.id)
    return [MessageOut.model_validate(m) for m in messages]

@router.get("/{conversation_id}/text/generate/stream")
async def stream_llm_controller(
    conversation_id: int,
    prompt: str,
    background_tasks: BackgroundTasks,
    session: DBSessionDep,
):
    conv = await ConversationRepository(session).get(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    async def gen():
        parts = []
        async for chunk in stream_chat_response(prompt):
            parts.append(chunk)
            yield chunk
        full_text = "".join(parts)
        background_tasks.add_task(store_message, prompt, full_text, conversation_id)

    return StreamingResponse(gen(), media_type="text/plain")



