#!/usr/bin/env python3
"""
Unit tests for read_me_later.py
"""

import unittest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys
import io
import time

# Add the current directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import read_me_later


class TestReadMeLater(unittest.TestCase):
    """Test cases for read_me_later.py"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_webhook = "https://hooks.slack.com/services/TEST123/BOT456/abcdefghijklmnopqrstuvwxyz"
        self.test_message = "Test message"
        
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.test_creds_file = os.path.join(self.temp_dir, "test_creds.json")
        
        # Create test credentials file
        with open(self.test_creds_file, 'w') as f:
            json.dump({"webhook": self.test_webhook}, f)

    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temporary files
        if os.path.exists(self.test_creds_file):
            os.remove(self.test_creds_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
        
        # Clean up rate limit file if it exists
        rate_limit_file = os.path.expanduser("~/.read_me_later_rate_limit")
        if os.path.exists(rate_limit_file):
            os.remove(rate_limit_file)

    def test_load_json_file_valid(self):
        """Test loading a valid JSON credentials file"""
        webhook = read_me_later.load_json_file(self.test_creds_file)
        self.assertEqual(webhook, self.test_webhook)

    def test_load_json_file_invalid_path(self):
        """Test loading a non-existent file"""
        webhook = read_me_later.load_json_file("/nonexistent/file.json")
        self.assertIsNone(webhook)

    def test_load_json_file_invalid_json(self):
        """Test loading a file with invalid JSON"""
        invalid_json_file = os.path.join(self.temp_dir, "invalid.json")
        with open(invalid_json_file, 'w') as f:
            f.write("invalid json content")
        
        webhook = read_me_later.load_json_file(invalid_json_file)
        self.assertIsNone(webhook)
        
        # Clean up
        os.remove(invalid_json_file)

    def test_load_json_file_missing_webhook(self):
        """Test loading a JSON file without webhook key"""
        invalid_creds_file = os.path.join(self.temp_dir, "no_webhook.json")
        with open(invalid_creds_file, 'w') as f:
            json.dump({"other_key": "value"}, f)
        
        webhook = read_me_later.load_json_file(invalid_creds_file)
        self.assertIsNone(webhook)
        
        # Clean up
        os.remove(invalid_creds_file)

    @patch('read_me_later.requests.post')
    def test_call_slack_success(self, mock_post):
        """Test successful Slack API call"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = read_me_later.call_slack(self.test_message, self.test_webhook)
        self.assertEqual(result, 200)
        
        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            self.test_webhook, 
            json={"text": self.test_message},
            headers={'User-Agent': 'read_me_later/1.2', 'Content-Type': 'application/json'},
            timeout=10
        )

    @patch('read_me_later.requests.post')
    def test_call_slack_failure(self, mock_post):
        """Test failed Slack API call"""
        # Mock failed response
        from requests.exceptions import RequestException
        mock_post.side_effect = RequestException("Network error")
        
        result = read_me_later.call_slack(self.test_message, self.test_webhook)
        self.assertIsNone(result)

    @patch('read_me_later.requests.post')
    def test_call_slack_timeout(self, mock_post):
        """Test Slack API call timeout"""
        from requests.exceptions import Timeout
        mock_post.side_effect = Timeout("Request timed out")
        
        result = read_me_later.call_slack(self.test_message, self.test_webhook)
        self.assertIsNone(result)

    def test_call_slack_missing_message(self):
        """Test call_slack with missing message"""
        result = read_me_later.call_slack("", self.test_webhook)
        self.assertIsNone(result)

    def test_call_slack_missing_webhook(self):
        """Test call_slack with missing webhook"""
        result = read_me_later.call_slack(self.test_message, "")
        self.assertIsNone(result)

    @patch('read_me_later.call_slack')
    def test_process_message_with_webhook_arg(self, mock_call_slack):
        """Test process_message with webhook argument"""
        mock_call_slack.return_value = 200
        
        # Create mock args
        args = MagicMock()
        args.creds_file = None
        args.webhook = self.test_webhook
        args.message = self.test_message
        
        result = read_me_later.process_message(args)
        self.assertEqual(result, 0)
        mock_call_slack.assert_called_once_with(self.test_message, self.test_webhook)

    @patch('read_me_later.call_slack')
    def test_process_message_with_creds_file(self, mock_call_slack):
        """Test process_message with credentials file"""
        mock_call_slack.return_value = 200
        
        # Create mock args
        args = MagicMock()
        args.creds_file = self.test_creds_file
        args.webhook = None
        args.message = self.test_message
        
        result = read_me_later.process_message(args)
        self.assertEqual(result, 0)
        mock_call_slack.assert_called_once_with(self.test_message, self.test_webhook)

    @patch('read_me_later.call_slack')
    @patch('os.path.exists')
    def test_process_message_no_credentials(self, mock_exists, mock_call_slack):
        """Test process_message with no credentials provided"""
        # Mock that no config files exist
        mock_exists.return_value = False
        
        # Create mock args
        args = MagicMock()
        args.creds_file = None
        args.webhook = None
        args.message = self.test_message
        
        result = read_me_later.process_message(args)
        self.assertEqual(result, 2)  # Should return error code for missing credentials
        mock_call_slack.assert_not_called()

    @patch('read_me_later.call_slack')
    def test_process_message_slack_failure(self, mock_call_slack):
        """Test process_message when Slack call fails"""
        mock_call_slack.return_value = None
        
        # Create mock args
        args = MagicMock()
        args.creds_file = None
        args.webhook = self.test_webhook
        args.message = self.test_message
        
        result = read_me_later.process_message(args)
        self.assertEqual(result, 3)  # Should return error code for Slack failure

    @patch('sys.argv', ['read_me_later.py', '--help'])
    def test_cli_parser_help(self):
        """Test CLI parser with help argument"""
        with self.assertRaises(SystemExit):
            read_me_later.cli_parser(['read_me_later.py', '--help'])

    def test_cli_parser_missing_message(self):
        """Test CLI parser with missing required message"""
        with self.assertRaises(SystemExit):
            read_me_later.cli_parser(['read_me_later.py'])

    def test_cli_parser_valid_args(self):
        """Test CLI parser with valid arguments"""
        with patch('sys.argv', ['read_me_later.py', '--webhook', self.test_webhook, '--message', self.test_message]):
            args = read_me_later.cli_parser(['read_me_later.py', '--webhook', self.test_webhook, '--message', self.test_message])
            
            self.assertEqual(args.webhook, self.test_webhook)
            self.assertEqual(args.message, self.test_message)
            self.assertIsNone(args.creds_file)

    def test_cli_parser_with_creds_file(self):
        """Test CLI parser with credentials file"""
        with patch('sys.argv', ['read_me_later.py', '--creds-file', self.test_creds_file, '--message', self.test_message]):
            args = read_me_later.cli_parser(['read_me_later.py', '--creds-file', self.test_creds_file, '--message', self.test_message])
            
            self.assertEqual(args.creds_file, self.test_creds_file)
            self.assertEqual(args.message, self.test_message)
            self.assertIsNone(args.webhook)

    @patch('read_me_later.process_message')
    def test_main_success(self, mock_process_message):
        """Test main function success"""
        mock_process_message.return_value = 0
        
        with patch('sys.argv', ['read_me_later.py', '--webhook', self.test_webhook, '--message', self.test_message]):
            result = read_me_later.main()
            self.assertEqual(result, 0)

    @patch('read_me_later.process_message')
    def test_main_failure(self, mock_process_message):
        """Test main function failure"""
        mock_process_message.return_value = 1
        
        with patch('sys.argv', ['read_me_later.py', '--webhook', self.test_webhook, '--message', self.test_message]):
            result = read_me_later.main()
            self.assertEqual(result, 1)

    @patch('read_me_later.cli_parser')
    def test_main_parser_failure(self, mock_cli_parser):
        """Test main function with parser failure"""
        mock_cli_parser.return_value = None
        
        result = read_me_later.main()
        self.assertEqual(result, 1)

    # Security feature tests
    def test_validate_webhook_url_valid(self):
        """Test webhook URL validation with valid URL"""
        valid_urls = [
            "https://hooks.slack.com/services/TEST123/BOT456/abcdefghijklmnopqrstuvwxyz",
            "https://hooks.slack.com/services/ABC123/DEF456/ghi789jkl012mno345pqr678stu901vwx234yz",
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(read_me_later.validate_webhook_url(url))

    def test_validate_webhook_url_invalid(self):
        """Test webhook URL validation with invalid URLs"""
        invalid_urls = [
            None,
            "",
            "not-a-url",
            "https://example.com/webhook",
            "https://hooks.slack.com/invalid",
            "http://hooks.slack.com/services/T123/B123/abc",
            "https://hooks.slack.com/services/T123/B123/abc/extra",
            "https://hooks.slack.com/services/T123/B123",
        ]
        
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(read_me_later.validate_webhook_url(url))

    def test_validate_message_length_valid(self):
        """Test message length validation with valid messages"""
        valid_messages = [
            "Short message",
            "A" * 1000,
            "A" * read_me_later.MAX_MESSAGE_LENGTH,
        ]
        
        for message in valid_messages:
            with self.subTest(message_length=len(message)):
                self.assertTrue(read_me_later.validate_message_length(message))

    def test_validate_message_length_invalid(self):
        """Test message length validation with invalid messages"""
        invalid_messages = [
            None,
            "",
            "A" * (read_me_later.MAX_MESSAGE_LENGTH + 1),
            "A" * 5000,
        ]
        
        for message in invalid_messages:
            with self.subTest(message_length=len(message) if message else 0):
                self.assertFalse(read_me_later.validate_message_length(message))

    def test_check_rate_limit_first_request(self):
        """Test rate limiting on first request"""
        # Clean up any existing rate limit file
        rate_limit_file = os.path.expanduser("~/.read_me_later_rate_limit")
        if os.path.exists(rate_limit_file):
            os.remove(rate_limit_file)
        
        # First request should pass
        self.assertTrue(read_me_later.check_rate_limit())
        
        # Verify file was created
        self.assertTrue(os.path.exists(rate_limit_file))

    def test_check_rate_limit_multiple_requests(self):
        """Test rate limiting with multiple requests"""
        # Clean up any existing rate limit file
        rate_limit_file = os.path.expanduser("~/.read_me_later_rate_limit")
        if os.path.exists(rate_limit_file):
            os.remove(rate_limit_file)
        
        # Make multiple requests within the limit
        for i in range(read_me_later.RATE_LIMIT_MAX_REQUESTS):
            with self.subTest(request_number=i+1):
                self.assertTrue(read_me_later.check_rate_limit())

    def test_check_rate_limit_exceeded(self):
        """Test rate limiting when limit is exceeded"""
        # Clean up any existing rate limit file
        rate_limit_file = os.path.expanduser("~/.read_me_later_rate_limit")
        if os.path.exists(rate_limit_file):
            os.remove(rate_limit_file)
        
        # Make requests up to the limit
        for i in range(read_me_later.RATE_LIMIT_MAX_REQUESTS):
            read_me_later.check_rate_limit()
        
        # Next request should be rate limited
        self.assertFalse(read_me_later.check_rate_limit())

    @patch('read_me_later.call_slack')
    def test_process_message_invalid_webhook(self, mock_call_slack):
        """Test process_message with invalid webhook URL"""
        # Create mock args with invalid webhook
        args = MagicMock()
        args.creds_file = None
        args.webhook = "https://example.com/invalid-webhook"
        args.message = self.test_message
        
        result = read_me_later.process_message(args)
        self.assertEqual(result, 6)  # Should return error code for invalid webhook
        mock_call_slack.assert_not_called()

    @patch('read_me_later.call_slack')
    def test_process_message_too_long(self, mock_call_slack):
        """Test process_message with message too long"""
        # Create mock args with message too long
        args = MagicMock()
        args.creds_file = None
        args.webhook = self.test_webhook
        args.message = "A" * (read_me_later.MAX_MESSAGE_LENGTH + 1)
        
        result = read_me_later.process_message(args)
        self.assertEqual(result, 4)  # Should return error code for message too long
        mock_call_slack.assert_not_called()

    @patch('read_me_later.check_rate_limit')
    @patch('read_me_later.call_slack')
    def test_process_message_rate_limited(self, mock_call_slack, mock_rate_limit):
        """Test process_message when rate limited"""
        mock_rate_limit.return_value = False
        
        # Create mock args
        args = MagicMock()
        args.creds_file = None
        args.webhook = self.test_webhook
        args.message = self.test_message
        
        result = read_me_later.process_message(args)
        self.assertEqual(result, 5)  # Should return error code for rate limit
        mock_call_slack.assert_not_called()

    @patch('builtins.open')
    def test_check_rate_limit_failure(self, mock_open):
        """Test rate limiting when file operations fail"""
        # Mock file operations to fail
        mock_open.side_effect = Exception("File system error")
        
        # Should fail open (allow the request) when rate limiting fails
        result = read_me_later.check_rate_limit()
        self.assertTrue(result)

    @patch('read_me_later.load_json_file')
    @patch('os.path.exists')
    def test_process_message_config_loading_feedback(self, mock_exists, mock_load_json):
        """Test that config loading provides proper feedback"""
        # Mock that default config exists
        mock_exists.return_value = True
        mock_load_json.return_value = self.test_webhook
        
        # Capture stdout to check print statements
        from io import StringIO
        import sys
        
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            # Create mock args
            args = MagicMock()
            args.creds_file = None
            args.webhook = None
            args.message = self.test_message
            
            # This should trigger the config loading feedback
            with patch('read_me_later.call_slack') as mock_call_slack:
                mock_call_slack.return_value = 200
                result = read_me_later.process_message(args)
            
            # Check that the feedback message was printed
            output = captured_output.getvalue()
            self.assertIn("Loading webhook from", output)
            self.assertEqual(result, 0)
            
        finally:
            sys.stdout = old_stdout

    @patch('read_me_later.load_json_file')
    @patch('os.path.exists')
    def test_process_message_docker_config_loading_feedback(self, mock_exists, mock_load_json):
        """Test that Docker config loading provides proper feedback"""
        # Mock that default config doesn't exist but Docker config does
        def exists_side_effect(path):
            if "~/.read_me_later.json" in path:
                return False
            elif "/app/.read_me_later.json" in path:
                return True
            return False
        
        mock_exists.side_effect = exists_side_effect
        mock_load_json.return_value = self.test_webhook
        
        # Capture stdout to check print statements
        from io import StringIO
        import sys
        
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            # Create mock args
            args = MagicMock()
            args.creds_file = None
            args.webhook = None
            args.message = self.test_message
            
            # This should trigger the Docker config loading feedback
            with patch('read_me_later.call_slack') as mock_call_slack:
                mock_call_slack.return_value = 200
                result = read_me_later.process_message(args)
            
            # Check that the Docker config feedback message was printed
            output = captured_output.getvalue()
            self.assertIn("Loading webhook from /app/.read_me_later.json", output)
            self.assertEqual(result, 0)
            
        finally:
            sys.stdout = old_stdout

    def test_validate_webhook_url_edge_cases(self):
        """Test webhook URL validation with edge cases"""
        edge_cases = [
            # Almost valid but wrong protocol
            "http://hooks.slack.com/services/TEST123/BOT456/abcdefghijklmnopqrstuvwxyz",
            # Almost valid but extra path
            "https://hooks.slack.com/services/TEST123/BOT456/abcdefghijklmnopqrstuvwxyz/extra",
            # Almost valid but missing parts
            "https://hooks.slack.com/services/TEST123/BOT456",
            "https://hooks.slack.com/services/TEST123",
            # Valid format but wrong characters
            "https://hooks.slack.com/services/TEST123/BOT456/abcdefghijklmnopqrstuvwxyz!",
            "https://hooks.slack.com/services/TEST123/BOT456/abcdefghijklmnopqrstuvwxyz#",
            # Wrong domain
            "https://hook.slack.com/services/TEST123/BOT456/abcdefghijklmnopqrstuvwxyz",
            "https://hooks.slack.org/services/TEST123/BOT456/abcdefghijklmnopqrstuvwxyz",
            # Wrong path structure
            "https://hooks.slack.com/api/services/TEST123/BOT456/abcdefghijklmnopqrstuvwxyz",
        ]
        
        for url in edge_cases:
            with self.subTest(url=url):
                self.assertFalse(read_me_later.validate_webhook_url(url))

    def test_validate_webhook_url_case_sensitivity(self):
        """Test webhook URL validation with different case combinations"""
        # Valid with mixed case in the token part
        valid_mixed_case = "https://hooks.slack.com/services/TEST123/BOT456/AbCdEfGhIjKlMnOpQrStUvWxYz"
        self.assertTrue(read_me_later.validate_webhook_url(valid_mixed_case))
        
        # Invalid with lowercase in team/channel parts
        invalid_lowercase = "https://hooks.slack.com/services/test123/bot456/abcdefghijklmnopqrstuvwxyz"
        self.assertFalse(read_me_later.validate_webhook_url(invalid_lowercase))

    @patch('read_me_later.check_rate_limit')
    @patch('read_me_later.call_slack')
    def test_process_message_all_security_checks_pass(self, mock_call_slack, mock_rate_limit):
        """Test that all security checks pass for a valid request"""
        mock_rate_limit.return_value = True
        mock_call_slack.return_value = 200
        
        # Create mock args with valid data
        args = MagicMock()
        args.creds_file = None
        args.webhook = self.test_webhook
        args.message = "Valid message"
        
        result = read_me_later.process_message(args)
        self.assertEqual(result, 0)
        
        # Verify all security checks were called
        mock_rate_limit.assert_called_once()
        mock_call_slack.assert_called_once_with("Valid message", self.test_webhook)


if __name__ == '__main__':
    unittest.main() 