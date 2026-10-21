import os
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("LLM_PROVIDER", "claude")


def ask_llm(prompt: str) -> str:
    """Send a prompt to the chosen AI model and return its text answer."""
    if PROVIDER == "claude":
        import anthropic
        client = anthropic.Anthropic()
        message = client.messages.create(
            model=os.getenv("CLAUDE_MODEL", "claude-haiku-5-5"),
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        if message.stop_reason == "max_tokens":
            raise ValueError("Answer was cut off (max_tokens reached)")
        return "".join(
            block.text for block in message.content if block.type == "text"
        )

    if PROVIDER == "ollama":
        import ollama
        response = ollama.chat(
            model=os.getenv("OLLAMA_MODEL", "llama3.2"),
            messages=[{"role": "user", "content": prompt}],
            format="json",  # ask Ollama to answer in JSON
        )
        return response.message.content

    raise ValueError(f"Unknown LLM_PROVIDER: {PROVIDER}")