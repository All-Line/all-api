from unittest.mock import patch

from scripts.slack_message import send_message_to_slack


@patch("scripts.slack_message.argparse")
@patch("scripts.slack_message.requests")
@patch("scripts.slack_message.env")
def test_send_message_to_slack(mock_env, mock_requests, mock_argparse):
    send_message_to_slack()

    mock_argparse.ArgumentParser.assert_called_once()

    parser = mock_argparse.ArgumentParser.return_value

    parser.add_argument.assert_called_once_with("message", type=str)
    parser.parse_args.assert_called_once()

    args = parser.parse_args.return_value

    mock_env.assert_called_once_with("SLACK_MESSAGE_URL")

    mock_requests.post.assert_called_once_with(
        mock_env.return_value, json={"text": args.message}
    )
