# nlp_processing.py
import spacy
from transformers import pipeline
import logging
import subprocess
import sys
import logging

logger = logging.getLogger(__name__)

class NLPProcessor:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
        
        self.intent_classifier = pipeline("text-classification", model="facebook/bart-large-mnli")

    def process_command(self, command):
        """Process and interpret the voice command."""
        doc = self.nlp(command)
        
        entities = {
            'verbs': [token.lemma_ for token in doc if token.pos_ == 'VERB'],
            'nouns': [token.lemma_ for token in doc if token.pos_ == 'NOUN'],
            'names': [ent.text for ent in doc.ents if ent.label_ == 'PERSON'],
            'dates': [ent.text for ent in doc.ents if ent.label_ == 'DATE'],
            'amounts': [ent.text for ent in doc.ents if ent.label_ == 'MONEY']
        }
        
        try:
            intent = self.intent_classifier(command)[0]
            return {
                'raw_command': command,
                'intent': intent['label'],
                'confidence': intent['score'],
                'entities': entities
            }
        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            return {
                'raw_command': command,
                'intent': 'unknown',
                'confidence': 0.0,
                'entities': entities
            }