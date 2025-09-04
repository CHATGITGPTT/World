# app/services/nlu_service.py
import asyncio
import logging
from typing import Any, Dict, List

import spacy
from transformers import pipeline

from .. import config

logger = logging.getLogger(__name__)


class NLUService:
    def __init__(self):
        # Load spaCy model for NER (fallback to blank model if unavailable)
        try:
            self.nlp = spacy.load(config.SPACY_MODEL)
        except Exception as e:
            logger.warning(f"Failed to load spaCy model '{config.SPACY_MODEL}': {e}. Falling back to blank 'en'.")
            self.nlp = spacy.blank("en")
        
        # Load pre-trained models (with graceful fallbacks)
        self.intent_classifier = None
        self.sentiment_analyzer = None
        try:
            self.intent_classifier = pipeline(
                "zero-shot-classification",
                model=config.INTENT_MODEL,
            )
        except Exception as e:
            logger.warning(f"Failed to initialize intent classifier '{config.INTENT_MODEL}': {e}. Using fallback.")
        
        try:
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model=config.SENTIMENT_MODEL,
            )
        except Exception as e:
            logger.warning(f"Failed to initialize sentiment analyzer '{config.SENTIMENT_MODEL}': {e}. Using fallback.")
        
        # Custom intent labels - expand based on your domain
        self.intent_labels = [
            "greeting",
            "goodbye",
            "question",
            "request_info",
            "complaint",
            "compliment",
            "booking",
            "cancel",
            "support",
            "product_inquiry",
            "pricing",
            "technical_issue",
        ]
        
    async def process_message(self, text: str) -> Dict[str, Any]:
        """Process message through complete NLU pipeline"""
        try:
            # Run NLU tasks concurrently
            tasks = [
                self._extract_entities(text),
                self._classify_intent(text),
                self._analyze_sentiment(text),
                self._extract_keywords(text)
            ]
            
            entities, intent_result, sentiment_result, keywords = await asyncio.gather(*tasks)
            
            return {
                "entities": entities,
                "intent": intent_result["intent"],
                "intent_confidence": intent_result["confidence"],
                "sentiment": sentiment_result["sentiment"],
                "sentiment_score": sentiment_result["score"],
                "keywords": keywords,
                "processed_text": text.lower().strip()
            }
            
        except Exception as e:
            logger.error(f"Error in NLU processing: {str(e)}")
            return self._get_default_result(text)
    
    async def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities using spaCy"""
        doc = await asyncio.to_thread(self.nlp, text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "confidence": 1.0  # spaCy doesn't provide confidence scores
            })
            
        return entities
    
    async def _classify_intent(self, text: str) -> Dict[str, Any]:
        """Classify user intent using zero-shot classification"""
        if self.intent_classifier is None:
            # Simple fallback heuristic
            default_intent = "greeting" if any(w in text.lower() for w in ["hi", "hello", "hey"]) else "question"
            return {"intent": default_intent, "confidence": 0.5, "all_scores": {default_intent: 0.5}}

        result = await asyncio.to_thread(self.intent_classifier, text, self.intent_labels)

        return {
            "intent": result["labels"][0],
            "confidence": result["scores"][0],
            "all_scores": dict(zip(result["labels"], result["scores"]))
        }
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of the message"""
        if self.sentiment_analyzer is None:
            # Fallback neutral sentiment
            return {"sentiment": "neutral", "score": 0.5}

        result = (await asyncio.to_thread(self.sentiment_analyzer, text))[0]
        
        # Map model output to standardized labels
        sentiment_mapping = {
            "LABEL_0": "negative",
            "LABEL_1": "neutral", 
            "LABEL_2": "positive"
        }
        
        sentiment = sentiment_mapping.get(result["label"], result["label"].lower())
        
        return {
            "sentiment": sentiment,
            "score": result["score"]
        }
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        doc = await asyncio.to_thread(self.nlp, text)
        keywords = []
        
        for token in doc:
            if (token.pos_ in ["NOUN", "VERB", "ADJ"] and 
                not token.is_stop and not token.is_punct and 
                len(token.text) > 2):
                keywords.append(token.lemma_.lower())
                
        return list(set(keywords))
    
    def _get_default_result(self, text: str) -> Dict[str, Any]:
        """Return default result when NLU processing fails"""
        return {
            "entities": [],
            "intent": "unknown",
            "intent_confidence": 0.0,
            "sentiment": "neutral",
            "sentiment_score": 0.5,
            "keywords": [],
            "processed_text": text.lower().strip()
        }
