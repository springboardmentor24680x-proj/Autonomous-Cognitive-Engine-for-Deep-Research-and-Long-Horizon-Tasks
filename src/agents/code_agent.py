from langsmith import traceable
from utils.llm import call_llm, clean_text

# ================= STEP 1: INTENT DETECTION =================

@traceable(name="Code Intent Detection")
def detect_code_intent(text: str):
    low = text.lower()

    if any(word in low for word in ["debug", "error", "fix"]):
        return "debug"

    if any(word in low for word in ["explain", "how", "why"]):
        return "explain"

    return "write"

# ================= STEP 2: LANGUAGE DETECTION =================

@traceable(name="Language Detection")
def detect_language(text: str):
    low = text.lower()

    if "python" in low:
        return "python"
    if "java" in low:
        return "java"
    if "javascript" in low or "js" in low:
        return "javascript"
    if "c++" in low:
        return "cpp"

    return "generic"

# ================= STEP 3: PROMPT BUILDER =================

@traceable(name="Code Prompt Builder")
def build_code_prompt(text, intent, language):
    return f"""
You are an expert {language} software engineer.

User request:
{text}

Detected intent: {intent}

Instructions:
- If intent is WRITE: generate correct and optimized code
- If intent is DEBUG: explain the issue and fix it
- If intent is EXPLAIN: explain step-by-step with examples
- Use clean formatting and comments
"""

# ================= STEP 4: LLM REASONING =================

@traceable(name="Code LLM Reasoning")
def llm_reasoning(prompt):
    return call_llm(prompt)

# ================= STEP 5: OUTPUT CLEANING =================

@traceable(name="Code Output Cleaning")
def clean_output(raw):
    return clean_text(raw)

# ================= MAIN CODE AGENT =================

@traceable(name="Code-Assistant-Agent")
def code_agent(user_text: str):
    """
    Handles:
    - code writing
    - debugging
    - explanation
    """

    intent = detect_code_intent(user_text)
    language = detect_language(user_text)
    prompt = build_code_prompt(user_text, intent, language)
    raw = llm_reasoning(prompt)
    final = clean_output(raw)

    return final
