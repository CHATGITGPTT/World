#!/usr/bin/env python3
"""
World Memory
Memory system for the World AI Agent System
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

class WorldMemory:
    """Memory system for World AI Agent System"""
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.memory_dir = self.base_path / "data" / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.memory_file = self.memory_dir / "world_memory.json"
        self.memories = self._load_memories()
        
    def _load_memories(self) -> Dict[str, Any]:
        """Load memories from file"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Return default memory structure
        return {
            "experiences": [],
            "knowledge": {},
            "patterns": {},
            "preferences": {},
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0",
                "total_experiences": 0
            }
        }
    
    async def store_experience(self, experience: Dict[str, Any]):
        """Store a new experience"""
        experience["timestamp"] = datetime.now().isoformat()
        experience["id"] = f"exp_{len(self.memories['experiences'])}"
        
        self.memories["experiences"].append(experience)
        self.memories["metadata"]["total_experiences"] = len(self.memories["experiences"])
        
        # Auto-refine memories periodically
        if len(self.memories["experiences"]) % 10 == 0:
            await self.refine()
        
        await self._save_memories()
    
    async def store_knowledge(self, topic: str, knowledge: Dict[str, Any]):
        """Store knowledge about a topic"""
        if topic not in self.memories["knowledge"]:
            self.memories["knowledge"][topic] = []
        
        knowledge["timestamp"] = datetime.now().isoformat()
        self.memories["knowledge"][topic].append(knowledge)
        
        await self._save_memories()
    
    async def get_knowledge(self, topic: str) -> List[Dict[str, Any]]:
        """Get knowledge about a topic"""
        return self.memories["knowledge"].get(topic, [])
    
    async def find_similar_experiences(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar experiences based on query"""
        # Simple keyword matching for now
        query_lower = query.lower()
        similar = []
        
        for exp in self.memories["experiences"]:
            if any(keyword in str(exp).lower() for keyword in query_lower.split()):
                similar.append(exp)
                if len(similar) >= limit:
                    break
        
        return similar
    
    async def refine(self):
        """Refine and optimize memories"""
        # Keep only recent experiences (last 1000)
        max_experiences = 1000
        if len(self.memories["experiences"]) > max_experiences:
            self.memories["experiences"] = self.memories["experiences"][-max_experiences:]
        
        # Extract patterns from experiences
        await self._extract_patterns()
        
        # Update metadata
        self.memories["metadata"]["last_refined"] = datetime.now().isoformat()
        self.memories["metadata"]["total_experiences"] = len(self.memories["experiences"])
        
        await self._save_memories()
    
    async def _extract_patterns(self):
        """Extract patterns from experiences"""
        patterns = {}
        
        for exp in self.memories["experiences"]:
            exp_type = exp.get("type", "general")
            if exp_type not in patterns:
                patterns[exp_type] = []
            
            # Extract key information
            pattern = {
                "type": exp_type,
                "timestamp": exp.get("timestamp"),
                "success": "error" not in exp
            }
            
            patterns[exp_type].append(pattern)
        
        self.memories["patterns"] = patterns
    
    async def _save_memories(self):
        """Save memories to file"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memories, f, indent=2)
        except IOError as e:
            print(f"Failed to save memories: {e}")
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "total_experiences": len(self.memories["experiences"]),
            "knowledge_topics": len(self.memories["knowledge"]),
            "patterns": len(self.memories["patterns"]),
            "last_refined": self.memories["metadata"].get("last_refined"),
            "created": self.memories["metadata"]["created"]
        }
    
    async def clear_memories(self):
        """Clear all memories"""
        self.memories = {
            "experiences": [],
            "knowledge": {},
            "patterns": {},
            "preferences": {},
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0",
                "total_experiences": 0
            }
        }
        await self._save_memories()
