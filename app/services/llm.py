from langchain_deepseek import ChatDeepSeek
from langchain.schema import HumanMessage
from typing import AsyncGenerator
from config import settings

llm = ChatDeepSeek(
    model="deepseek-chat",  
    api_key = settings.DEEPSEEK_API_KEY,
    temperature=0.7,
    streaming=True
)


async def stream_chat_response(prompt: str) -> AsyncGenerator[str, None]:
    """
    Генерация ответа от LLM в виде потока
    """
    async for chunk in llm.astream([HumanMessage(content=prompt)]):
        if chunk.content:
            yield chunk.content

