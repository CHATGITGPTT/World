# app/services/conversation_service.py
import redis
import json
from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime, timedelta
import hashlib

from ..utils.response_generator import ResponseGenerator
from .. import config

logger = logging.getLogger(__name__)

class ConversationService:
    def __init__(self):
        self.redis_client = None
        self.response_generator = ResponseGenerator()
        self.context_ttl = config.SESSION_TIMEOUT
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection with error handling"""
        try:
            self.redis_client = redis.Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                db=config.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            self.redis_client = None
    
    def _get_redis_client(self):
        """Get Redis client, reconnecting if necessary"""
        if self.redis_client is None:
            self._init_redis()
        return self.redis_client
    
    async def get_context(self, session_id: str) -> Dict[str, Any]:
        """Retrieve conversation context from Redis"""
        try:
            redis_client = self._get_redis_client()
            if redis_client is None:
                return self._initialize_context()
            
            context_key = f"context:{session_id}"
            context_data = redis_client.get(context_key)
            
            if context_data:
                return json.loads(context_data)
            else:
                return self._initialize_context()
                
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return self._initialize_context()
    
    async def update_context(self, session_id: str, message: str, 
                           nlu_result: Dict[str, Any], 
                           current_context: Dict[str, Any]) -> Dict[str, Any]:
        """Update conversation context with new information"""
        try:
            # Update message history
            current_context["messages"].append({
                "text": message,
                "timestamp": datetime.now().isoformat(),
                "intent": nlu_result["intent"],
                "entities": nlu_result["entities"],
                "sentiment": nlu_result["sentiment"],
                "sentiment_score": nlu_result["sentiment_score"]
            })
            
            # Keep only last 10 messages
            current_context["messages"] = current_context["messages"][-10:]
            
            # Update entities with deduplication
            for entity in nlu_result["entities"]:
                entity_key = entity["label"]
                if entity_key not in current_context["entities"]:
                    current_context["entities"][entity_key] = []
                if entity["text"] not in current_context["entities"][entity_key]:
                    current_context["entities"][entity_key].append(entity["text"])
            
            # Update conversation state
            current_context["current_intent"] = nlu_result["intent"]
            current_context["last_update"] = datetime.now().isoformat()
            current_context["message_count"] = len(current_context["messages"])
            
            # Track sentiment over time
            current_context["sentiment_history"].append({
                "sentiment": nlu_result["sentiment"],
                "score": nlu_result["sentiment_score"],
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep only last 5 sentiment records
            current_context["sentiment_history"] = current_context["sentiment_history"][-5:]
            
            # Calculate average sentiment
            if current_context["sentiment_history"]:
                avg_sentiment = sum(s["score"] for s in current_context["sentiment_history"]) / len(current_context["sentiment_history"])
                current_context["average_sentiment"] = avg_sentiment
            
            # Save to Redis
            redis_client = self._get_redis_client()
            if redis_client:
                context_key = f"context:{session_id}"
                redis_client.setex(
                    context_key, 
                    self.context_ttl, 
                    json.dumps(current_context)
                )
            
            return current_context
            
        except Exception as e:
            logger.error(f"Error updating context: {str(e)}")
            return current_context
    
    async def generate_response(self, intent: str, entities: List[Dict[str, Any]], 
                              context: Dict[str, Any], user_message: str) -> str:
        """Generate contextual response based on intent and conversation history"""
        try:
            return await self.response_generator.generate(
                intent=intent,
                entities=entities,
                context=context,
                user_message=user_message
            )
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."
    
    async def get_suggestions(self, intent: str, context: Dict[str, Any]) -> List[str]:
        """Get contextual suggestions for follow-up questions"""
        try:
            # Base suggestions by intent
            base_suggestions = {
                "greeting": [
                    "How can I help you today?",
                    "What would you like to know?",
                    "Tell me about your requirements"
                ],
                "product_inquiry": [
                    "Would you like to see more details?",
                    "Do you need pricing information?",
                    "Should I show you similar products?"
                ],
                "support": [
                    "Would you like me to escalate this?",
                    "Do you need additional assistance?",
                    "Can I help with anything else?"
                ],
                "question": [
                    "Does that answer your question?",
                    "Would you like me to clarify anything?",
                    "Is there something else you'd like to know?"
                ]
            }
            
            suggestions = base_suggestions.get(intent, [
                "How else can I help?",
                "Do you have other questions?",
                "Is there anything else I can assist with?"
            ])
            
            # Add contextual suggestions based on conversation history
            if context.get("message_count", 0) > 3:
                suggestions.append("Would you like me to summarize our conversation?")
            
            if context.get("average_sentiment", 0.5) < 0.3:
                suggestions.append("I notice you seem frustrated. Would you like me to escalate this?")
            
            return suggestions[:5]  # Limit to 5 suggestions
            
        except Exception as e:
            logger.error(f"Error getting suggestions: {str(e)}")
            return ["How else can I help?"]
    
    def _initialize_context(self) -> Dict[str, Any]:
        """Initialize new conversation context"""
        return {
            "session_start": datetime.now().isoformat(),
            "messages": [],
            "entities": {},
            "current_intent": None,
            "sentiment_history": [],
            "user_preferences": {},
            "conversation_stage": "initial",
            "last_update": datetime.now().isoformat(),
            "message_count": 0,
            "average_sentiment": 0.5
        }
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions (optional maintenance task)"""
        try:
            redis_client = self._get_redis_client()
            if redis_client is None:
                return 0
            
            # This is a simplified cleanup - in production you might want more sophisticated logic
            # For now, Redis TTL will handle expiration automatically
            return 0
            
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {str(e)}")
            return 0
