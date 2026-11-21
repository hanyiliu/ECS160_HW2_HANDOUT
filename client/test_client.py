from unittest.mock import MagicMock, patch

import main


def mock_moderation_response(result):
    response = MagicMock()
    response.json.return_value = {"result": result}
    return response


def test_passing_post_is_printed_with_hashtag(capsys):
    post = main.Post("c0", "alice", "url", "t", "Posted", 0, 5)

    with patch.object(main.requests, "post", return_value=mock_moderation_response("#post")) as mock_post:
        main.process_post(post, 1)

    assert "Posted #post" in capsys.readouterr().out
    assert mock_post.call_args.kwargs["json"] == {"post_content": "Posted"}


def test_failed_post_is_printed_as_deleted(capsys):
    post = main.Post("c0", "bob", "url", "t", "Crypto here!", 0, 5)

    with patch.object(main.requests, "post", return_value=mock_moderation_response("FAILED")):
        main.process_post(post, 1)

    out = capsys.readouterr().out
    assert "[DELETED]" in out
    assert "Crypto here!" not in out
