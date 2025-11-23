"""
LLM Provider Abstraction
Built with Kiro - unified interface for OpenAI
"""
from core.config import openai_client, EMBEDDING_MODEL, CHEAP_LLM_MODEL


def get_embedding(text: str, user_id: str = None) -> list[float]:
    """
    Generate embedding for text using OpenAI
    
    Args:
        text: Text to embed
        user_id: Optional user ID for usage tracking
        
    Returns:
        List of floats representing the embedding vector
    """
    try:
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        raise


def ask_llm(task_description: str, input_data: str, temperature: float = 0.7) -> str:
    """
    Ask LLM to perform a task
    
    Args:
        task_description: Description of the task
        input_data: Input data for the task
        temperature: Sampling temperature (0-1)
        
    Returns:
        LLM response as string
    """
    try:
        response = openai_client.chat.completions.create(
            model=CHEAP_LLM_MODEL,
            messages=[
                {"role": "system", "content": task_description},
                {"role": "user", "content": input_data}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ LLM error: {e}")
        raise
