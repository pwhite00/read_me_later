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

# Add the current directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import read_me_later


class TestReadMeLater(unittest.TestCase):
    """Test cases for read_me_later.py"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_webhook = "https://hooks.slack.com/services/test/test/test"
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
            json={"text": self.test_message}
        )

    @patch('read_me_later.requests.post')
    def test_call_slack_failure(self, mock_post):
        """Test failed Slack API call"""
        # Mock failed response
        mock_post.side_effect = Exception("Network error")
        
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
        """Test main function success path"""
        mock_process_message.return_value = 0
        
        with patch('sys.argv', ['read_me_later.py', '--webhook', self.test_webhook, '--message', self.test_message]):
            result = read_me_later.main()
            self.assertEqual(result, 0)

    @patch('read_me_later.process_message')
    def test_main_failure(self, mock_process_message):
        """Test main function failure path"""
        mock_process_message.return_value = 2
        
        with patch('sys.argv', ['read_me_later.py', '--webhook', self.test_webhook, '--message', self.test_message]):
            result = read_me_later.main()
            self.assertEqual(result, 2)

    @patch('read_me_later.cli_parser')
    def test_main_parser_failure(self, mock_cli_parser):
        """Test main function when parser fails"""
        mock_cli_parser.return_value = None
        
        with patch('sys.argv', ['read_me_later.py', '--invalid-arg']):
            result = read_me_later.main()
            self.assertEqual(result, 1)


if __name__ == '__main__':
    unittest.main() 