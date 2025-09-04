# app/main.py
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
import asyncio
import logging
from datetime import datetime
import uuid
import time
from collections import defaultdict

from .services.nlu_services import NLUService
from .services.conversation_service import ConversationService
from .services.knowledge_service import KnowledgeService
from .services.analytics_service import AnalyticsService
from .database import get_db
from . import config as app_config

# Configure logging
logging.basicConfig(level=getattr(logging, app_config.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Advanced AI Chatbot API",
    description="Production-ready chatbot with NLU, context management, and analytics",
    version="2.0.0"
)

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=app_config.ALLOWED_HOSTS)
if not app_config.ALLOWED_HOSTS:
    raise RuntimeError("ALLOWED_HOSTS cannot be empty.")

# CORS middleware with configurable origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Rate limiting storage
rate_limit_storage = defaultdict(list)

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old entries
    rate_limit_storage[client_ip] = [
        timestamp for timestamp in rate_limit_storage[client_ip]
        if current_time - timestamp < 3600  # 1 hour window
    ]
    
    # Check rate limits
    if len(rate_limit_storage[client_ip]) >= app_config.RATE_LIMIT_PER_HOUR:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    
    # Add current request
    rate_limit_storage[client_ip].append(current_time)
    
    response = await call_next(request)
    return response

# Initialize services
nlu_service = NLUService()
conversation_service = ConversationService()
knowledge_service = KnowledgeService()
analytics_service = AnalyticsService()

class ChatMessage(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    message: str
    timestamp: Optional[datetime] = None
    context: Optional[Dict[str, Any]] = None
    
    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        if len(v) > app_config.MAX_MESSAGE_LENGTH:
            raise ValueError(f'Message too long. Maximum length is {app_config.MAX_MESSAGE_LENGTH} characters')
        return v.strip()
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or not v.strip():
            raise ValueError('User ID cannot be empty')
        return v.strip()

class ChatResponse(BaseModel):
    session_id: str
    response: str
    intent: str
    intent_confidence: float
    entities: List[Dict[str, Any]]
    sentiment: str
    sentiment_score: float
    suggestions: Optional[List[str]] = None
    context: Dict[str, Any]
    response_time: float

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage, db=Depends(get_db)):
    start_time = datetime.now()
    
    try:
        # Generate session ID if not provided
        session_id = message.session_id or str(uuid.uuid4())
        
        # Process message through NLU pipeline
        nlu_result = await nlu_service.process_message(message.message)
        
        # Retrieve and update conversation context
        context = await conversation_service.get_context(session_id)
        updated_context = await conversation_service.update_context(
            session_id, message.message, nlu_result, context
        )
        
        # Generate response based on intent and context
        response = await conversation_service.generate_response(
            intent=nlu_result["intent"],
            entities=nlu_result["entities"],
            context=updated_context,
            user_message=message.message
        )
        
        # Get suggestions for follow-up
        suggestions = await conversation_service.get_suggestions(
            nlu_result["intent"], updated_context
        )
        
        # Log conversation for analytics if enabled
        if app_config.ANALYTICS_ENABLED:
            await analytics_service.log_interaction(
                user_id=message.user_id,
                session_id=session_id,
                message=message.message,
                response=response,
                nlu_result=nlu_result
            )
        
        # Calculate response time
        response_time = (datetime.now() - start_time).total_seconds()
        
        return ChatResponse(
            session_id=session_id,
            response=response,
            intent=nlu_result["intent"],
            intent_confidence=nlu_result["intent_confidence"],
            entities=nlu_result["entities"],
            sentiment=nlu_result["sentiment"],
            sentiment_score=nlu_result["sentiment_score"],
            suggestions=suggestions,
            context=updated_context,
            response_time=response_time
        )
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/analytics/dashboard")
async def get_analytics():
    """Get conversation analytics dashboard data"""
    if not app_config.ANALYTICS_ENABLED:
        raise HTTPException(status_code=503, detail="Analytics service is disabled")
    return await analytics_service.get_dashboard_data()

@app.post("/feedback")
async def submit_feedback(feedback: Dict[str, Any]):
    """Submit user feedback for continuous learning"""
    if not app_config.ANALYTICS_ENABLED:
        raise HTTPException(status_code=503, detail="Analytics service is disabled")
    await analytics_service.log_feedback(feedback)
    return {"status": "success"}

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now(),
        "version": "2.0.0",
        "services": {
            "nlu": "operational",
            "conversation": "operational",
            "analytics": "operational" if app_config.ANALYTICS_ENABLED else "disabled"
        }
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Advanced AI Chatbot API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }
