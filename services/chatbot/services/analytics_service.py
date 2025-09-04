"""Analytics service for logging interactions and generating dashboard data."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func

from ..database import SessionLocal, Conversation, UserFeedback


class AnalyticsService:
    def __init__(self) -> None:
        pass

    async def log_interaction(
        self,
        user_id: str,
        session_id: str,
        message: str,
        response: str,
        nlu_result: Dict[str, Any],
    ) -> None:
        """Persist a single interaction to the database."""

        def _write() -> None:
            session = SessionLocal()
            try:
                rec = Conversation(
                    session_id=session_id,
                    user_id=user_id,
                    message=message,
                    response=response,
                    intent=nlu_result.get("intent"),
                    intent_confidence=float(nlu_result.get("intent_confidence") or nlu_result.get("confidence") or 0.0),
                    sentiment=nlu_result.get("sentiment"),
                    sentiment_score=float(nlu_result.get("sentiment_score") or nlu_result.get("score") or 0.0),
                    entities=nlu_result.get("entities", []),
                    timestamp=datetime.utcnow(),
                    response_time=None,
                )
                session.add(rec)
                session.commit()
            finally:
                session.close()

        await asyncio.to_thread(_write)

    async def log_feedback(self, feedback: Dict[str, Any]) -> None:
        """Persist user feedback to the database."""

        def _write() -> None:
            session = SessionLocal()
            try:
                rec = UserFeedback(
                    session_id=feedback.get("session_id"),
                    user_id=feedback.get("user_id"),
                    rating=feedback.get("rating"),
                    feedback_text=feedback.get("feedback_text"),
                    timestamp=datetime.utcnow(),
                )
                session.add(rec)
                session.commit()
            finally:
                session.close()

        await asyncio.to_thread(_write)

    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Return basic analytics suitable for a dashboard."""

        def _read() -> Dict[str, Any]:
            session = SessionLocal()
            try:
                total_messages = session.query(func.count(Conversation.id)).scalar() or 0

                avg_response_time = (
                    session.query(func.avg(Conversation.response_time))
                    .scalar()
                )
                avg_response_time = float(avg_response_time) if avg_response_time is not None else 0.0

                # Intent distribution
                intent_rows = (
                    session.query(Conversation.intent, func.count(Conversation.id))
                    .group_by(Conversation.intent)
                    .all()
                )
                intents = {intent or "unknown": int(count) for intent, count in intent_rows}

                # Sentiment distribution
                sentiment_rows = (
                    session.query(Conversation.sentiment, func.count(Conversation.id))
                    .group_by(Conversation.sentiment)
                    .all()
                )
                sentiments = {sent or "unknown": int(count) for sent, count in sentiment_rows}

                # Recent activity (last 24h)
                since = datetime.utcnow() - timedelta(hours=24)
                last_24h_count = (
                    session.query(func.count(Conversation.id))
                    .filter(Conversation.timestamp >= since)
                    .scalar()
                    or 0
                )

                return {
                    "total_messages": int(total_messages),
                    "avg_response_time": avg_response_time,
                    "intents": intents,
                    "sentiments": sentiments,
                    "last_24h_messages": int(last_24h_count),
                    "generated_at": datetime.utcnow().isoformat() + "Z",
                }
            finally:
                session.close()

        return await asyncio.to_thread(_read)

