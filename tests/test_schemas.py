import pytest
from pydantic import ValidationError

from app.schemas import QueryInput


def test_query_rejects_unknown_search_mode():
    with pytest.raises(ValidationError):
        QueryInput(session_id="session-1", question="Xin chào", search_mode="invalid")
