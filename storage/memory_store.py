"""
Memory Store - FAISS Vector Store with Persistence
Built with Kiro - efficient vector storage and retrieval
"""
import faiss
import numpy as np
import json
import os
from typing import List, Dict
from datetime import datetime

from core.config import EMBEDDING_DIM, SIMILARITY_THRESHOLD
from core.llm import get_embedding


class MemoryStore:
    """Handles vector storage and retrieval with local persistence"""
    
    def __init__(self):
        self.index = None
        self.memory_store = []
        self.load()
    
    def load(self):
        """Load existing data from local disk"""
        # Load FAISS index
        try:
            if os.path.exists('faiss_index.bin'):
                self.index = faiss.read_index('faiss_index.bin')
                print(f"✅ Loaded {self.index.ntotal} vectors")
            else:
                self.index = faiss.IndexFlatL2(EMBEDDING_DIM)
                print("✅ Created new index")
        except Exception as e:
            print(f"⚠️ Creating new index: {e}")
            self.index = faiss.IndexFlatL2(EMBEDDING_DIM)
        
        # Load memory store
        try:
            if os.path.exists('memory_store.json'):
                with open('memory_store.json', 'r') as f:
                    self.memory_store = json.load(f)
                print(f"✅ Loaded {len(self.memory_store)} memories")
        except Exception as e:
            print(f"⚠️ Memory load failed: {e}")
            self.memory_store = []
    
    def save(self):
        """Save data to local disk"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, 'faiss_index.bin')
            
            # Save memory store
            with open('memory_store.json', 'w') as f:
                json.dump(self.memory_store, f, indent=2)
            
            print("✅ Saved to disk")
                
        except Exception as e:
            print(f"⚠️ Save failed: {e}")
    
    def add_memory(self, user_id: str, user_msg: str, llm_response: str,
                   chunk_text: str, chunk_type: str, priority: str, provider: str):
        """
        Add a memory chunk to vector store
        
        Args:
            user_id: User identifier
            user_msg: User's message
            llm_response: LLM's response
            chunk_text: Text chunk to store
            chunk_type: Type of chunk (conversation, fact, etc.)
            priority: Priority level (high, medium, low)
            provider: LLM provider used
        """
        # Generate embedding
        embedding = get_embedding(chunk_text, user_id=user_id)
        
        # Create memory entry
        memory_entry = {
            "user_id": user_id,
            "user_message": user_msg,
            "llm_response": llm_response,
            "chunk_text": chunk_text,
            "chunk_type": chunk_type,
            "priority": priority,
            "provider": provider,
            "timestamp": datetime.now().isoformat(),
            "combined_text": chunk_text
        }
        
        # Add to FAISS
        embedding_array = np.array([embedding]).astype('float32')
        self.index.add(embedding_array)
        self.memory_store.append(memory_entry)
    
    def retrieve(self, user_id: str, query: str, top_k: int = 5) -> List[str]:
        """
        Retrieve relevant contexts with priority filtering
        
        Args:
            user_id: User identifier
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of relevant text chunks
        """
        if self.index.ntotal == 0:
            print("⚠️ Retrieve: Index is empty")
            return []
        
        print(f"🔍 Retrieving for user '{user_id}', query: '{query[:50]}...'")
        
        # Get query embedding
        query_embedding = get_embedding(query, user_id=user_id)
        query_array = np.array([query_embedding]).astype('float32')
        
        # Search
        search_k = min(top_k * 2, self.index.ntotal)
        distances, indices = self.index.search(query_array, search_k)
        
        print(f"🔍 Searched {search_k} vectors, examining results...")
        
        # Organize by priority
        results = {"high": [], "medium": [], "low": []}
        user_memories_found = 0
        
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.memory_store) and idx >= 0:
                memory = self.memory_store[idx]
                similarity = 1 - (distance / 2)
                
                # Filter by user_id
                if memory.get("user_id") != user_id:
                    continue
                
                # Filter by similarity threshold
                if similarity < SIMILARITY_THRESHOLD:
                    continue
                
                chunk_text = memory.get("chunk_text", memory.get("combined_text", ""))
                priority = memory.get("priority", "medium")
                
                user_memories_found += 1
                item = {"text": chunk_text, "similarity": similarity}
                results[priority].append(item)
        
        print(f"✅ Found {user_memories_found} matches")
        
        # Sort each priority group by similarity
        for priority in ["high", "medium", "low"]:
            results[priority].sort(key=lambda x: x["similarity"], reverse=True)
        
        # Combine results
        all_results = results["high"] + results["medium"] + results["low"]
        return [item["text"] for item in all_results[:top_k]]
    
    def clear_user_memory(self, user_id: str) -> int:
        """
        Clear all memories for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of memories cleared
        """
        initial = len(self.memory_store)
        self.memory_store = [m for m in self.memory_store if m.get("user_id") != user_id]
        cleared = initial - len(self.memory_store)
        
        if cleared > 0:
            # Rebuild index
            self.index = faiss.IndexFlatL2(EMBEDDING_DIM)
            for memory in self.memory_store:
                try:
                    text = memory.get("chunk_text", memory.get("combined_text", ""))
                    embedding = get_embedding(text)
                    self.index.add(np.array([embedding]).astype('float32'))
                except Exception as e:
                    print(f"⚠️ Re-index warning: {e}")
            
            self.save()
        
        return cleared
    
    def get_user_memories(self, user_id: str) -> List[Dict]:
        """
        Get all memories for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of memory dictionaries
        """
        return [m for m in self.memory_store if m.get("user_id") == user_id]
    
    def get_stats(self) -> Dict:
        """
        Get storage statistics
        
        Returns:
            Dictionary with stats
        """
        # Count unique users
        unique_users = set(m.get("user_id") for m in self.memory_store if m.get("user_id"))
        
        return {
            "total_memories": len(self.memory_store),
            "total_vectors": self.index.ntotal,
            "total_users": len(unique_users),
            "storage_type": "Local"
        }
