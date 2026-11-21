from unittest.mock import MagicMock, patch

import moderation_service as ms
from moderation_service import ModerateRequest


def test_clean_post_returns_hashtage():
    mock_stub = MagicMock()
    mock_stub.GetHashtag.return_value.hashtag = "#post"

    with patch.object(ms.hashtagging_pb2_grpc, "HashtagServiceStub", return_value=mock_stub):
        response = ms.moderate(ModerateRequest(post_content="Posted"))

    assert response.result == "#post"
    sent_request = mock_stub.GetHashtag.call_args.args[0]
    assert sent_request.post_content == "Posted"


def test_banned_post_fails():
    mock_stub = MagicMock()

    with patch.object(ms.hashtagging_pb2_grpc, "HashtagServiceStub", return_value=mock_stub):
        response = ms.moderate(ModerateRequest(post_content="Crypto here!"))

    assert response.result == "FAILED"
    mock_stub.GetHashtag.assert_not_called()
