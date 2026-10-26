import json

import pytest
from pydantic import ValidationError

from analysis import ALLOWED_TOPICS, build_prompt, parse_response

VALID_SUMMARY = (
    "This paper studies robot grasping with tactile sensors. "
    "A new learning method improves success on unseen objects."
)


def make_answer(summary=VALID_SUMMARY, topics=("manipulation",), difficulty=3):
    """Build a fake AI answer as JSON text."""
    return json.dumps(
        {"summary": summary, "topics": list(topics), "difficulty": difficulty}
    )


# ---------- Valid answers ----------

def test_valid_answer_passes():
    result = parse_response(make_answer())
    assert result.summary == VALID_SUMMARY
    assert result.topics == ["manipulation"]
    assert result.difficulty == 3


def test_extra_text_around_json_is_ignored():
    text = "Here is the JSON:\n" + make_answer() + "\nHope this helps!"
    result = parse_response(text)
    assert result.topics == ["manipulation"]


def test_topics_are_cleaned_and_deduplicated():
    result = parse_response(make_answer(topics=[" Manipulation ", "manipulation", "SLAM"]))
    assert result.topics == ["manipulation", "slam"]


def test_unknown_topic_is_dropped_if_a_valid_one_exists():
    result = parse_response(make_answer(topics=["manipulation", "cooking"]))
    assert result.topics == ["manipulation"]


# ---------- Invalid answers ----------

def test_only_unknown_topics_are_rejected():
    with pytest.raises(ValidationError):
        parse_response(make_answer(topics=["cooking"]))


@pytest.mark.parametrize("difficulty", [0, 6])
def test_difficulty_outside_1_to_5_is_rejected(difficulty):
    with pytest.raises(ValidationError):
        parse_response(make_answer(difficulty=difficulty))


def test_too_many_topics_are_rejected():
    four_topics = ["manipulation", "slam", "control", "navigation"]
    with pytest.raises(ValidationError):
        parse_response(make_answer(topics=four_topics))


def test_summary_too_long_is_rejected():
    with pytest.raises(ValidationError):
        parse_response(make_answer(summary="word " * 300))


def test_text_without_json_fails():
    with pytest.raises(ValueError, match="No JSON"):
        parse_response("Sorry, I cannot help with that.")


def test_broken_json_fails():
    with pytest.raises(ValueError):
        parse_response('{"summary": "missing the end"')


# ---------- Prompt ----------

def test_prompt_contains_title_abstract_and_all_topics():
    prompt = build_prompt("My Title", "My abstract text")
    assert "My Title" in prompt
    assert "My abstract text" in prompt
    for topic in ALLOWED_TOPICS:
        assert topic in prompt