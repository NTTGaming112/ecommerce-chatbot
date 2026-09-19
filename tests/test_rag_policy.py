from app.core.rag_policy import is_greeting, requests_web_search, resolve_route


def test_standalone_greeting_is_detected():
    assert is_greeting("Xin chào!")
    assert is_greeting("Bạn là ai?")


def test_substring_hi_does_not_misclassify_current_question():
    question = "Hiện tại chính sách đổi trả là gì?"

    assert not is_greeting(question)
    assert requests_web_search(question)


def test_explicit_vector_mode_is_honored():
    decision = resolve_route("general", "vector")

    assert decision.intent == "retrieval"
    assert decision.search_mode == "vector"
    assert decision.answer_mode == "deep"


def test_general_question_uses_retrieval_in_strict_mode():
    decision = resolve_route("general", "auto")

    assert decision.search_mode == "vector"
    assert decision.answer_mode == "deep"
