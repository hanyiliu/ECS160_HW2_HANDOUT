"""Unit tests for the hashtagging service. Gemini is mocked, so no API key or network is needed."""
from unittest.mock import MagicMock, patch

import hashtagging_pb2
import hashtagging_service as hs


def test_request_returns_hashtag():
    mock_gemini = MagicMock()
    mock_gemini.models.generate_content.return_value.text = "#post"

    with patch.object(hs, "get_client", return_value=mock_gemini):
        request = hashtagging_pb2.HashtagRequest(post_content="Posted")
        response = hs.HashtagServiceServicer().GetHashtag(request, context=MagicMock())

    assert response.hashtag == "#post"
    prompt = mock_gemini.models.generate_content.call_args.kwargs["contents"]
    assert "Posted" in prompt


def test_gemini_failure_returns_default():
    mock_gemini = MagicMock()
    mock_gemini.models.generate_content.side_effect = RuntimeError("Unavailable")

    with patch.object(hs, "get_client", return_value=mock_gemini):
        assert hs.generate_hashtag("Posted") == hs.DEFAULT
