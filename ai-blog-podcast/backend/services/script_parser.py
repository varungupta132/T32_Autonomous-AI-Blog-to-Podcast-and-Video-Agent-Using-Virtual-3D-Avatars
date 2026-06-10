from typing import List, Dict
import re

class ScriptParser:
    """Parse podcast script into structured dialogues"""
    
    @staticmethod
    def parse(script: str) -> List[Dict[str, str]]:
        """
        Parse script in format 'SPEAKER: dialogue' into structured list
        Returns: [{"speaker": "HOST", "text": "Welcome..."}, ...]
        """
        dialogues = []
        lines = script.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Match pattern: SPEAKER: text
            match = re.match(r'^([A-Z]+):\s*(.+)$', line)
            if match:
                speaker = match.group(1).strip()
                text = match.group(2).strip()
                
                # Clean text from markdown artifacts
                text = re.sub(r'\*+', '', text)  # Remove asterisks
                text = re.sub(r'#+', '', text)   # Remove hashes
                text = text.strip()
                
                if text:
                    dialogues.append({
                        "speaker": speaker,
                        "text": text
                    })
        
        return dialogues
    
    @staticmethod
    def get_speakers(dialogues: List[Dict[str, str]]) -> List[str]:
        """Extract unique speakers from dialogues"""
        speakers = []
        for dialogue in dialogues:
            speaker = dialogue["speaker"]
            if speaker not in speakers:
                speakers.append(speaker)
        return speakers
    
    @staticmethod
    def get_word_count(dialogues: List[Dict[str, str]]) -> int:
        """Calculate total word count"""
        total_words = 0
        for dialogue in dialogues:
            total_words += len(dialogue["text"].split())
        return total_words
