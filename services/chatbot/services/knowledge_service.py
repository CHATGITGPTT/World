"""Knowledge service stub for future RAG/FAQ integrations."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class KnowledgeService:
    def __init__(self) -> None:
        # Placeholder: in a real system, initialize vector DB / retriever here
        self.enabled = False

    async def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search a knowledge base. Returns empty until implemented."""
        return []

    async def get_answer(self, query: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Get an answer if available. Returns None until implemented."""
        return None

