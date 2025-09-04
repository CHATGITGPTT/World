import asyncio
import sys, pathlib

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from core.orchestrator import WorldOrchestrator


def test_enqueue_dequeue(monkeypatch):
    orch = WorldOrchestrator(config={})
    processed = []

    async def fake_process(task):
        processed.append(task["id"])

    monkeypatch.setattr(orch, "_process_task", fake_process)

    async def main():
        await orch.start()
        for i in range(3):
            await orch.execute_command({"id": i})
        await asyncio.sleep(0.05)
        await orch.stop()

    asyncio.run(main())
    assert processed == [0, 1, 2]
