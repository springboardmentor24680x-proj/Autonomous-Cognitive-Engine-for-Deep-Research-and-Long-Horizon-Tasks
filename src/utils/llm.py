import os
from dotenv import load_dotenv
from groq import Groq

# LangSmith tracing
from langsmith import traceable

load_dotenv()

# ================= ENV =================
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise RuntimeError("❌ GROQ_API_KEY not found in .env")

# ================= GROQ CLIENT =================
client = Groq(api_key=API_KEY)

# ⚡ FAST GROQ MODEL
MODEL = "llama-3.1-8b-instant"

# ================= SIMPLE CACHE =================
_LLM_CACHE = {}

# ================= TRACED LLM CALL =================
@traceable(
    name="Groq-LLM-Call",
    tags=["groq", "llm", "chat", "milestone1"]
)
def call_llm(prompt: str) -> str:
    """
    Groq LLM call with LangSmith tracing
    """

    # Cache hit (still traced)
    if prompt in _LLM_CACHE:
        return _LLM_CACHE[prompt]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=256
        )

        answer = response.choices[0].message.content.strip()
        _LLM_CACHE[prompt] = answer
        return answer

    except Exception as e:
        return f"❌ LLM ERROR: {str(e)}"


# ================= CLEANER =================
def clean_text(text: str) -> str:
    return text.strip()
