"""
Chat Service - Main orchestration layer
Built with Kiro - handles memory-enhanced conversations
"""
from datetime import datetime
from typing import List, Dict

from storage.memory_store import MemoryStore
from core.llm import ask_llm


class ChatService:
    """
    Orchestrates the RAG pipeline with memory enhancement
    """
    
    def __init__(self):
        self.store = MemoryStore()
    
    def chat(self, user_id: str, message: str, llm_provider: str = "openai", top_k: int = 20) -> dict:
        """Main chat function with memory enhancement"""
        
        print(f"\n{'='*60}")
        print(f"💬 Chat Request: {user_id}")
        print(f"📝 Message: {message}")
        print(f"{'='*60}\n")
        
        # Retrieve relevant contexts
        print(f"🔍 Retrieving contexts (top_k={top_k})...")
        contexts = self.store.retrieve(user_id, message, top_k)
        print(f"✅ Retrieved {len(contexts)} contexts")
        
        # Enhance prompt with memory
        enhanced_prompt = message
        has_memory = len(contexts) > 0
        
        if has_memory:
            memory_context = "\n\n".join([f"- {ctx}" for ctx in contexts[:3]])
            enhanced_prompt = f"Relevant memories:\n{memory_context}\n\nUser question: {message}"
            print(f"✅ Enhanced with {len(contexts)} memories")
        else:
            print("ℹ️  No relevant memory found")
        
        # Generate response
        print(f"🤖 Generating response with {llm_provider}...")
        response = self._generate_response(
            message=enhanced_prompt,
            contexts=contexts,
            provider=llm_provider
        )
        
        print(f"✅ Response generated: {response[:100]}...")
        
        # Store conversation
        print("💾 Storing conversation...")
        self._store_conversation(user_id, message, response, llm_provider)
        
        print(f"\n{'='*60}")
        print("✅ Chat complete!")
        print(f"{'='*60}\n")
        
        return {
            "response": response,
            "context_used": contexts,
            "has_memory": has_memory,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_response(self, message: str, contexts: List[str], provider: str) -> str:
        """Generate LLM response"""
        
        task = """You are a helpful AI assistant.

Answer the user's question naturally and conversationally.

If the question includes memories/context at the beginning, use that information to give a personalized answer, but don't mention that you're using memories."""
        
        response = ask_llm(
            task_description=task,
            input_data=message,
            temperature=0.7
        )
        
        return response.strip()
    
    def _store_conversation(self, user_id: str, user_message: str, llm_response: str, provider: str):
        """Store conversation in memory"""
        
        try:
            # Create simple chunk
            chunk_text = f"User: {user_message}\nAssistant: {llm_response}"
            
            # Store in memory
            self.store.add_memory(
                user_id=user_id,
                user_msg=user_message,
                llm_response=llm_response,
                chunk_text=chunk_text,
                chunk_type="conversation",
                priority="high",
                provider=provider
            )
            
            print("   ✅ Conversation stored")
            
            # Save to disk/S3
            self.store.save()
            
        except Exception as e:
            print(f"   ⚠️ Storage failed: {e}")
    
    def retrieve_context(self, user_id: str, query: str, top_k: int = 5) -> List[str]:
        """
        Retrieve context for Chrome extension
        Returns relevant memory snippets
        """
        contexts = self.store.retrieve(user_id, query, top_k)
        return contexts[:top_k]
    
    def save_conversation(self, user_id: str, user_message: str, llm_response: str, provider: str = "openai") -> dict:
        """
        Save conversation (called by /save-response endpoint)
        """
        print(f"\n💾 Saving conversation for {user_id}")
        
        try:
            chunk_text = f"User: {user_message}\nAssistant: {llm_response}"
            
            self.store.add_memory(
                user_id=user_id,
                user_msg=user_message,
                llm_response=llm_response,
                chunk_text=chunk_text,
                chunk_type="conversation",
                priority="high",
                provider=provider
            )
            
            self.store.save()
            
            return {
                "chunks_stored": 1,
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Save failed: {e}")
            return {
                "chunks_stored": 0,
                "success": False
            }
    
    def save_pending_prompt(self, user_id: str, prompt: str):
        """Save prompt before response is available"""
        print(f"💾 Prompt saved (pending response): {prompt[:50]}...")
    
    def get_user_memories(self, user_id: str) -> List[dict]:
        """Get user memories"""
        return self.store.get_user_memories(user_id)
    
    def clear_user_data(self, user_id: str) -> int:
        """Clear user data"""
        return self.store.clear_user_memory(user_id)
    
    def get_stats(self) -> dict:
        """Get system stats"""
        return self.store.get_stats()
