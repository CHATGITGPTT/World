# app/utils/response_generator.py
import random
from typing import Dict, List, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

class ResponseGenerator:
    def __init__(self):
        self.response_templates = self._load_response_templates()
        self.dynamic_responses = self._load_dynamic_responses()
    
    async def generate(self, intent: str, entities: List[Dict[str, Any]], 
                      context: Dict[str, Any], user_message: str) -> str:
        """Generate contextual response"""
        try:
            # Check for dynamic response patterns first
            dynamic_response = await self._generate_dynamic_response(
                intent, entities, context, user_message
            )
            
            if dynamic_response:
                return dynamic_response
            
            # Fall back to template-based responses
            return self._generate_template_response(intent, entities, context)
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble understanding. Could you please rephrase that?"
    
    async def _generate_dynamic_response(self, intent: str, entities: List[Dict[str, Any]], 
                                       context: Dict[str, Any], user_message: str) -> str:
        """Generate dynamic responses based on context and entities"""
        
        # Handle specific patterns
        if intent == "greeting":
            time_of_day = self._get_time_of_day()
            return f"Good {time_of_day}! I'm here to help you. What can I assist you with today?"
        
        elif intent == "product_inquiry":
            product_entities = [e for e in entities if e["label"] in ["PRODUCT", "ORG"]]
            if product_entities:
                product = product_entities[0]["text"]
                return f"I'd be happy to help you learn more about {product}. What specific information are you looking for?"
        
        elif intent == "complaint":
            sentiment_history = context.get("sentiment_history", [])
            if len(sentiment_history) > 1 and all(s["sentiment"] == "negative" for s in sentiment_history[-2:]):
                return "I understand you're frustrated, and I sincerely apologize for the inconvenience. Let me escalate this to ensure we resolve your concerns properly."
        
        return None
    
    def _generate_template_response(self, intent: str, entities: List[Dict[str, Any]], 
                                   context: Dict[str, Any]) -> str:
        """Generate template-based response"""
        templates = self.response_templates.get(intent, self.response_templates["default"])
        template = random.choice(templates)
        
        # Simple entity substitution
        response = template
        for entity in entities:
            if entity["label"] == "PERSON":
                response = response.replace("{person}", entity["text"])
            elif entity["label"] == "ORG":
                response = response.replace("{organization}", entity["text"])
        
        return response
    
    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Load response templates for different intents"""
        return {
            "greeting": [
                "Hello! How can I assist you today?",
                "Hi there! What can I help you with?",
                "Welcome! I'm here to help. What do you need?"
            ],
            "goodbye": [
                "Goodbye! Have a wonderful day!",
                "Thank you for chatting with me. Take care!",
                "It was great helping you today. See you soon!"
            ],
            "question": [
                "That's a great question! Let me help you with that.",
                "I'd be happy to answer that for you.",
                "Let me provide you with the information you need."
            ],
            "complaint": [
                "I understand your concern and I'm here to help resolve this.",
                "I apologize for any inconvenience. Let me see how I can assist you.",
                "Thank you for bringing this to my attention. I'll help you sort this out."
            ],
            "compliment": [
                "Thank you so much! I'm glad I could help.",
                "That's very kind of you to say!",
                "I appreciate your feedback. It means a lot!"
            ],
            "default": [
                "I'm here to help! Could you please provide more details?",
                "I want to make sure I understand correctly. Can you elaborate?",
                "Let me assist you with that. Could you be more specific?"
            ]
        }
    
    def _load_dynamic_responses(self) -> Dict[str, Any]:
        """Load dynamic response patterns"""
        return {
            "context_aware": True,
            "personalization": True,
            "entity_aware": True
        }
    
    def _get_time_of_day(self) -> str:
        """Get appropriate greeting based on time of day"""
        from datetime import datetime
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 22:
            return "evening"
        else:
            return "evening"
