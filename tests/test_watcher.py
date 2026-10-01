import json
import tempfile
import time
import unittest
from pathlib import Path

from engine.runtime.events import RuntimeEventBus
from engine.runtime.watcher import EventStore, PollingWatcher, WorkspaceMutationWorker, is_high_signal_event
from engine.working_memory import WorkingMemory


class TestPollingWatcher(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name) / "workspace"
        self.workspace.mkdir()
        self.state_dir = Path(self.temp_dir.name) / "state"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initial_scan_is_silent_and_changes_are_coalesced(self):
        watcher = PollingWatcher([self.workspace], debounce_seconds=5)
        base = time.monotonic()
        self.assertEqual(watcher.poll(now=base), [])

        target = self.workspace / "notes.md"
        target.write_text("one", encoding="utf-8")
        watcher.poll(now=base + 1)
        target.write_text("two", encoding="utf-8")
        watcher.poll(now=base + 2)

        events = watcher.poll(now=base + 7)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].workspace, "workspace")
        self.assertEqual(events[0].files, ("notes.md",))
        self.assertEqual(events[0].kinds, ("modified",))

    def test_ignored_directories_and_suffixes(self):
        watcher = PollingWatcher([self.workspace], debounce_seconds=0)
        (self.workspace / ".git").mkdir()
        (self.workspace / ".git" / "ignored.txt").write_text("x", encoding="utf-8")
        (self.workspace / "cache.pyc").write_bytes(b"x")
        self.assertEqual(watcher.poll(now=0), [])

    def test_event_store_and_worker(self):
        watcher = PollingWatcher([self.workspace], debounce_seconds=0)
        memory = WorkingMemory(self.state_dir)
        memory.update_focus("Teste do watcher", project="workspace")
        worker = WorkspaceMutationWorker(watcher, EventStore(self.state_dir), memory)
        base = time.monotonic()
        worker.run_cycle(now=base)

        target = self.workspace / "source.py"
        target.write_text("print('ok')", encoding="utf-8")
        result = worker.run_cycle(now=base + 1)
        self.assertEqual(result["events_persisted"], 1)

        stored = list((self.state_dir / "events").glob("workspace_mutation_*.json"))
        self.assertEqual(len(stored), 1)
        payload = json.loads(stored[0].read_text(encoding="utf-8"))
        self.assertEqual(payload["files"], ["source.py"])
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(memory.focus, "Teste do watcher")
        self.assertEqual(memory.get_variable("last_workspace_mutation")["files"], ["source.py"])

    def test_high_signal_policy_is_explicit(self):
        watcher = PollingWatcher([self.workspace], debounce_seconds=0)
        alerts = []
        worker = WorkspaceMutationWorker(watcher, EventStore(self.state_dir), notifier=lambda title, message: alerts.append((title, message)))
        base = time.monotonic()
        worker.run_cycle(now=base)
        target = self.workspace / ".env.local"
        target.write_text("TOKEN=redacted", encoding="utf-8")
        result = worker.run_cycle(now=base + 1)
        self.assertEqual(result["high_signal_events"], 1)
        self.assertEqual(len(alerts), 1)
        self.assertTrue(is_high_signal_event(worker.last_events[0]))

    def test_worker_publishes_runtime_event(self):
        watcher = PollingWatcher([self.workspace], debounce_seconds=0)
        bus = RuntimeEventBus()
        subscriber = bus.subscribe()
        worker = WorkspaceMutationWorker(watcher, EventStore(self.state_dir), event_bus=bus)
        base = time.monotonic()
        worker.run_cycle(now=base)
        (self.workspace / "runtime.py").write_text("value = 1", encoding="utf-8")
        worker.run_cycle(now=base + 1)
        event = subscriber.get_nowait()
        self.assertEqual(event.event_type, "workspace_mutation")
        self.assertEqual(event.payload["files"], ("runtime.py",))
        self.assertIn("event: workspace_mutation", event.to_sse())
        bus.unsubscribe(subscriber)

    def test_worker_attaches_metadata_without_file_contents(self):
        watcher = PollingWatcher([self.workspace], debounce_seconds=0)
        worker = WorkspaceMutationWorker(watcher, EventStore(self.state_dir))
        base = time.monotonic()
        worker.run_cycle(now=base)
        (self.workspace / "module.py").write_text("print('safe')\n", encoding="utf-8")
        worker.run_cycle(now=base + 1)
        analysis = worker.last_events[0].analysis
        self.assertIn("source_code", analysis["risk_tags"])
        self.assertEqual(analysis["file_stats"][0]["lines"], 1)
        self.assertNotIn("print", str(analysis))


if __name__ == "__main__":
    unittest.main()
