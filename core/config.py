"""
Configuration and Constants
Built with Kiro - centralized configuration management
"""
import os
from openai import OpenAI

# Embedding settings
EMBEDDING_DIM = 1536
EMBEDDING_MODEL = "text-embedding-ada-002"

# Storage paths
MEMORY_FILE = "memory_store.json"
INDEX_FILE = "faiss_index.bin"
ENTITIES_FILE = "user_entities.json"

# LLM settings
CHEAP_LLM_MODEL = "gpt-4o-mini"
EXTRACTION_TEMPERATURE = 0.1
EXPANSION_TEMPERATURE = 0.3
CHAT_TEMPERATURE = 0.7

# Retrieval settings
DEFAULT_TOP_K = 5
SIMILARITY_THRESHOLD = 0.5

# Supabase JWT Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
SUPABASE_JWT_ISSUER = f"{SUPABASE_URL}/auth/v1"
SUPABASE_JWT_AUDIENCE = "authenticated"
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Stripe Configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STRIPE_PRICE_PRO = os.getenv("STRIPE_PRICE_PRO", "price_pro")
STRIPE_PRICE_ENTERPRISE = os.getenv("STRIPE_PRICE_ENTERPRISE", "price_enterprise")
WEBAPP_URL = os.getenv("WEBAPP_URL", "http://localhost:3000")

# Initialize OpenAI client
def get_openai_client():
    """Initialize and return OpenAI client"""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI initialized")
        return client
    except Exception as e:
        print(f"❌ OpenAI failed: {e}")
        return None

# Global OpenAI client
openai_client = get_openai_client()
