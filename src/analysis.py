import json
from pydantic import BaseModel, Field, field_validator

ALLOWED_TOPICS = [
    "manipulation", "locomotion", "navigation", "aerial robots",
    "humanoids", "reinforcement learning", "perception", "slam",
    "human-robot interaction", "autonomous driving", "multi-robot",
    "control", "simulation", "foundation models", "other",
]


class PaperAnalysis(BaseModel):
    """The exact shape we expect from the AI. Anything else is rejected."""
    summary: str = Field(min_length=20, max_length=800)
    topics: list[str] = Field(min_length=1, max_length=3)
    difficulty: int = Field(ge=1, le=5)  # ge = greater or equal, le = less or equal

    @field_validator("topics")
    @classmethod
    def only_allowed_topics(cls, topics):
        cleaned = [t.strip().lower() for t in topics]
        valid = [t for t in cleaned if t in ALLOWED_TOPICS]
        if not valid:
            raise ValueError(f"No allowed topics in {topics}")
        return list(dict.fromkeys(valid))  # remove duplicates, keep order


def build_prompt(title: str, abstract: str) -> str:
    return f"""You are helping students understand robotics research papers.

Read this paper and answer with ONLY a JSON object, no other text.

Title: {title}
Abstract: {abstract}

JSON format:
{{
 "summary": "2-3 short, simple sentences, MAXIMUM 60 words: what problem, what method, what result",
  "topics": ["1 to 3 topics, chosen ONLY from the allowed list"],
  "difficulty": 1-5 (1 = easy for a bachelor student, 5 = very advanced)
}}

Allowed topics: {", ".join(ALLOWED_TOPICS)}"""


def parse_response(text: str) -> PaperAnalysis:
    """Turn the AI's text into a checked PaperAnalysis object."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON found in AI response")
    data = json.loads(text[start:end + 1])
    return PaperAnalysis.model_validate(data)