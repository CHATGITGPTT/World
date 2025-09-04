import asyncio
import contextlib
from typing import Optional, Dict, Any


class WorldOrchestrator:
    """Simple orchestrator using an asyncio.Queue for task management."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tasks: asyncio.Queue = asyncio.Queue()
        self.running = False
        self._bg_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        self.running = True
        self._bg_task = asyncio.create_task(self._task_processing_loop())

    async def execute_command(self, task: Dict[str, Any]) -> None:
        await self.tasks.put(task)

    async def _process_task(self, task: Dict[str, Any]) -> None:  # pragma: no cover - to be patched in tests
        pass

    async def _task_processing_loop(self) -> None:
        while self.running:
            task = await self.tasks.get()
            try:
                await self._process_task(task)
            finally:
                self.tasks.task_done()

    async def stop(self) -> None:
        self.running = False
        if self._bg_task:
            with contextlib.suppress(asyncio.TimeoutError):
                await asyncio.wait_for(self.tasks.join(), timeout=1.0)
            self._bg_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._bg_task
