"""
Unit tests for error handling module
"""

import unittest
from error_handler import (
    validate_input,
    handle_ollama_error,
    handle_audio_error,
    PodcastGenerationError,
    OllamaConnectionError
)


class TestErrorHandler(unittest.TestCase):
    
    def test_validate_input_empty_content(self):
        """Test validation fails for empty content"""
        error = validate_input("")
        self.assertIsNotNone(error)
        self.assertIn("empty", error.lower())
    
    def test_validate_input_short_content(self):
        """Test validation fails for too short content"""
        error = validate_input("Short")
        self.assertIsNotNone(error)
        self.assertIn("short", error.lower())
    
    def test_validate_input_long_content(self):
        """Test validation fails for too long content"""
        error = validate_input("x" * 60000)
        self.assertIsNotNone(error)
        self.assertIn("long", error.lower())
    
    def test_validate_input_valid_content(self):
        """Test validation passes for valid content"""
        content = "This is a valid blog post with enough content to pass validation."
        error = validate_input(content)
        self.assertIsNone(error)
    
    def test_validate_input_long_title(self):
        """Test validation fails for too long title"""
        content = "Valid content here with enough characters to pass."
        title = "x" * 250
        error = validate_input(content, title)
        self.assertIsNotNone(error)
        self.assertIn("title", error.lower())
    
    def test_handle_ollama_error_connection(self):
        """Test handling of connection errors"""
        error = Exception("Connection refused")
        result = handle_ollama_error(error)
        self.assertFalse(result['success'])
        self.assertIn('connect', result['error'].lower())
    
    def test_handle_ollama_error_model(self):
        """Test handling of model not found errors"""
        error = Exception("Model not found")
        result = handle_ollama_error(error)
        self.assertFalse(result['success'])
        self.assertIn('model', result['error'].lower())
    
    def test_handle_audio_error(self):
        """Test handling of audio generation errors"""
        error = Exception("Audio processing failed")
        result = handle_audio_error(error)
        self.assertFalse(result['success'])
        self.assertIn('audio', result['error'].lower())
    
    def test_custom_exceptions(self):
        """Test custom exception classes"""
        with self.assertRaises(PodcastGenerationError):
            raise PodcastGenerationError("Test error")
        
        with self.assertRaises(OllamaConnectionError):
            raise OllamaConnectionError("Connection failed")


if __name__ == '__main__':
    unittest.main()
