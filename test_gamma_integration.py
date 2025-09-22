#!/usr/bin/env python3
"""
Test script for Gamma API integration in Victoria Terminal.

This script tests the Gamma API client and CLI functionality.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from gamma_client import GammaClient, GammaAPIError


class TestGammaClient(unittest.TestCase):
    """Test cases for the GammaClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "sk-gamma-test123456"
        self.client = GammaClient(self.api_key)
    
    def test_client_initialization(self):
        """Test that the client initializes correctly."""
        self.assertEqual(self.client.api_key, self.api_key)
        self.assertEqual(
            self.client.session.headers['X-API-KEY'],
            self.api_key
        )
        self.assertEqual(
            self.client.session.headers['Content-Type'],
            'application/json'
        )
    
    @patch('gamma_client.requests.Session.post')
    def test_generate_presentation_success(self, mock_post):
        """Test successful presentation generation."""
        mock_response = Mock()
        mock_response.json.return_value = {"generationId": "test-gen-123"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.client.generate_presentation(
            input_text="Test presentation content",
            theme_name="Test Theme"
        )
        
        self.assertEqual(result, "test-gen-123")
        mock_post.assert_called_once()
        
        # Check the request payload
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        self.assertEqual(payload['inputText'], "Test presentation content")
        self.assertEqual(payload['themeName'], "Test Theme")
    
    @patch('gamma_client.requests.Session.post')
    def test_generate_presentation_api_error(self, mock_post):
        """Test API error handling in presentation generation."""
        import requests
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("API Error")
        mock_post.return_value = mock_response
        
        with self.assertRaises(GammaAPIError):
            self.client.generate_presentation("Test content")
    
    @patch('gamma_client.requests.Session.get')
    def test_check_generation_status_success(self, mock_get):
        """Test successful status checking."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "completed",
            "url": "https://gamma.app/test"
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.check_generation_status("test-gen-123")
        
        self.assertEqual(result['status'], "completed")
        self.assertEqual(result['url'], "https://gamma.app/test")
    
    @patch('gamma_client.requests.Session.get')
    def test_check_generation_status_error(self, mock_get):
        """Test error handling in status checking."""
        import requests
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("API Error")
        mock_get.return_value = mock_response
        
        with self.assertRaises(GammaAPIError):
            self.client.check_generation_status("test-gen-123")
    
    @patch('gamma_client.GammaClient.check_generation_status')
    @patch('gamma_client.time.sleep')
    def test_wait_for_completion_success(self, mock_sleep, mock_check_status):
        """Test successful completion waiting."""
        mock_check_status.return_value = {
            "status": "completed",
            "url": "https://gamma.app/test"
        }
        
        result = self.client.wait_for_completion("test-gen-123", timeout=10)
        
        self.assertEqual(result['status'], "completed")
        mock_check_status.assert_called_once_with("test-gen-123")
    
    @patch('gamma_client.GammaClient.check_generation_status')
    @patch('gamma_client.time.sleep')
    def test_wait_for_completion_failed(self, mock_sleep, mock_check_status):
        """Test handling of failed generation."""
        mock_check_status.return_value = {
            "status": "failed",
            "error": "Generation failed"
        }
        
        with self.assertRaises(GammaAPIError) as context:
            self.client.wait_for_completion("test-gen-123", timeout=10)
        
        self.assertIn("Generation failed", str(context.exception))
    
    @patch('gamma_client.GammaClient.check_generation_status')
    @patch('gamma_client.time.sleep')
    @patch('gamma_client.time.time')
    def test_wait_for_completion_timeout(self, mock_time, mock_sleep, mock_check_status):
        """Test timeout handling in completion waiting."""
        # Mock time to simulate timeout
        mock_time.side_effect = [0, 0, 400]  # Start, check, timeout
        mock_check_status.return_value = {"status": "pending"}
        
        with self.assertRaises(GammaAPIError) as context:
            self.client.wait_for_completion("test-gen-123", timeout=300)
        
        self.assertIn("timed out", str(context.exception))
    
    @patch('gamma_client.requests.get')
    def test_download_file_success(self, mock_get):
        """Test successful file download."""
        mock_response = Mock()
        mock_response.iter_content.return_value = [b'test content']
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.pdf"
            self.client.download_file("https://example.com/test.pdf", file_path)
            
            self.assertTrue(file_path.exists())
            with open(file_path, 'rb') as f:
                self.assertEqual(f.read(), b'test content')
    
    @patch('gamma_client.requests.get')
    def test_download_file_error(self, mock_get):
        """Test error handling in file download."""
        import requests
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("Download failed")
        mock_get.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.pdf"
            
            with self.assertRaises(GammaAPIError):
                self.client.download_file("https://example.com/test.pdf", file_path)
    
    @patch('gamma_client.GammaClient.wait_for_completion')
    @patch('gamma_client.GammaClient.generate_presentation')
    def test_create_presentation_from_file_success(self, mock_generate, mock_wait):
        """Test successful presentation creation from file."""
        mock_generate.return_value = "test-gen-123"
        mock_wait.return_value = {
            "status": "completed",
            "url": "https://gamma.app/test"
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test input file
            input_file = Path(temp_dir) / "input.txt"
            with open(input_file, 'w') as f:
                f.write("Test presentation content")
            
            output_dir = Path(temp_dir) / "output"
            
            result = self.client.create_presentation_from_file(
                input_file=input_file,
                output_dir=output_dir
            )
            
            # Should create URL file since no export format specified
            self.assertTrue(result.name.endswith('_presentation_url.txt'))
            self.assertTrue(result.exists())
    
    def test_create_presentation_from_file_missing_input(self):
        """Test error handling for missing input file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = Path(temp_dir) / "nonexistent.txt"
            output_dir = Path(temp_dir) / "output"
            
            with self.assertRaises(GammaAPIError) as context:
                self.client.create_presentation_from_file(
                    input_file=input_file,
                    output_dir=output_dir
                )
            
            self.assertIn("Input file not found", str(context.exception))


class TestGammaCLI(unittest.TestCase):
    """Test cases for the Gamma CLI functionality."""
    
    @patch('gamma_cli.APP_HOME', Path("/tmp/test_victoria"))
    @patch('gamma_cli.load_dotenv')
    def test_load_environment(self, mock_load_dotenv):
        """Test environment loading."""
        from gamma_cli import load_environment
        
        # Create a mock .env file path
        with patch('gamma_cli.APP_HOME') as mock_app_home:
            mock_env_file = Mock()
            mock_env_file.exists.return_value = True
            mock_app_home.__truediv__.return_value = mock_env_file
            
            load_environment()
            
            mock_load_dotenv.assert_called_once()
    
    @patch('gamma_cli.console')
    @patch('gamma_cli.os.environ.get')
    def test_get_gamma_client_no_api_key(self, mock_environ_get, mock_console):
        """Test error handling when no API key is available."""
        from gamma_cli import get_gamma_client
        
        mock_environ_get.return_value = None
        
        with self.assertRaises(SystemExit):
            get_gamma_client()
    
    @patch('gamma_cli.os.environ.get')
    def test_get_gamma_client_success(self, mock_environ_get):
        """Test successful client creation."""
        from gamma_cli import get_gamma_client
        
        mock_environ_get.return_value = "sk-gamma-test123"
        client = get_gamma_client()
        
        self.assertIsInstance(client, GammaClient)
        self.assertEqual(client.api_key, "sk-gamma-test123")


def run_tests():
    """Run all tests."""
    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestGammaClient))
    suite.addTests(loader.loadTestsFromTestCase(TestGammaCLI))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
