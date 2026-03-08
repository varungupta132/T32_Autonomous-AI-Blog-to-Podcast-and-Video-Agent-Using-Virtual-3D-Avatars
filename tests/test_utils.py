"""
Unit tests for utility functions
"""

import unittest
from utils import (
    clean_script_text,
    normalize_speaker_labels,
    validate_script_lines,
    format_filename
)


class TestUtils(unittest.TestCase):
    
    def test_clean_script_text_removes_emojis(self):
        """Test that emojis are removed from script"""
        script = "Hello 🎙️ World 🎉"
        cleaned = clean_script_text(script)
        self.assertNotIn('🎙️', cleaned)
        self.assertNotIn('🎉', cleaned)
    
    def test_clean_script_text_removes_stage_directions(self):
        """Test that stage directions are removed"""
        script = "Host: Hello *laughs* everyone (smiling)"
        cleaned = clean_script_text(script)
        self.assertNotIn('*laughs*', cleaned)
        self.assertNotIn('(smiling)', cleaned)
    
    def test_normalize_speaker_labels(self):
        """Test speaker label normalization"""
        script = "Host 1: Hello\nHost 2: Hi there"
        normalized = normalize_speaker_labels(script)
        self.assertIn('Alex:', normalized)
        self.assertIn('Sam:', normalized)
        self.assertNotIn('Host 1:', normalized)
    
    def test_validate_script_lines(self):
        """Test script line validation"""
        script = "Alex: This is valid\nSam: Also valid\nInvalid line\n: No speaker"
        lines = validate_script_lines(script)
        self.assertEqual(len(lines), 2)
        self.assertTrue(all(':' in line for line in lines))
    
    def test_format_filename(self):
        """Test filename formatting"""
        filename = format_filename("My Podcast", "co-host", "global", "txt")
        self.assertIn("podcast", filename)
        self.assertIn("co-host", filename)
        self.assertIn("global", filename)
        self.assertTrue(filename.endswith(".txt"))


if __name__ == '__main__':
    unittest.main()
